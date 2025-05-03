# core/email/utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# SMTP server configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')


# Jinja2 environment for rendering HTML templates
env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


def render_template(template_name: str, context: dict) -> str:
    """
    Render an HTML template with the provided context.

    Args:
        template_name (str): Name of the template file.
        context (dict): Dictionary with template variables and their values.

    Returns:
        str: Rendered HTML string.
    """
    template = env.get_template(template_name)
    return template.render(context)


# Function to send email
def dispatch_email(to_email: str, subject: str, html_body: str = None):
    msg = MIMEMultipart("alternative")
    msg['From'] = SMTP_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach both plain text and HTML versions to the email
    part = MIMEText(html_body, 'html')
    msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

print(SMTP_SERVER)
