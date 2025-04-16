#!/bin/bash

# Force installation of openai
pip install openai==1.74.0

# Install Python dependencies
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