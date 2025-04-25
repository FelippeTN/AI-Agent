from groq import Groq
import streamlit as st

def initialize_groq_client(api_key):
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"Erro ao inicializar cliente Groq: {str(e)}")
        return None

def agent_response(client, user_input, conversation_history, system_prompt="Você é um assistente de IA útil. Responda de forma clara e concisa."):
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