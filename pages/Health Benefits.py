
import streamlit as st
import os
import openai
from dotenv import load_dotenv
import io
from database import database_manager as db_manager
import chardet

if os.path.exists('certificate\certificate.crt'):
    os.environ['REQUESTS_CA_BUNDLE'] = 'certificate\certificate.crt'
else:
    print("Certificate file does not exist or is inaccessible.")
    
load_dotenv()

bot_id = 3

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

st.image("cumminslogo.png")
st.header(f"{bot_name}")

prompt = st.text_input(
    f"Please type your {bot_name} questions below. Questions/Responses may be monitored.", placeholder="Enter question...")

formatted_response = ""

if st.button("Search") and prompt != "":
    complete_prompt = f"Use the following context below to answer question:  {prompt} /n/n (Please use markdown to make the response easier to read). Do not make up answers and only respond to questions relevant to to the context. /n/n context: {file_content}"
    with st.spinner("Generating response..."):
        generated_response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[
                {"role": "user", "content": complete_prompt}
            ],
            temperature=0.0
        )

        formatted_response = generated_response['choices'][0]['message']['content']


if formatted_response != "":
    st.write(formatted_response)
else:
    st.markdown(f"Definition: {bot_purpose}")


st.write("**Benefits Summary**: [link](https://cummins365.sharepoint.com/sites/GRP_CC42904/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FGRP%5FCC42904%2FShared%20Documents%2FBenefits%2F2022%20Employee%20Benefit%20Summary%2Epdf&parent=%2Fsites%2FGRP%5FCC42904%2FShared%20Documents%2FBenefits)")