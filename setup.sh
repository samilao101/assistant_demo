#!/bin/bash

# Print Python version
python --version

# Force installation of openai via pip
pip install openai==1.74.0

# Force installation via pipenv
pip install pipenv
pipenv install --deploy --skip-lock

# Force another direct pip install of key packages
pip install streamlit==1.25.0 openai==1.74.0 python-dotenv==1.0.0

# Install Python dependencies from requirements.txt as backup
pip install -r requirements.txt

# Check if OpenAI is installed
python -c "import openai; print('OpenAI version:', openai.__version__)"

mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
enableStaticServing = true\n\
" > ~/.streamlit/config.toml