from pathlib import Path
from typing import List, Any, Dict
from pydantic import EmailStr, BaseModel

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from src.service import get_settings


class EmailSchema(BaseModel):
    email: List[EmailStr]
    body: Dict[str, Any]


app_settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=app_settings.mail_username,
    MAIL_PASSWORD=app_settings.mail_password,
    MAIL_FROM=EmailStr(app_settings.mail_from),
    MAIL_PORT=app_settings.mail_port,  # 587
    MAIL_SERVER=app_settings.mail_server,
    MAIL_STARTTLS=app_settings.mail_starttls,  # True
    MAIL_SSL_TLS=app_settings.mail_ssl_tls,  # False
    TEMPLATE_FOLDER=Path(__file__).parent / "email-templates",
    USE_CREDENTIALS=app_settings.use_credentials,
)

fm = FastMail(conf)


async def send_new_account_info(
    email: EmailStr, password: str, owner_name: str, subject: str = "New Account Info"
):
    email_body = {
        "password": password,
        "email": email,
        "login_ui_url": app_settings.login_ui_url,
        "owner_name": owner_name,
        "app_name": get_settings().app_name,
    }
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        template_body=email_body,
        subtype=MessageType.html,
    )
    await fm.send_message(message, template_name="new_account_info.html")


async def send_how_to_change_password_email(
    email: EmailStr, subject: str = "Change Password"
):
    email_body = {
        "email": email,
        "login_ui_url": app_settings.login_ui_url,
        "app_name": get_settings().app_name,
    }
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        template_body=email_body,
        subtype=MessageType.html,
    )
    await fm.send_message(message, template_name="how_to_change_password.html")


async def send_change_password_request_mail(
    email: EmailStr, subject: str, reset_token: str
) -> None:
    email_body = {
        "token": reset_token,
        "email": email,
        "reset_password_ui_url": app_settings.reset_password_ui_url,
        "expires_in": app_settings.password_request_minutes,
        "app_name": get_settings().app_name,
    }
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        template_body=email_body,
        subtype=MessageType.html,
    )
    await fm.send_message(message, template_name="password_change_request.html")


async def send_password_changed_mail(email: EmailStr) -> None:
    email_body = {
        "email": email,
        "app_name": get_settings().app_name,
    }
    message = MessageSchema(
        subject="Password Successfully Changed",
        recipients=[email],
        template_body=email_body,
        subtype=MessageType.html,
    )
    await fm.send_message(message, template_name="password_changed.html")
