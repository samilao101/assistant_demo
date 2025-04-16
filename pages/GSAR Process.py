import streamlit as st
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
import io
from database import database_manager as db_manager
import chardet
import PyPDF2
from GSAR_functions import functions, document_creator
import json
from docx import Document
import model_api

# Fix path handling for cross-platform compatibility
if os.path.exists(os.path.join('certificate', 'certificate.crt')):
    os.environ['REQUESTS_CA_BUNDLE'] = os.path.join('certificate', 'certificate.crt')
else:
    print("Certificate file does not exist or is inaccessible.")
    
load_dotenv()

try:
    bot_id = 1
    
    bot = db_manager.get_bot_by_id(bot_id)
    
    if bot:
        bot_id, bot_name, bot_purpose, bot_file_name = bot
        
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=OPENAI_API_KEY)
        openai.api_key = OPENAI_API_KEY
        
        file_path = f'dataform/{bot_file_name}'
        
        file_content = ""
        if os.path.exists(file_path):
            try:
                # For PDF files, use PyPDF2 to extract text
                if file_path.lower().endswith('.pdf'):
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        file_content = ""
                        for page in pdf_reader.pages:
                            text = page.extract_text()
                            if text:
                                file_content += text + "\n"
                else:
                    # For other file types, try different encodings
                    with open(file_path, 'rb') as file:
                        result = chardet.detect(file.read())
                    
                    encoding = result['encoding'] or 'utf-8'
                    
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            file_content = file.read()
                    except UnicodeDecodeError:
                        try:
                            with open(file_path, 'r', encoding='latin-1') as file:
                                file_content = file.read()
                        except UnicodeDecodeError:
                            # If all else fails, read as binary
                            with open(file_path, 'rb') as file:
                                file_content = "Binary file - cannot display content"
            except Exception as e:
                st.error(f"Error reading file: {e}")
                file_content = "File could not be read."
        else:
            st.warning(f"File not found: {file_path}")
            file_content = "File not found."

        def process_function_call(response):
            available_functions = {
                "create_document_with_settings": functions.create_document_with_settings
            }
            function_name = response["function_call"]["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(response["function_call"]["arguments"])
            function_response = function_to_call(
                document_settings=function_args
            )
        
        st.image("cumminslogo.png")
        st.header(f"{bot_name}")
        
        prompt = st.text_input(
            f"Please type your {bot_name} questions below. Questions/Responses may be monitored.", placeholder="Enter question...")
        
        formatted_response = ""
        
        if st.button("Search") and prompt != "":
            complete_prompt = f"Use the following context below to answer question:  {prompt} /n/n (Please use markdown to make the response easier to read). Do not make up answers and only respond to questions relevant to to the context. /n/n context: {file_content}"
            with st.spinner("Generating response..."):
            
                interface = model_api.UniversalModelInterface()
        
                generated_response = interface.get_response("gpt-4-response", complete_prompt, f'responses/{bot_name}.xlsx', prompt)
                print(complete_prompt)
                
                # Update for newer OpenAI API
                response_message = generated_response.choices[0].message
                
                if hasattr(response_message, "function_call") and response_message.function_call:
                    # Convert the response to the expected format
                    response_dict = {
                        "function_call": {
                            "name": response_message.function_call.name,
                            "arguments": response_message.function_call.arguments
                        }
                    }
                    process_function_call(response=response_dict)
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
                
                # Get the content
                formatted_response = response_message.content if response_message.content else ""
        
        if formatted_response != "":
            st.write(formatted_response)
        else:
            st.markdown(f"Definition: {bot_purpose}")
    else:
        st.error("Bot not found. Please create a bot first from the Admin page.")
except Exception as e:
    st.error(f"An error occurred: {e}")
    st.info("Please go to the Admin page to create a bot first.")