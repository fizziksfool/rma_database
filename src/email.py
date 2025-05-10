import win32com.client as win32


def send_outlook_email(subject, body, to_emails, cc_emails=None, attachments=None):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)  # 0: Mail item

    mail.Subject = subject
    mail.Body = body
    mail.To = to_emails  # Comma-separated string
    if cc_emails:
        mail.CC = cc_emails  # Optional

    # Add attachments if any
    if attachments:
        for file_path in attachments:
            mail.Attachments.Add(file_path)

    mail.Send()  # Use .Display() to open draft instead
    print('Email sent via Outlook.')
