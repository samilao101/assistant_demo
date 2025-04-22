
import streamlit as st
import os
import openai
from dotenv import load_dotenv
import io
from database import database_manager as db_manager
import chardet
import model_api

if os.path.exists('certificate/certificate.crt'):
    os.environ['REQUESTS_CA_BUNDLE'] = 'certificate/certificate.crt'
else:
    print("Certificate file does not exist or is inaccessible.")
    
load_dotenv()

bot_id = 2

bot = db_manager.get_bot_by_id(bot_id)

bot_id, bot_name, bot_purpose, bot_file_name = bot

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

file_path = f'dataform/{bot_file_name}'

# Read file in binary mode first to detect encoding
with open(file_path, 'rb') as file:
    raw_data = file.read()
    result = chardet.detect(raw_data)

encoding = result['encoding']

# Try with detected encoding, fallback to latin-1 if it fails
try:
    with open(file_path, 'r', encoding=encoding) as file:
        file_content = file.read()
except UnicodeDecodeError:
    # Fallback to latin-1 which can handle any byte sequence
    with open(file_path, 'r', encoding='latin-1') as file:
        file_content = file.read()

st.image("cumminslogo.png")
st.header(f"{bot_name}")

prompt = st.text_input(
    f"Please type your {bot_name} questions below. Questions/Responses may be monitored.", 
    placeholder="Enter question...",
    key="user_prompt"  # Added unique key
)

formatted_response = ""

if st.button("Search") and prompt != "":
    complete_prompt = f"Use the following context below to answer question: {prompt} \n\n (Please use markdown to make the response easier to read). Do not make up answers and only respond to questions relevant to the context. \n\n context: {file_content}"
    with st.spinner("Generating response..."):
        interface = model_api.UniversalModelInterface()
        formatted_response = interface.get_response("gpt-4", complete_prompt, f'responses/{bot_name}.xlsx', prompt)

if formatted_response != "":
    st.write(formatted_response)
else:
    st.markdown(f"Definition: {bot_purpose}")
