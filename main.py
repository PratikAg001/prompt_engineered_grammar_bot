import streamlit as st
import json
import os
from lesson_plan_generator import generate_subtopics, generate_lesson_plan
from lesson_chatbot import LessonChatbot, initialize_chat_openai

st.set_page_config(page_title="Lesson Chatbot", page_icon=":robot:")

# Streamlit UI
st.title("AI English Lesson Plan Generator & Interactive Chatbot")

# Get API key and endpoint
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "api_endpoint" not in st.session_state:
    st.session_state.api_endpoint = ""

if not st.session_state.api_key:
    st.session_state.api_key = st.text_input("Please enter your AzureOpenAI API key to start:", type="password")
if st.session_state.api_key and not st.session_state.api_endpoint:
    st.session_state.api_endpoint = st.text_input("Please enter your AzureOpenAI API endpoint to start:")

if st.session_state.api_key and st.session_state.api_endpoint:
    # Dropdown for main topic
    topic = st.selectbox("Choose the main topic", ["Noun", "Adjective", "Preposition", "Tense", "Composition"])

    # Generate subtopics and lesson plan only if they are not already generated
    if 'subtopics' not in st.session_state:
        st.session_state.subtopics = []

    if 'lesson_plan' not in st.session_state:
        st.session_state.lesson_plan = []

    if st.button("Generate Lesson Plan"):
        st.session_state.subtopics = generate_subtopics(topic, st.session_state.api_key, st.session_state.api_endpoint)
        st.write("Generated Subtopics:")
        st.write(st.session_state.subtopics)
        
        st.session_state.lesson_plan = generate_lesson_plan(st.session_state.subtopics, st.session_state.api_key, st.session_state.api_endpoint)
        
        # Save lesson plan to JSON file
        with open('lesson_plan.json', 'w') as f:
            json.dump(st.session_state.lesson_plan, f, indent=4)
        
        st.write("Lesson Plan Generated and Saved to 'lesson_plan.json'")
        st.write(st.session_state.lesson_plan)

        # Reset the chatbot to use the new lesson plan
        if 'chatbot' in st.session_state:
            del st.session_state.chatbot

    # Check if lesson plan exists
    lesson_plan_exists = os.path.isfile('lesson_plan.json')

    if lesson_plan_exists:
        # Load the lesson plan JSON
        with open('lesson_plan.json', 'r') as f:
            plan_json = json.load(f)

        if "chat" not in st.session_state:
            st.session_state.chat = initialize_chat_openai(st.session_state.api_key, st.session_state.api_endpoint)
            st.rerun()

        if "chat" in st.session_state and "chatbot" not in st.session_state:
            st.session_state.chatbot = LessonChatbot(plan_json, st.session_state.chat)

        if "chatbot" in st.session_state:
            chatbot = st.session_state.chatbot

            if "current_topic_index" not in st.session_state:
                st.session_state.current_topic_index = 0
            if "current_question_index" not in st.session_state:
                st.session_state.current_question_index = 0
            if "incorrect_attempts" not in st.session_state:
                st.session_state.incorrect_attempts = 0
            if "user_inputs" not in st.session_state:
                st.session_state.user_inputs = []
            if "hints" not in st.session_state:
                st.session_state.hints = []
            if "show_hint" not in st.session_state:
                st.session_state.show_hint = False
            if "current_input" not in st.session_state:
                st.session_state.current_input = ""
            if "explanation" not in st.session_state:
                st.session_state.explanation = chatbot.explain_topic()

            def next_question():
                st.session_state.current_question_index += 1
                st.session_state.incorrect_attempts = 0
                st.session_state.show_hint = False
                st.session_state.hints = []
                st.session_state.current_input = ""
                if st.session_state.current_question_index >= len(chatbot.get_current_topic()["engaging_questions"]):
                    st.session_state.current_question_index = 0
                    st.session_state.current_topic_index += 1
                    if st.session_state.current_topic_index >= len(plan_json):
                        st.session_state.current_topic_index = 0
                        st.success("End of lesson plan. Good job!")
                        st.stop()
                chatbot.current_topic_index = st.session_state.current_topic_index
                chatbot.current_question_index = st.session_state.current_question_index
                st.session_state.explanation = chatbot.explain_topic()
                st.rerun()

            # Display explanation
            st.write(f"**Topic: {chatbot.get_current_topic()['topic']}**")
            st.write("Explanation:", st.session_state.explanation)

            # Display question
            question = chatbot.ask_question()
            st.write("Question:", question)

            user_input = st.text_input("Your answer (or type 'exit' to quit): ", key="user_input")

            if st.button("Submit Answer"):
                if user_input:
                    st.session_state.current_input = user_input
                    if user_input.lower() == "exit":
                        st.write("Exiting the lesson. Goodbye!")
                        st.stop()

                    st.session_state.user_inputs.append(user_input)
                    evaluation = chatbot.evaluate_answer(user_input)
                    st.write("Evaluation:", evaluation)

                    if evaluation == "NO":
                        st.session_state.incorrect_attempts += 1
                        if st.session_state.incorrect_attempts >= 2:
                            st.write("Incorrect twice. Moving to the next question.")
                            hint = chatbot.give_hint_or_respond(user_input, st.session_state.incorrect_attempts)
                            st.session_state.hints.append(hint)
                            st.write("Hint or Response:", hint)
                            next_question()
                        else:
                            hint = chatbot.give_hint_or_respond(user_input)
                            st.session_state.hints.append(hint)
                            st.write("Hint or Response:", hint)
                    else:
                        st.session_state.incorrect_attempts = 0
                        st.write("Correct! Moving to the next question.")
                        next_question()

st.write("[DEBUG] Main execution complete.")
