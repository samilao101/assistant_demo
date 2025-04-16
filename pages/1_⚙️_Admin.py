import streamlit as st
from forms_templates.templates import generate_page_template
import os
import shutil
import random
import string
import openai
from openai import OpenAI
from io import StringIO
from dotenv import load_dotenv
import io
import sqlite3
from database import database_manager as db_manager
import time
import pickle
from pathlib import Path

if os.path.exists(os.path.join('certificate', 'certificate.crt')):
    os.environ['REQUESTS_CA_BUNDLE'] = os.path.join('certificate', 'certificate.crt')
else:
    print("Certificate file does not exist or is inaccessible.")

# For demo purposes, we're skipping authentication
load_dotenv()

db_manager.create_table()

# Try to get API key from environment first, then from Streamlit secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
try:
    if not OPENAI_API_KEY and 'openai' in st.secrets:
        OPENAI_API_KEY = st.secrets["openai"]["api_key"]
except:
    pass
    
client = OpenAI(api_key=OPENAI_API_KEY)
openai.api_key = OPENAI_API_KEY

st.header("Create a Bot")

if 'show_fields' not in st.session_state:
    st.session_state.show_fields = True

if st.session_state.show_fields == True:
    name = st.text_input("Name of Bot")

    col1, col2 = st.columns(2)

    uploaded_file = st.file_uploader("Instructions File", type=['txt'])

    if 'formatted_response' not in st.session_state:
        st.session_state.formatted_response = ""

    if st.button("Generate Purpose from File"):
        if uploaded_file is not None:
            bytes_data = uploaded_file.getvalue()

            all_text = bytes_data.decode('utf-8')
            
            gsar_prompt = f"summarize the following text into 2 to 3 concise sentences describing it in the way you would see it as introductory paragraph:  {all_text} /n/n "
            
            with st.spinner("Generating response..."):
                response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{gsar_prompt}"}
                ]
                )

                formatted_response = response.choices[0].message.content
                st.session_state.formatted_response = formatted_response
            
    purpose = st.text_area("Purpose of Bot", st.session_state.formatted_response)

    if uploaded_file is not None and purpose != "" and name != "":
        if st.button("Create"):
            file_name = f"{name}.py"
            folder_name = "pages"
            
            try:
                file_extension = os.path.splitext(uploaded_file.name)[-1].lower()
                    
                # Specify the folder where you want to save the file
                save_folder = "dataform"
                    
                # Create the folder if it doesn't exist
                if not os.path.exists(save_folder):
                    os.makedirs(save_folder)
                    
                # Construct the full path to save the file
                save_path = os.path.join(save_folder, uploaded_file.name)
                    
                # Save the file to the specified location
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getvalue())


            except Exception as e:
                st.error(f"Error saving file: {e}")
                
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            file_path = os.path.join(folder_name, file_name)

            try:
                bot_id = db_manager.create_bot(name, purpose, uploaded_file)
                with open(file_path, "w") as file:
                    file.write(generate_page_template(name, uploaded_file.name, purpose, bot_id))

                st.success(f"Created Bot {name}.")

                
                st.session_state.show_fields = False

                st.session_state.formatted_response = ""




            except Exception as e:
                st.error(f"Error creating bot script: {e}")

else:
    st.success(f"Created New Bot")
    if st.button("Add More"):
        st.session_state.show_fields = True


bots_data = db_manager.get_all_bots()


st.divider()
if bots_data is not None:
    st.header("Built:")
    for bot in bots_data:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            new_name = st.text_input("Name", bot[1])

        with col2:
            new_purpose = st.text_area("Purpose", bot[2])

        with col3:
            new_data = st.file_uploader(f"{bot[3]}", type=['txt'])

        with col4:
            if st.button(f"Update {bot[1]}"):
                db_manager.update_bot(bot[0], new_name, new_purpose)
                db_manager.update_file_name(f"pages/{bot[1]}.py", f"{new_name}.py")


                if new_data is not None:
                    db_manager.delete_bot_file(f"dataform/{bot[3]}")
                    db_manager.create_new_file(new_data)
                    db_manager.update_bot_file_db(bot[0], new_data.name)



        with col5:
            if st.button(f"Delete {bot[1]}", type="primary"):
                db_manager.delete_row_by_id(bot[0])
                db_manager.delete_bot_file(f"pages/{bot[1]}.py")
        st.divider()




st.divider()
st.title('Delete All:')
st.write("Click the button below to delete all data from the database.")

# Button to delete data
if st.button('Delete All Data'):
    db_manager.delete_all_files()
    db_manager.delete_all_bots_from_db()

    st.write("All data has been deleted from the database.")