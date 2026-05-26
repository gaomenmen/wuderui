from flask import Flask, render_template, request, redirect, url_for, session
from flask_babel import Babel, gettext as _
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Babel 配置
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'zh']

def get_locale():
    lang = request.args.get('lang')
    if lang:
        session['lang'] = lang
    return session.get('lang', 'zh')

babel = Babel(app, locale_selector=get_locale)
app.jinja_env.globals['get_locale'] = get_locale

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/learn-chinese")
def learn_chinese():
    return render_template("learn_chinese.html")

@app.route("/tai-chi")
def tai_chi():
    return render_template("tai_chi.html")

@app.route("/custom-trips")
def custom_trips():
    return render_template("custom_trips.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == '__main__':
    app.run(debug=True)
