import json
from langchain_openai import ChatOpenAI,AzureChatOpenAI
from langchain.schema import SystemMessage
import os

# Function to generate subtopics
# def generate_subtopics(topic, openai_api_key):
#     chat = ChatOpenAI(
#         openai_api_key=openai_api_key,
#         model='gpt-3.5-turbo',
#         temperature=0,
#         max_tokens=None,
#         timeout=None
#     )
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
            return a ***LIST*** format of the subtopics'''
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
            Here is the subtopic_list : {subtopics_list}. Write an explanation and 2 engaging MCQs on each subtopic in a **JSON** format which will be used as a lesson plan later with the keys being topic, explanation, engaging_questions. Engaging questions will just have the keys - question and the options.'''
      ))
    ]
    
    res = chat(messages)
    return json.loads(res.content)['subtopics']
