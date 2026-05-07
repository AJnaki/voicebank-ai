import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, FileType, Disposition,
)
from app.config import get_settings
import asyncio

settings = get_settings()


def _mask_email(email: str) -> str:
    local, domain = email.split("@")
    return f"{local[0]}***@{domain}"


def _send_sync(to_email: str, subject: str, body: str, pdf_bytes: bytes | None, filename: str) -> bool:
    message = Mail(
        from_email=settings.email_from,
        to_emails=to_email,
        subject=subject,
        html_content=body,
    )
    if pdf_bytes:
        attachment = Attachment(
            FileContent(base64.b64encode(pdf_bytes).decode()),
            FileName(filename),
            FileType("application/pdf"),
            Disposition("attachment"),
        )
        message.attachment = attachment

    client = SendGridAPIClient(settings.sendgrid_api_key)
    response = client.send(message)
    return response.status_code in (200, 202)


async def send_statement_email(
    to_email: str, user_name: str, pdf_bytes: bytes, month_label: str
) -> tuple[bool, str]:
    """Send statement PDF via email. Returns (success, masked_email)."""
    subject = f"Your {month_label} Statement — {settings.bank_name}"
    body = (
        f"<p>Dear {user_name},</p>"
        f"<p>Please find attached your account statement for {month_label}.</p>"
        f"<p>If you have any questions, please contact us.</p>"
        f"<p>{settings.bank_name}</p>"
    )
    filename = f"statement_{month_label.replace(' ', '_')}.pdf"
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(
        None, _send_sync, to_email, subject, body, pdf_bytes, filename
    )
    return success, _mask_email(to_email)
