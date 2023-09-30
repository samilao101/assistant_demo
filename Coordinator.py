import streamlit as st
import os
import openai
from dotenv import load_dotenv
import io
from database import database_manager as db_manager
from forms_templates import prompt_generator
from streamlit_javascript import st_javascript
base_url = st_javascript("await fetch('').then(r => window.parent.location.href)", key="secret")

if os.path.exists('certificate\certificate.crt'):
    os.environ['REQUESTS_CA_BUNDLE'] = 'certificate\certificate.crt'
else:
    print("Certificate file does not exist or is inaccessible.")

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def convert_spaces_to_underscores(input_string):
    # Replace white spaces with underscores using the str.replace method
    result_string = input_string.replace(" ", "_")
    return result_string

def sidebar():
    st.sidebar.header("FAQ Form:") 
    question = st.sidebar.text_area(  # Moved to sidebar
        "Please type below what you would like to learn more about and I will try to find the process for you to ask your questions. ", placeholder="Enter question...")

    formatted_response = ""


    if st.sidebar.button("Search") and question != "":  
        loading_message = st.sidebar.empty()  # Create an empty slot in the sidebar.
        loading_message.text("Generating response...")  # Display loading message in the sidebar.

        prompt_question = prompt_generator.generate_coordinator_prompt(question)
        generated_response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[
                {"role": "user", "content": prompt_question}
            ],
            temperature=0.0
        )
        
        formatted_response = generated_response['choices'][0]['message']['content']
        loading_message.text("")  # Clear the loading message or replace it with the completed message.

            

    if formatted_response != "":
        st.sidebar.markdown(formatted_response)  # Moved to sidebar
    else:
        st.sidebar.markdown(f"")  # Moved to sidebar

sidebar()
st.image("cumminslogo.png")  # Moved to sidebar
st.header("Process FAQ Bots")

all_bots = db_manager.get_all_bots()

st.text_input("Enter process name...")

num_columns = 3
cols = st.columns(num_columns)

for i in range(0, len(all_bots), num_columns):
    for j in range(num_columns):
        idx = i + j
        bot_id, bot_name, bot_purpose, bot_file_name = all_bots[idx]
        if idx < len(all_bots):
            cols[j].markdown(f"[{bot_name}]({base_url}{convert_spaces_to_underscores(bot_name)})")