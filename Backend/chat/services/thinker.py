from hmac import new
from openai import OpenAI
import datetime
from django.apps import apps
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

class ChatThinker:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )
        
    def create_title(self, user_message):
        title_prompt = f"""
        Without including any explanations, create a title for the following message.
        The title should be a single sentence that captures the main idea of the message less than 10 words.
        The title should be in the english language.
        Message: {user_message}
        """
        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": title_prompt}],
        )
        title_response = completion.choices[0].message.content
        return title_response

    def analyze_message(self, user_message):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        extract_prompt = f"""
        STRICT INFORMATION EXTRACTION RULES:
        1. Extract ONLY factual, personal, or descriptive information worth storing long-term.
        2. Format each fact as a simple, standalone sentence in the 3rd person (e.g., "The user's name is...").
        3. If NO valuable information is found, respond EXACTLY with: 'NO_DATA'.
        4. NEVER include explanations, notes, or variations—ONLY the extracted facts.
        5. SEPARATE multiple facts with a single '|' (no spaces around it).
        6. If the user mentions an action (past/present), include the date ONLY if it’s explicitly stated or implied (e.g., "yesterday" → use [{date} - 1 day]).
        7. NEVER add standalone dates (e.g., avoid "The user sent a message on...") unless the date is PART of the fact (e.g., "The user played football on 2025-08-12").
        8. Keep sentences SHORT and avoid fluff (e.g., "we enjoy a lot" → remove unless critical).
        9. If the message contains code, commands, or non-storable data → 'NO_DATA'.

        EXAMPLES:
        Message: "My name is Mahdi Momeni and I played football yesterday."
        Output: "The user's name is Mahdi Momeni | The user played football on {date}"

        Message: "I love pizza and my cat is named Whiskers."
        Output: "The user loves pizza | The user's cat is named Whiskers"

        Message: "print('hello world')"
        Output: "NO_DATA"

        Message: "I'm 30 years old."
        Output: "The user is 30 years old"

        Current date: [{date}]
        Message: [{user_message}]
        """

        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": extract_prompt}],
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
        
    def compare(self, old_information, new_information):
        compare_prompt = f"""
        STRICT COMPARISON INSTRUCTIONS:
        1. Analyze the new information piece by piece (separated by |)
        2. For each piece in new information, check if it is COMPLETELY CONTAINED within old information
        3. If ALL pieces from new information exist in old information, respond EXACTLY with: NO_DATA
        4. If ANY piece is new, include ONLY the new pieces in the output
        5. Preserve the original formatting and structure (| separation)
        6. DO NOT include any explanations, commentary, or variations
        7. Consider two pieces identical if their core meaning is the same, even if wording differs slightly
        
        EXAMPLES:
        Information in memory: The user's name is John | The user is 30 years old
        NEW: The user's name is John
        RESPONSE: NO_DATA
        
        Information in memory: The user likes apples
        NEW: The user likes apples | The user likes oranges
        RESPONSE: The user likes oranges
        ---------------------------------------------------
        Information in memory: 
        {old_information}

        New information:
        {new_information}
        """
        print("old info:", old_information)
        print("new info:", new_information)
        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": compare_prompt}],
            temperature=0.0  # Add this for more deterministic responses
        )
        response = completion.choices[0].message.content if completion.choices[0].message.content != "NO_DATA" else None
        print("Response:", response)
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
                    limit=3,
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
                limit=3,
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
