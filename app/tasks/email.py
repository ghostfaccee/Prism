from email.mime.text import MIMEText
import aiosmtplib
from app.core import celery_app, settings
import asyncio

@celery_app.task
def send_verification_email(to_email: str, token: str):
    asyncio.run(_send_email(to_email, token))

async def _send_email(to_email: str, token: str):
    verification_link = f'{settings.VERIFICATION_LINK}/{token}'
    msg = MIMEText(f'Hi! Confirm your email by following the link: {verification_link}')
    msg['Subject'] = 'Email verification'
    msg['From'] = settings.SMTP_USER
    msg['To'] = to_email

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
        use_tls=False
    )
