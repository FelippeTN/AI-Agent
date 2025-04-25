import streamlit as st
import imaplib
import email
from email.header import decode_header
from uuid import uuid4
from agent_config import load_config, agent_response

config = load_config()

def decode_email_subject(subject):
    decoded_subject = decode_header(subject)[0][0]
    if isinstance(decoded_subject, bytes):
        try:
            return decoded_subject.decode()
        except:
            return decoded_subject.decode('utf-8', errors='ignore')
    return decoded_subject

def fetch_new_emails(email_address, email_password, max_emails=10):
    try:
        # Conectar ao servidor IMAP do Gmail
        imap_server = "imap.gmail.com"
        imap = imaplib.IMAP4_SSL(imap_server, 993)
        imap.login(email_address, email_password)
        imap.select("INBOX")

        # Buscar emails não lidos
        st.write("Buscando emails não lidos...")
        _, message_numbers = imap.search(None, "UNSEEN")
        message_ids = sorted(message_numbers[0].split(), key=int, reverse=True)
        message_ids = message_ids[:max_emails]
        st.write(f"Processando {len(message_ids)} emails não lidos (máximo: {max_emails})...")
        
        emails = []
        for num in message_ids:
            _, msg_data = imap.fetch(num, "(RFC822)")
            email_body = msg_data[0][1]
            email_msg = email.message_from_bytes(email_body)
            
            # Extrair remetente, assunto e data
            sender = email_msg["from"]
            subject = decode_email_subject(email_msg["subject"] or "Sem Assunto")
            date = email_msg["date"]
            
            # Extrair corpo do email
            body = ""
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                body = email_msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            # Limitar o corpo a 200 caracteres para o relatório inicial
            body_snippet = (body[:200] + "...") if len(body) > 200 else body
            
            emails.append({
                "sender": sender,
                "subject": subject,
                "date": date,
                "body_snippet": body_snippet,
                "full_body": body
            })
        
        imap.logout()
        st.write("Busca concluída! Gerando relatórios...")
        return emails
    except Exception as e:
        st.error(f"Erro ao buscar emails: {str(e)}")
        return f"Erro ao buscar emails: {str(e)}"

# Configuração da interface Streamlit
st.set_page_config(page_title="Assistente de IA", page_icon="🤖")

# Menu de navegação lateral
st.sidebar.title("Navegação")
opcao = st.sidebar.radio("Selecione uma funcionalidade:", ["Conversar com Chatbot", "Verificar Novos Emails"])

# Inicializar históricos
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'report_history' not in st.session_state:
    st.session_state.report_history = []
if 'email_report_history' not in st.session_state:
    st.session_state.email_report_history = []

# Funcionalidade: Conversar com Chatbot
if opcao == "Conversar com Chatbot":
    st.title("Chatbot Inteligente")
    st.subheader("Faça suas perguntas e receba respostas instantâneas!")

    user_input = st.chat_input("Digite sua pergunta aqui...")
    if user_input:
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        response = agent_response(user_input, st.session_state.conversation_history)
        st.session_state.conversation_history.append({"role": "assistant", "content": response})
    
    for message in st.session_state.conversation_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.button("Limpar Conversa"):
        st.session_state.conversation_history = []
        st.rerun()


elif opcao == "Verificar Novos Emails":
    st.title("Verificar Novos Emails")
    st.subheader("Busque novos emails não lidos e gere um relatório.")

    if not config or not config.get('EMAIL_ADDRESS') or not config.get('EMAIL_PASSWORD'):
        st.error("Credenciais de email não encontradas no config.json.")
    else:
        if st.button("Buscar Novos Emails"):
            emails = fetch_new_emails(config['EMAIL_ADDRESS'], config['EMAIL_PASSWORD'])
            
            if isinstance(emails, str):
                st.error(emails)
            elif not emails:
                st.info("Nenhum email não lido encontrado.")
            else:
                # Gerar relatório para cada email
                for email_data in emails:
                    report_input = f"Remetente: {email_data['sender']}\nAssunto: {email_data['subject']}\nData: {email_data['date']}\nTrecho: {email_data['body_snippet']}"
                    system_prompt = "Você é um assistente de IA especializado em análise de emails. Gere um relatório conciso para o email fornecido, destacando remetente, assunto, data, tom e pontos-chave do trecho fornecido."
                    report = agent_response(report_input, [], system_prompt)
                    
                    st.session_state.email_report_history.append({
                        "role": "email",
                        "content": report_input
                    })
                    st.session_state.email_report_history.append({
                        "role": "report",
                        "content": report
                    })

        # Exibir histórico de relatórios de emails
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