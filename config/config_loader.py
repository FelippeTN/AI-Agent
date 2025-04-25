import json
import streamlit as st

def load_config():
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
            return {
                'GROQ_API_KEY': config.get('GROQ_API_KEY'),
                'EMAIL_ADDRESS': config.get('EMAIL_ADDRESS'),
                'EMAIL_PASSWORD': config.get('EMAIL_PASSWORD')
            }
    except FileNotFoundError:
        st.error("Arquivo config.json não encontrado. Crie um arquivo com 'GROQ_API_KEY', 'EMAIL_ADDRESS' e 'EMAIL_PASSWORD'.")
        return None