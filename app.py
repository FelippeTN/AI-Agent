import streamlit as st
from config.config_loader import load_config
from services.ai_service import initialize_groq_client
from pages.chatbot_page import render as render_chatbot
from pages.email_page import render as render_email

st.set_page_config(page_title="Assistente de IA", page_icon="🤖")

config = load_config()
client = initialize_groq_client(config.get('GROQ_API_KEY') if config else None)

st.sidebar.title("Navegação")
opcao = st.sidebar.radio("Selecione uma funcionalidade:", ["Conversar com Chatbot", "Verificar Novos Emails"])

if opcao == "Conversar com Chatbot":
    render_chatbot(client)
elif opcao == "Verificar Novos Emails":
    render_email(client, config)