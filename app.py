from flask import Flask, request, render_template
from flask_babel import Babel, _, get_locale  # ⬅ додали get_locale

app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

def select_locale():
    return request.args.get('lang') or app.config['BABEL_DEFAULT_LOCALE']

babel = Babel(app, locale_selector=select_locale)

# ⬅ зробимо змінну доступною в усіх шаблонах
@app.context_processor
def inject_locale():
    # get_locale() повертає Babel Locale; перетворимо на рядок ('uk', 'en', 'cs', ...)
    return {'current_locale': str(get_locale())}

@app.route("/")
def index():
    return render_template("index.html", name="Mykola Shyshka")

if __name__ == "__main__":
    app.run(debug=True)
