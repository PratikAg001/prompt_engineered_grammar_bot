import json
from langchain_openai import AzureChatOpenAI
from langchain.schema import SystemMessage
import os
class LessonChatbot:
    def __init__(self, plan_json, chat):
        self.plan_json = plan_json
        self.current_topic_index = 0
        self.current_question_index = 0
        self.incorrect_attempts = 0
        self.conversation_gpt = chat
        self.evaluation_gpt = chat
        self.hint_gpt = chat

    def get_current_topic(self):
        return self.plan_json[self.current_topic_index]

    def next_question(self):
        self.current_question_index += 1
        self.incorrect_attempts = 0
        if self.current_question_index >= len(self.get_current_topic()["engaging_questions"]):
            self.current_question_index = 0
            self.current_topic_index += 1
            if self.current_topic_index >= len(self.plan_json):
                return "end"
        return self.get_current_topic()["engaging_questions"][self.current_question_index]

    def explain_topic(self):
        current_topic = self.get_current_topic()
        prompt = f"You are an English teacher. Explain the topic '{current_topic['topic']}' with the explanation: {current_topic['explanation']}."
        messages = [SystemMessage(content=prompt)]
        explanation_response = self.conversation_gpt(messages)
        return explanation_response.content

    def ask_question(self):
        current_topic = self.get_current_topic()
        current_question = self.get_current_topic()["engaging_questions"][self.current_question_index]
        question_text = f"{current_question['question']} {current_question['options']}"
        return question_text

    def evaluate_answer(self, user_input):
        current_topic = self.get_current_topic()
        current_question = self.get_current_topic()["engaging_questions"][self.current_question_index]
        question_text = f"{current_question['question']} {current_question['options']}"
        prompt = f'''You are a professor that evaluates whether a student's answer to a teacher's question contains factually incorrect information. You do not count typos as incorrect information. Fully irrelevant responses are counted as incorrect.

        The student's answer and the teacher's question are provided below:

        Teacher Question: {question_text}

        Student Answer: {user_input}

        Use the following format:
        YES or NO
        '''
        messages = [SystemMessage(content=prompt)]
        evaluation_response = self.evaluation_gpt(messages)
        return evaluation_response.content.strip()

    def give_hint_or_respond(self, user_input,incorrect_attempts=0):
        current_topic = self.get_current_topic()
        current_question = self.get_current_topic()["engaging_questions"][self.current_question_index]
        question_text = f"{current_question['question']} {current_question['options']}"
        prompt = f'''You are an AI English Teacher. Your job is to provide a hint to the student if they give a wrong answer or answer their query if it is in the input text.
        -If the incorrect_attempts : {incorrect_attempts} is greater than or equal to 2; Reveal the final answer from the options from the {question_text}.
        -Never ask question back,your job is to provide hints.
        -Never say, "This is not the correct answer, choose a correct one.";You have to provide a hint,you may say why that answer was wrong and an hint about the correct answer.
        -If the answer user gave is not from the options from the {question_text}, then evaluate it wrong as NO.

        Teacher Question: {question_text}

        Student Answer: {user_input}

        If the Student Answer was wrong, give a hint. If the Student Answer is another query or something, respond accordingly.
        '''
        messages = [SystemMessage(content=prompt)]
        hint_response = self.hint_gpt(messages)
        return hint_response.content

# Function to initialize ChatOpenAI with the provided API key
def initialize_chat_openai(api_key, api_endpoint):
    os.environ["AZURE_OPENAI_API_KEY"] = api_key
    os.environ["AZURE_OPENAI_ENDPOINT"] = api_endpoint
    return AzureChatOpenAI(
        azure_deployment="azureopenaijapangrammarcorrection",
        api_version="2023-12-01-preview",
        temperature=0,
        max_tokens=None,
        timeout=None
    )
