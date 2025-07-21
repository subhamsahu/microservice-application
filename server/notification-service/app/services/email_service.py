"""
Email Service Module
This module provides functionality to send emails using HTML templates and SMTP.
It uses Jinja2 for templating and supports both synchronous and asynchronous email sending.
"""

import os
from email.message import EmailMessage
import smtplib

import aiosmtplib

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import config  # adjust to match your project
from app.core.logger import logger  # adjust to match your project


class EmailService:
    """
    Service class for sending emails using HTML templates.
    """

    def __init__(self):
        self.log = logger

        # Setup Jinja2 template environment
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'emails')
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'ejs'])
        )

    def send_email(self, template_folder: str, receiver_email: str, email_details: dict) -> None:
        """
        Sends an email using HTML and subject templates stored under a template folder.
        """
        try:
            html_template = self.jinja_env.get_template(f"{template_folder}/html.ejs")
            subject_template = self.jinja_env.get_template(f"{template_folder}/subject.ejs")

            html_body = html_template.render(email_details)
            subject = subject_template.render(email_details)

            message = EmailMessage()
            message["Subject"] = subject or "MSA Notification"
            message["From"] = f"MSA Application <{config.MAIL_FROM}>"
            message["To"] = receiver_email
            message.set_content("This email requires an HTML-compatible email client.")
            message.add_alternative(html_body, subtype="html")

            with smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT) as smtp:
                smtp.starttls()
                smtp.login(config.MAIL_FROM, config.MAIL_PASSWORD)
                smtp.send_message(message)

            self.log.info(f"Email sent successfully to {receiver_email} using template folder '{template_folder}'.")

        except Exception as e:
            self.log.error(f"Error in send_email(): {str(e)}")

    async def async_send_email(self, template_folder: str, receiver_email: str, email_details: dict):
        """
        Asynchronous method to send an email using a template and dynamic variables.
        """
        try:
            html_template = self.jinja_env.get_template(f"{template_folder}/html.ejs")

            html_body = html_template.render(email_details)

            msg = EmailMessage()

            msg["Subject"] = email_details.get("subject", "MSA Notification")
            msg["From"] = f"MSA <{config.MAIL_FROM}>"
            msg["To"] = receiver_email
            msg.set_content("This email requires an HTML-compatible client.")
            msg.add_alternative(html_body, subtype="html")

            await aiosmtplib.send(
                msg,
                hostname=config.MAIL_SERVER,
                port=config.MAIL_PORT,
                start_tls=True,
                username=config.MAIL_FROM,
                password=config.MAIL_PASSWORD,
            )

            self.log.info(f"Async email to {receiver_email} with email subject '{msg["Subject"]}'")

        except Exception as e:
            self.log.error(f"EmailServiceAsync error: {str(e)}")
