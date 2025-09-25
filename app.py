# app.py
import os
import smtplib
from email.message import EmailMessage
from flask import Flask, request, render_template, render_template_string, abort, redirect, url_for, flash
from flask_babel import Babel, _, get_locale
import requests

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())  # знайде найближчий .env і завантажить


app = Flask(__name__)
app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-only-change-me')

# Змінні середовища
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
MAIL_TO   = os.getenv("MAIL_TO", SMTP_USER)

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")  # опційно
# RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET")  # опційно
app.secret_key = "SECRET_KEY"  


# Мінімальна валідація конфіга
if not SMTP_USER or not SMTP_PASS:
    raise RuntimeError("SMTP_USER/SMTP_PASS не задані. Перевір .env або змінні середовища.")

def select_locale():
    # ?lang=uk / ?lang=en / ?lang=cs
    return request.args.get("lang") or app.config["BABEL_DEFAULT_LOCALE"]

babel = Babel(app, locale_selector=select_locale)

@app.post("/contact")
def contact():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    msg = (request.form.get("message") or "").strip()
    website_hp = (request.form.get("website") or "").strip()  # honeypot

    # Honeypot
    if website_hp:
        abort(400, "Bot detected")

    # Проста валідація
    if not name or not email or not msg:
        abort(400, "Missing fields")

    # Захист від інʼєкцій у заголовках
    if any(x in name for x in ("\r", "\n")) or any(x in email for x in ("\r", "\n")):
        abort(400, "Invalid input")

    # (Опційно) reCAPTCHA
    # token = request.form.get("g-recaptcha-response")
    # if token:
    #     r = requests.post(
    #         "https://www.google.com/recaptcha/api/siteverify",
    #         data={"secret": RECAPTCHA_SECRET, "response": token},
    #         timeout=10,
    #     )
    #     if not r.json().get("success"):
    #         abort(400, "reCAPTCHA failed")

    subject = f"Portfolio contact: {name}"
    text = f"From: {name} <{email}>\n\n{msg}"

    if SENDGRID_API_KEY:
        send_via_sendgrid(SENDGRID_API_KEY, MAIL_TO, subject, text, email, name)
    else:
        send_via_smtp(MAIL_TO, subject, text, reply_email=email, reply_name=name)

    flash(_("Thanks! Your message has been sent."), "success")
    return redirect(url_for("index", _anchor="contact"))

def send_via_smtp(to_addr, subject, text, reply_email=None, reply_name=None):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_addr
    msg["Subject"] = subject
    if reply_email:
        msg["Reply-To"] = f"{reply_name} <{reply_email}>" if reply_name else reply_email
    msg.set_content(text)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)

def send_via_sendgrid(api_key, to_addr, subject, text, reply_email, reply_name):
    import json
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "personalizations": [{"to": [{"email": to_addr}]}],
        "from": {"email": to_addr, "name": "Portfolio Form"},
        "reply_to": {"email": reply_email, "name": reply_name},
        "subject": subject,
        "content": [{"type": "text/plain", "value": text}],
    }
    r = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers=headers,
        data=json.dumps(data),
        timeout=10,
    )
    r.raise_for_status()

@app.context_processor
def inject_locale():
    return {"current_locale": str(get_locale())}

@app.route("/")
def index():
    return render_template("index.html", name="Mykola Shyshka")

if __name__ == "__main__":
    app.run(debug=True)
