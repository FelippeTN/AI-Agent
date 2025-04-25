import streamlit as st
from services.email_service import fetch_new_emails
from services.ai_service import agent_response

def render(client, config):
    st.title("Verificar Novos Emails")
    st.subheader("Busque novos emails não lidos e gere um relatório.")

    if not config or not config.get('EMAIL_ADDRESS') or not config.get('EMAIL_PASSWORD'):
        st.error("Credenciais de email não encontradas no config.json.")
        return

    if 'email_report_history' not in st.session_state:
        st.session_state.email_report_history = []

    if st.button("Buscar Novos Emails"):
        emails = fetch_new_emails(config['EMAIL_ADDRESS'], config['EMAIL_PASSWORD'])
        
        if not emails:
            st.info("Nenhum email não lido encontrado.")
        elif isinstance(emails, str):
            st.error(emails)
        else:
            for email_data in emails:
                report_input = f"Remetente: {email_data['sender']}\nAssunto: {email_data['subject']}\nData: {email_data['date']}\nTrecho: {email_data['body_snippet']}"
                system_prompt = "Você é um assistente de IA especializado em análise de emails. Gere um relatório conciso para o email fornecido, destacando remetente, assunto, data, tom e pontos-chave do trecho fornecido."
                report = agent_response(client, report_input, [], system_prompt)
                
                st.session_state.email_report_history.append({
                    "role": "email",
                    "content": report_input
                })
                st.session_state.email_report_history.append({
                    "role": "report",
                    "content": report
                })

    if st.session_state.email_report_history:
        st.subheader("Relatórios de Emails")
        for message in st.session_state.email_report_history:
            with st.container():
                if message["role"] == "email":
                    st.write("**Email Recebido:**")
                    st.write(message["content"])
                else:
                    st.write("**Relatório Gerado:**")
                    st.write(message["content"])
                st.divider()

    if st.button("Limpar Histórico de Emails"):
        st.session_state.email_report_history = []
        st.rerun()