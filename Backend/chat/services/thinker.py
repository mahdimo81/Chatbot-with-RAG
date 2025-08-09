from openai import OpenAI
import datetime
from django.apps import apps
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

class ChatThinker:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="",
        )
        
    def analyze_message(self, user_message):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        storage_prompt = f"""
        Without including any explanations analyze this message and extract any factual information that should be stored in memory.
        If there is information to store, write these details as simple sentences separated by a single space.
        If not, respond with 'NO_DATA'. Do not include any explanations.
        For example if user wrote their name and their job in message, you should write:
        The user name is ...
        The user job is ....
        or the user hates ... 
        or the user likes ...
        If the user mentions that they did something, write it down along with the date of the action and information which their describe the action with.
        Seprate the informatios with '|'
        
        For example: 
        My father's name is Steve and we always play football and we enjoy alot
        >>> The user's father's name is Steve | The user always plays football with his father and they enjoys alot
        
        or i'm playing guitar now
        >>> The user played guitar on date ... 

        Avoid writing long texts and programmeing codes as information.
        date of this message is: [{date}]
        Message: [{user_message}]
        """

        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": storage_prompt}],
        )
        extracted_data = completion.choices[0].message.content if completion.choices[0].message.content != 'NO_DATA' else None

        retrieval_prompt = f"""
        Without including any explanations analyze this message and determine if it requires retrieving factual information from memory.
        If yes, identify the key concepts to search for and write them as simple terms separated by a |.
        If not, respond with 'NO_DATA'. Do not include any explanations.
        
        Message: {user_message}
        """

        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": retrieval_prompt}],
        )
        retrieval_response = completion.choices[0].message.content if completion.choices[0].message.content != 'NO_DATA' else None

        return extracted_data, retrieval_response
    
    def compare(self, old_information, new_informations):
        compare_prompt = f"""
        Without including any explanations, Compare these informations.
        With preserving the structure of new information (seprating with |), only remove the repetitive informations.
        Write new, non-duplicate information in the output without additional explanation.
        If all new information are in old informations, respond with 'NO_DATA'. Do not include any explanations.
        informations in memory: 
        {old_information}

        new informations:
        {new_informations}
        """
        
        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": compare_prompt}],
        )
        response = completion.choices[0].message.content if completion.choices[0].message.content != "NO_DATA" else None
        
        return response
    
    def store_information(self, user_id, extracted_data):
        if extracted_data:
            
            apps.get_app_config('chat').collection.load()
            old_information = ""
            
            for text in map(str.strip, extracted_data.split("|")):
                if not text:
                    continue

                search_embedding = model.encode([text])[0].tolist()
                search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

                results = apps.get_app_config('chat').collection.search(
                    data=[search_embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=5,
                    output_fields=["user_id", "content"],
                    expr=f"user_id == {user_id}"
                )

                if results:
                    for hits in results:
                        for hit in hits:
                            content = hit.entity.get('content', '')
                            if content:
                                old_information += content + " | "
                                
            old_information = old_information.rstrip(" | ")
            information_to_save = self.compare(old_information, extracted_data)

            if information_to_save:
                texts = [text.strip() for text in information_to_save.split("|") if text.strip()]
                documents = []
                for text in texts:
                    documents.append({'user_id': user_id, 'content': text})

                embeddings = model.encode([doc["content"] for doc in documents])
                data = [
                    [doc["user_id"] for doc in documents],
                    [doc["content"] for doc in documents],
                    embeddings.tolist()
                ]
                insert_result = apps.get_app_config('chat').collection.insert(data)
                print("New information inserted.")
                
            return information_to_save

        else:
            return None
    def retrieve_information(self, user_id, retrieval_terms):
        if not retrieval_terms:
            return None
            
        information = ""
        for text in map(str.strip, retrieval_terms.split("|")):
            if not text:
                continue

            search_embedding = model.encode([text])[0].tolist()
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

            results = apps.get_app_config('chat').collection.search(
                data=[search_embedding],
                anns_field="embedding",
                param=search_params,
                limit=5,
                output_fields=["user_id", "content"],
                expr=f"user_id == {user_id}"
            )

            if results:
                for hits in results:
                    for hit in hits:
                        content = hit.entity.get('content', '')
                        if content:
                            information += content + " | "

        return information.rstrip(" | ") if information else None

    def process_message(self, user_id, user_message):
        # Analyze message for storage and retrieval
        extracted_data, retrieval_terms = self.analyze_message(user_message)

        # Store new information
        self.store_information(user_id, extracted_data)
        
        # Retrieve relevant information
        retrieved_data = self.retrieve_information(user_id, retrieval_terms)
        
        # Generate response
        return self.generate_response(user_message, retrieved_data)

    def generate_response(self, user_message, retrieved_data=None):
        if retrieved_data:
            prompt = f"""
            Context from memory: {retrieved_data}
            
            User question: {user_message}
            
            Please answer the user's question using the provided context when relevant.
            """
        else:
            prompt = user_message

        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content