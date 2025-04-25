import streamlit as st
from services.ai_service import agent_response

def render(client):
    st.title("Chatbot Inteligente")
    st.subheader("Faça suas perguntas e receba respostas instantâneas!")

    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    user_input = st.chat_input("Digite sua pergunta aqui...")
    if user_input:
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        response = agent_response(client, user_input, st.session_state.conversation_history)
        st.session_state.conversation_history.append({"role": "assistant", "content": response})

    for message in st.session_state.conversation_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.button("Limpar Conversa"):
        st.session_state.conversation_history = []
        st.rerun()