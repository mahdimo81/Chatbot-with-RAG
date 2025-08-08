import requests
from openai import OpenAI
import datetime

class ChatThinker:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )
        
    def analyze_message(self, user_message):
        # Step 1: Check if message contains information to store
        
        date = datetime.datetime.now()
        date = str(date).split(" ")[0]
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
        

        # Step 2: Check if message requires information retrieval
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
        response = completion.choices[0].message.content

        return response