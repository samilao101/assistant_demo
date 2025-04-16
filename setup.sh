#!/bin/bash

# Print Python version
python --version

# Make sure pip is up to date
pip install --upgrade pip

# Direct install of openai with pip
pip install openai

# Install Python dependencies from requirements.txt
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