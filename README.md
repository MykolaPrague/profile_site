# 🌐 Mykola Shyshka – Profile Site (Flask + Render)

A lightweight personal portfolio website built with **Python (Flask)**,  
featuring multilingual support, email contact form, and clean responsive design.

---

### 🚀 Live Demo  
👉 [https://profile-site-eu.onrender.com](https://profile-site-eu.onrender.com)

> ⚠️ **Note:** This site is hosted on a free Render plan —  
> it may take up to 30–60 seconds to “wake up” after inactivity (cold start).

---

### 🧩 Tech Stack
- 🐍 **Backend:** Flask (Python 3.13)  
- 🌍 **Frontend:** HTML + CSS (PicoCSS) + Vanilla JS  
- 🌐 **Internationalization:** Flask-Babel (EN / CS / UK)  
- ✉️ **Contact form:** Flask-Mail / SendGrid integration  
- 🔒 **Environment variables:** `.env` via python-dotenv  
- 📦 **Hosting:** Render (free tier)  
- 🗄️ **Template engine:** Jinja2  

---

### ✨ Features
- 🌗 Light/Dark theme toggle (saved in localStorage)  
- 🈳 3 languages: English, Czech, Ukrainian  
- 💬 Contact form with SMTP/SendGrid email integration  
- 📱 Fully responsive layout (desktop & mobile)  
- ⚙️ Configurable via `.env` (safe for production)  
- 🧠 Simple, readable code structure  

---

### 🗂️ Folder Structure
profile_site/
│
├── app.py
├── templates/
│ └── index.html
├── static/
│ ├── style.css
│ ├── myScript.js
│ ├── avatar2.png
│ ├── background.png
│ └── favicon.ico
├── translations/
│ ├── en/
│ ├── cs/
│ └── uk/
├── .env.example
└── README.md

yaml
Копіювати код

---

### ⚙️ Environment Variables
To run locally, create a `.env` file in the project root:
FLASK_SECRET_KEY=your_secret
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_password
MAIL_TO=your_email@gmail.com

yaml
Копіювати код

> Or, if using SendGrid:
> ```
> SENDGRID_API_KEY=your_sendgrid_api_key
> MAIL_TO=your_email@example.com
> ```

---

### 🧭 Local Development
python -m venv .venv
source .venv/bin/activate # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask run

yaml
Копіювати код

Then open your browser at **http://127.0.0.1:5000**

---

### 📫 Contact
- 💬 **Telegram:** available upon request  
- 🧑‍💻 **GitHub:** [MykolaPrague](https://github.com/MykolaPrague)  
- 🧰 **Upwork:** [upwork.com/freelancers/~01d4779350a70aa648](https://www.upwork.com/freelancers/~01d4779350a70aa648)  
- ✉️ **Email:** *available upon request*

---

> ⚡ *This project demonstrates my ability to build multilingual Flask apps  
> with integrated email delivery, dynamic templates, and production deployment on Render.*
