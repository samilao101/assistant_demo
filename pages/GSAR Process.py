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
from pathlib import Path


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

st.audio("gsar.audio.wav", format="audio/wav", loop=True)


prompt = st.text_input(
    f"Please type your {bot_name} questions below. Questions/Responses may be monitored.", placeholder="Enter question...")

formatted_response = ""
generate_doc = st.toggle("Generate Template/S360 eForm Steps", value=False)

if st.button("Search") and prompt != "":

    if generate_doc:
        complete_prompt = f"Use the following context below to answer question: {prompt}\n\n(Please use markdown to make the response easier to read). Do not make up answers and only respond to questions relevant to the context.\n\nIf the user is requesting to create or update a GSAR document, please use the create_document_with_settings function with the appropriate settings. For example, if they want to update an address, set address_update to 'yes'.\n\nContext: {file_content}. \n\n If they dont ask for a form or document, just provide the response making a function call to create_document_with_settings."
        response_type = "gpt-4-response"
    else:
        complete_prompt = f"Use the following context below to answer question: {prompt}\n\n(Please use markdown to make the response easier to read). Do not make up answers and only respond to questions relevant to the context.\n\n Context: {file_content}"
        response_type = "gpt-4"
    with st.spinner("Generating response..."):
        if generate_doc:       
            interface = model_api.UniversalModelInterface()
            generated_response = interface.get_response(response_type, complete_prompt, f'responses/{bot_name}.xlsx', prompt)
            response_message = generated_response.choices[0].message 
            if hasattr(response_message, "function_call") and response_message.function_call:
                # Process the function call (e.g., build the docx)
                process_function_call(response=response_message)

                # Retrieve first document
                doc_download = document_creator.return_document()
                bio = io.BytesIO()
                doc_download.save(bio)
                bio.seek(0)  # Ensure the buffer is at the beginning

                if doc_download:
                    st.download_button(
                        label="Download Template Document",
                        data=bio.getvalue(),
                        file_name="template.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                # Retrieve second document (eForm)
                doc_download2 = document_creator.return_eform_document()
                bio2 = io.BytesIO()
                doc_download2.save(bio2)
                bio2.seek(0)

                if doc_download2:
                    st.download_button(
                        label="Download S360 E-Form Steps",
                        data=bio2.getvalue(),
                        file_name="eform_docs.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                formatted_response = response_message.content
        else:
            interface = model_api.UniversalModelInterface()
            formatted_response = interface.get_response("gpt-4", complete_prompt, f'responses/{bot_name}.xlsx', prompt)            

if formatted_response != "":
    st.write(formatted_response)
else:
    st.markdown(f"Definition: {bot_purpose}")

st.link_button("Additional Information/Templates/Training", "https://cummins365.sharepoint.com/sites/CS405/SitePages/S360.aspx")

# html = Path("GSAR.html").read_text(encoding="utf‑8")

# # 2 ‑ embed it in an iframe‑like component
# st.components.v1.html(
#     html,
#     height=900,          # make taller or set width=…
#     scrolling=True       # allow the user to scroll within the frame
# )