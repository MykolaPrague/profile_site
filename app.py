import os
import smtplib
from email.message import EmailMessage

from flask import (
    Flask, request, render_template, abort,
    redirect, url_for, flash, session, g
)
from flask_babel import Babel, _, get_locale
from dotenv import load_dotenv, find_dotenv

# -------------------- ENV --------------------
load_dotenv(find_dotenv())

# -------------------- APP --------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-only-change-me')

# i18n
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['LANGUAGES'] = ['en', 'cs', 'uk']

# -------------------- SMTP --------------------
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
MAIL_TO   = os.getenv("MAIL_TO", SMTP_USER)

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

# Create Babel and register locale selector in a way that works across versions
babel = Babel()
# Try Babel 4.x style (init_app with keyword)
try:
    babel.init_app(app, locale_selector=_select_locale)
except TypeError:
    # Probably 2.x/3.x: init first, then try to register via attribute
    babel.init_app(app)
    # Try new attribute name (4.x) — callable form
    if hasattr(babel, "locale_selector"):
        try:
            babel.locale_selector(_select_locale)  # type: ignore[attr-defined]
        except TypeError:
            # Some builds expose it only as a decorator, ignore
            pass
    # Try old 2.x decorator-style registrar
    if hasattr(babel, "localeselector"):
        try:
            babel.localeselector(_select_locale)  # type: ignore[attr-defined]
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
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    msg = (request.form.get("message") or "").strip()
    website_hp = (request.form.get("website") or "").strip()

    lang = _norm_lang(
        request.args.get("lang")
        or request.form.get("lang")
        or session.get("lang")
        or str(get_locale())
    ) or 'en'

    if website_hp:
        abort(400, "Bot detected")
    if not name or not email or not msg:
        abort(400, "Missing fields")
    if any(x in name for x in ("\r", "\n")) or any(x in email for x in ("\r", "\n")):
        abort(400, "Invalid input")

    subject = f"Portfolio contact: {name}"
    text = f"From: {name} <{email}>\n\n{msg}"

    if not SMTP_USER or not SMTP_PASS:
        app.logger.error("SMTP credentials missing; set SMTP_USER/SMTP_PASS")
        abort(500, "Mail server not configured")

    try:
        send_via_smtp(MAIL_TO, subject, text, reply_email=email, reply_name=name)
    except Exception:
        app.logger.exception("Mail send failed")
        abort(500, "Mail send failed")

    flash(_("Thanks! Your message has been sent."), "success")
    return redirect(url_for("index", _anchor="contact", lang=lang))

# -------------------- SMTP SENDER --------------------
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

# -------------------- DEV --------------------
if __name__ == "__main__":
    app.run(debug=True)
