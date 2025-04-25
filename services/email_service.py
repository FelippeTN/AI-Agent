import imaplib
import email
from email.header import decode_header
import streamlit as st

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
        imap_server = "imap.gmail.com"
        imap = imaplib.IMAP4_SSL(imap_server, 993)
        imap.login(email_address, email_password)
        imap.select("INBOX")

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

            sender = email_msg["from"]
            subject = decode_email_subject(email_msg["subject"] or "Sem Assunto")
            date = email_msg["date"]

            body = ""
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                body = email_msg.get_payload(decode=True).decode('utf-8', errors='ignore')

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
        return None