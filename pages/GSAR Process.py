import streamlit as st
import os
import openai
from dotenv import load_dotenv
import io
from database import database_manager as db_manager
import chardet

from GSAR_functions import functions, document_creator
import json
import io
from docx import Document
import model_api

if os.path.exists('certificate\certificate.crt'):
    os.environ['REQUESTS_CA_BUNDLE'] = 'certificate\certificate.crt'
else:
    print("Certificate file does not exist or is inaccessible.")
    
load_dotenv()

bot_id = 1

bot = db_manager.get_bot_by_id(bot_id)

bot_id, bot_name, bot_purpose, bot_file_name = bot

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

file_path = f'dataform/{bot_file_name}'

with open(file_path, 'rb') as file:
    result = chardet.detect(file.read())

encoding = result['encoding']

with open(file_path, 'r', encoding = encoding) as file:
    file_content = file.read()

def process_function_call(response):
    available_functions = {
        "create_document_with_settings" : functions.create_document_with_settings
    }
    function_name = response.function_call.name
    function_to_call = available_functions[function_name]
    function_args = json.loads(response.function_call.arguments)
    function_response = function_to_call(
        document_settings=function_args
    )

st.image("cumminslogo.png")
st.header(f"{bot_name}")

prompt = st.text_input(
    f"Please type your {bot_name} questions below. Questions/Responses may be monitored.", placeholder="Enter question...")

formatted_response = ""

if st.button("Search") and prompt != "":
    complete_prompt = f"Use the following context below to answer question: {prompt}\n\n(Please use markdown to make the response easier to read). Do not make up answers and only respond to questions relevant to the context.\n\nIf the user is requesting to create or update a GSAR document, please use the create_document_with_settings function with the appropriate settings. For example, if they want to update an address, set address_update to 'yes'.\n\nContext: {file_content}"
    with st.spinner("Generating response..."):
    
        interface = model_api.UniversalModelInterface()

        generated_response = interface.get_response("gpt-4-response", complete_prompt, f'responses/{bot_name}.xlsx', prompt)
        print(complete_prompt)
        response_message = generated_response.choices[0].message
        
        if hasattr(response_message, "function_call") and response_message.function_call:
            process_function_call(response=response_message)
            doc_download = document_creator.return_document()
            print(type(doc_download))
            bio = io.BytesIO()
            doc_download.save(bio)
            if doc_download:
                st.download_button(
                    label="Click here to download",
                    data=bio.getvalue(),
                    file_name="template.docx",
                    mime="docx"
                )
        formatted_response = response_message.content


if formatted_response != "":
    st.write(formatted_response)
else:
    st.markdown(f"Definition: {bot_purpose}")