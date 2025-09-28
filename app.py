import os
from flask import (
    Flask, request, render_template, abort,
    redirect, url_for, flash, session, g
)
from flask_babel import Babel, _, get_locale
from dotenv import load_dotenv, find_dotenv
import requests  # потрібен для SendGrid

# -------------------- ENV --------------------
load_dotenv(find_dotenv())

# -------------------- APP --------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-only-change-me')

# i18n
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['LANGUAGES'] = ['en', 'cs', 'uk']

# -------------------- SENDGRID --------------------
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
MAIL_TO = os.getenv("MAIL_TO")  # куди надсилати листи з форми

# -------------------- LOCALE --------------------
def _norm_lang(lang: str | None) -> str | None:
    if not lang:
        return None
    lang = lang.replace('-', '_').lower()
    return lang.split('_', 1)[0]

def _select_locale():
    """?lang → session → Accept-Language → 'en'"""
    supported = app.config['LANGUAGES']

    raw = request.args.get('lang')
    lang = _norm_lang(raw)
    if lang in supported:
        session['lang'] = lang
        g.current_locale = lang
        return lang

    lang = _norm_lang(session.get('lang'))
    if lang in supported:
        g.current_locale = lang
        return lang

    best = request.accept_languages.best_match(supported) or 'en'
    g.current_locale = best
    return best

# Працює як із Babel 4.x, так і зі старішими
babel = Babel()
try:
    # Babel 4.x
    babel.init_app(app, locale_selector=_select_locale)
except TypeError:
    # 2.x/3.x
    babel.init_app(app)
    if hasattr(babel, "locale_selector"):
        try:
            babel.locale_selector(_select_locale)  # callable форма
        except TypeError:
            pass
    if hasattr(babel, "localeselector"):
        try:
            babel.localeselector(_select_locale)
        except TypeError:
            pass

@app.context_processor
def inject_locale():
    return {"current_locale": str(get_locale())}

# -------------------- ROUTES --------------------
@app.route("/")
def index():
    return render_template("index.html", name="Mykola Shyshka")

@app.post("/contact")
def contact():
    # Поля форми
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    msg = (request.form.get("message") or "").strip()
    website_hp = (request.form.get("website") or "").strip()  # honeypot

    # Мова для редіректу
    lang = _norm_lang(
        request.args.get("lang")
        or request.form.get("lang")
        or session.get("lang")
        or str(get_locale())
    ) or 'en'

    # Проста валідація
    if website_hp:
        abort(400, "Bot detected")
    if not name or not email or not msg:
        abort(400, "Missing fields")
    if any(x in name for x in ("\r", "\n")) or any(x in email for x in ("\r", "\n")):
        abort(400, "Invalid input")

    subject = f"Portfolio contact: {name}"
    text = f"From: {name} <{email}>\n\n{msg}"

    # Перевірки конфігурації відправки
    if not SENDGRID_API_KEY:
        app.logger.error("SENDGRID_API_KEY is missing")
        abort(500, "Mail service not configured")
    if not MAIL_TO:
        app.logger.error("MAIL_TO is missing")
        abort(500, "Mail recipient not configured")

    # Надсилання через SendGrid
    try:
        send_via_sendgrid(SENDGRID_API_KEY, MAIL_TO, subject, text, reply_email=email, reply_name=name)
    except Exception as e:
        app.logger.exception("Mail send failed")
        abort(500, "Mail send failed")

    flash(_("Thanks! Your message has been sent."), "success")
    return redirect(url_for("index", _anchor="contact", lang=lang))

# -------------------- SENDGRID SENDER --------------------
def send_via_sendgrid(api_key: str, to_addr: str, subject: str, text: str, reply_email: str, reply_name: str):
    """
    Відправка листа через SendGrid API v3.
    """
    import json
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "personalizations": [
            {"to": [{"email": to_addr}]}
        ],
        # 'from' краще вказувати так само як і MAIL_TO (Single Sender)
        "from": {"email": to_addr, "name": "Portfolio Form"},
        "reply_to": {"email": reply_email, "name": reply_name},
        "subject": subject,
        "content": [{"type": "text/plain", "value": text}],
    }
    r = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers=headers,
        data=json.dumps(data),
        timeout=15,
    )
    # Якщо SendGrid повертає 202 — це успіх; інші коди — помилка
    if r.status_code != 202:
        raise RuntimeError(f"SendGrid error {r.status_code}: {r.text}")

# -------------------- DEV --------------------
if __name__ == "__main__":
    app.run(debug=False)
