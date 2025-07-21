
import os
import smtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.schemas.email import EmailMessage
from app.core.config import config  # Adjust import as needed
from app.core.logger import logger


async def fetch_template_and_send_email(template: str, receiver: str, locals_: dict) -> None:
    """
    Sends an email using the specified template, receiver, and local variables.

    :param template: Name of the email template (without extension).
    :param receiver: Recipient's email address.
    :param locals_: Dictionary of template variables.
    """
    try:
        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'src', 'templates', 'emails')
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml', 'ejs'])
        )

        # Load the email template
        template_file = f"{template}.ejs"  # assuming .ejs is used
        template_obj = env.get_template(template_file)
        html_content = template_obj.render(locals_.dict())

        # Compose the email
        msg = EmailMessage()
        msg['Subject'] = 'Notification from MSA Application'
        msg['From'] = f"MSA Application <{config.MAIL_FROM}>"
        msg['To'] = receiver
        msg.set_content("This email requires an HTML-compatible email client.")
        msg.add_alternative(html_content, subtype='html')

        # Send the email using SMTP
        with smtplib.SMTP('smtp.ethereal.email', 587) as server:
            server.starttls()
            server.login(config.MAIL_FROM, config.MAIL_PASSWORD)
            await server.send_message(msg)

    except Exception as e:
        logger.error(str(e))
