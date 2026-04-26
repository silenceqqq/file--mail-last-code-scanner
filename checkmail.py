import imaplib
import email
import re

IMAP_HOST = "imap.firstmail.ltd"  # замени на реальный сервер


def load_accounts(file_path):
    accounts = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                email_addr, password = line.strip().split(":", 1)
                accounts.append((email_addr, password))
    return accounts


def extract_code(text):
    # ищем подряд 4-8 цифр (обычные коды подтверждения)
    match = re.search(r"\b\d{4,8}\b", text)
    return match.group(0) if match else None


def get_last_email_code(mail):
    status, data = mail.select("INBOX")
    if status != "OK":
        return None

    status, messages = mail.search(None, "ALL")
    if status != "OK":
        return None

    mail_ids = messages[0].split()
    if not mail_ids:
        return None

    latest_id = mail_ids[-1]

    status, msg_data = mail.fetch(latest_id, "(RFC822)")
    if status != "OK":
        return None

    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)

    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    body += part.get_payload(decode=True).decode(errors="ignore")
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode(errors="ignore")
        except:
            pass

    return extract_code(body)


def process_accounts(accounts):
    for email_addr, password in accounts:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_HOST)
            mail.login(email_addr, password)

            code = get_last_email_code(mail)

            if code:
                print(f"{email_addr} → код: {code}")
            else:
                print(f"{email_addr} → код не найден")

            mail.logout()

        except Exception as e:
            print(f"{email_addr} → ошибка: {e}")


if __name__ == "__main__":
    accounts = load_accounts("accounts.txt")
    process_accounts(accounts)