import win32com.client as win32


def send_outlook_email(
    subject: str,
    body: str,
    to_emails: str,
    cc_emails: str | None = None,
    attachments: list[str] | None = None,
    display_draft: bool = True,
) -> None:
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)  # 0: Mail item

    mail.Subject = subject
    mail.Body = body
    mail.To = to_emails  # semi-colon-separated string
    if cc_emails:
        mail.CC = cc_emails  # Optional semi-colon-separated string

    # Add attachments if any
    if attachments:
        for file_path in attachments:
            mail.Attachments.Add(file_path)

    if display_draft:
        mail.Display()
    else:
        mail.Send()


if __name__ == '__main__':
    subject = 'Test Email'
    body = 'This is a test email.'
    to_emails = 'erbe.joshua@gmail.com;j.erbe@oregon-physics.com'
    cc_emails = None
    attachments = [r'C:\Users\joshua\Desktop\MA-H201-002 Hyperion H201 Manual_v1.docx']
    send_outlook_email(subject, body, to_emails, cc_emails, attachments)
