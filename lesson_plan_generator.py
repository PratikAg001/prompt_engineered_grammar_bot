import json
from langchain_openai import AzureChatOpenAI
from langchain.schema import SystemMessage
import os

def generate_subtopics(topic,api_key, api_endpoint):
    os.environ["AZURE_OPENAI_API_KEY"] = api_key
    os.environ["AZURE_OPENAI_ENDPOINT"] = api_endpoint
    chat=AzureChatOpenAI(
        azure_deployment="azureopenaijapangrammarcorrection",
        api_version="2023-12-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None
    )
    
    messages = [
        SystemMessage(content=(
            f'''You are Sivi, an AI English Professor. Your task is to create subtopics on the topic {topic}
            return a ***LIST*** format of the subtopics
            -Maximum should be 10 topics.
            -You can combine 2 topics in one item if needed.
            -Only give important and relevant topics'''
        ))
    ]
    
    res = chat(messages)
    subtopics_list = [line.strip('- ').strip() for line in res.content.strip().split('\n') if line.strip()]
    return subtopics_list

# Function to generate lesson plan
def generate_lesson_plan(subtopics_list, api_key,api_endpoint):
    os.environ["AZURE_OPENAI_API_KEY"] = api_key
    os.environ["AZURE_OPENAI_ENDPOINT"] = api_endpoint
    chat=AzureChatOpenAI(
        azure_deployment="azureopenaijapangrammarcorrection",
        api_version="2023-12-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None
    )
    
    messages = [
      SystemMessage(content=(
          f'''Generate a JSON object. The main key will be "subtopics".
            - Do NOT include triple backticks or any other formatting characters in the output.
            Here is the subtopic_list : {subtopics_list}. Write an explanation and 2 engaging MCQs on each subtopic in a **JSON** format which will be used as a lesson plan later with the keys being topic, explanation, engaging_questions. Engaging questions will just have the keys - question and the options.
            -The response should be a *JSON* object '''
      ))  
    ]
    
    res = chat(messages)
    print(res.content)
    return json.loads(res.content)['subtopics']
