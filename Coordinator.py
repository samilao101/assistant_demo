import streamlit as st
import os
import openai
from dotenv import load_dotenv
import io
from database import database_manager as db_manager
from forms_templates import prompt_generator
from streamlit_javascript import st_javascript
base_url = st_javascript("await fetch('').then(r => window.parent.location.href)", key="secret")

if os.path.exists(os.path.join('certificate', 'certificate.crt')):
    os.environ['REQUESTS_CA_BUNDLE'] = os.path.join('certificate', 'certificate.crt')
else:
    print("Certificate file does not exist or is inaccessible.")

load_dotenv()

# Try to get API key from environment first, then from Streamlit secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
try:
    if not OPENAI_API_KEY and 'openai' in st.secrets:
        OPENAI_API_KEY = st.secrets["openai"]["api_key"]
except:
    pass

openai.api_key = OPENAI_API_KEY

def convert_spaces_to_underscores(input_string):
    # Replace white spaces with underscores using the str.replace method
    result_string = input_string.replace(" ", "_")
    return result_string

def truncate_text(text, max_chars=250):
    if len(text) > max_chars:
        return text[:max_chars] + '...'
    else:
        return text

def sidebar():
    st.sidebar.header("Find:") 
    question = st.sidebar.text_area(  # Moved to sidebar
        "What are you trying to do or learn more about?", placeholder="Enter question...")

    formatted_response = ""


    if st.sidebar.button("Search") and question != "":  
        loading_message = st.sidebar.empty()  # Create an empty slot in the sidebar.
        loading_message.text("Generating response...")  # Display loading message in the sidebar.

        prompt_question = prompt_generator.generate_coordinator_prompt(question)
        
        # Updated to use the new OpenAI client
        client = openai.OpenAI()
        generated_response = client.chat.completions.create(
            model='gpt-4',
            messages=[
                {"role": "user", "content": prompt_question}
            ],
            temperature=0.0
        )
        
        formatted_response = generated_response.choices[0].message.content
        loading_message.text("")  # Clear the loading message or replace it with the completed message.

            

    if formatted_response != "":
        st.sidebar.markdown(formatted_response)  # Moved to sidebar
    else:
        st.sidebar.markdown(f"")  # Moved to sidebar

sidebar()
st.image("cumminslogo.png")  # Moved to sidebar
st.header("FAQ Harbor:")
st.markdown('_A safe place to dock with your questions and sail away with great answers..._')
all_bots = db_manager.get_all_bots_query()

query = st.text_input('Search process you would like to know more about by title or key words....')

filtered_bots = [bot for bot in all_bots if query.lower() in bot['name'].lower() or query.lower() in bot['purpose'].lower()]

num_columns = 3
cols = st.columns(num_columns)

if not filtered_bots:
    st.write("Not found.")
else:
    for i in range(0, len(filtered_bots), num_columns):
        for j in range(num_columns):
            idx = i + j
            if idx < len(filtered_bots):  # Ensure idx is within the range of filtered_bots
                bot = filtered_bots[idx]
                cols[j].markdown(f"[{bot['name']}]({base_url}{convert_spaces_to_underscores(bot['name'])})")
                cols[j].markdown(f"{truncate_text(bot['purpose'])}")