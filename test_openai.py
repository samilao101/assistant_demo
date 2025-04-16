import streamlit as st
import os
import sys

# Print Python environment info
st.write(f"Python version: {sys.version}")
st.write(f"Python executable: {sys.executable}")

# Try to import openai
try:
    import openai
    st.success(f"Successfully imported openai version: {openai.__version__}")
except ImportError as e:
    st.error(f"Failed to import openai: {str(e)}")
    
# Show all installed packages
st.subheader("Installed Packages")
import subprocess
result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
st.code(result.stdout)