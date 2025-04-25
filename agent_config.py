import streamlit as st
from groq import Groq
import json, os

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

config = load_config()
client = Groq(api_key=config.get('GROQ_API_KEY') if config else None)

def agent_response(user_input, conversation_history, system_prompt="Você é um assistente de IA útil. Responda de forma clara e concisa."):
    if not client:
        return "Erro: Cliente Groq não inicializado."
    
    try:
        messages = [
            {"role": "system", "content": system_prompt}
        ] + conversation_history + [
            {"role": "user", "content": user_input}
        ]
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao processar a resposta: {str(e)}"