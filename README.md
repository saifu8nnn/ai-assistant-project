# 🚀 Habibi AI Assistant 

Welcome to the **Habibi AI Assistant**! 

Ever wanted to build your own ChatGPT or Gemini clone from scratch? That's exactly what this project is. It's a fully functional, lightning-fast desktop application built with **Electron.js** on the frontend and **FastAPI** on the backend. It streams AI responses in real-time, remembers your chat history, and wraps it all in a sleek, modern dark-mode UI.

Whether you're here to use it, learn from the code, or contribute, I'm glad you stopped by!

---

## ✨ What's Inside? (Features)

*   **⚡ Real-Time Streaming:** Watch the AI type out its thoughts instantly using WebSockets. No waiting for long loading bars.
*   **🔐 Secure Authentication:** Full user registration and login system protected by JWT (JSON Web Tokens). Your chats are yours alone.
*   **🗄️ Persistent History:** Close the app, come back tomorrow, and your chats will be right there in the sidebar, thanks to our relational database setup.
*   **🎨 Clean, Native UI:** A beautiful dark-mode interface inspired by the best AI tools out there, powered by Electron for a native desktop feel.
*   **🧠 Groq-Powered AI:** Uses the incredibly fast Groq API (or any LLM provider you swap in) for instant, intelligent responses.
*   **Multi-Chat Sessions:** Grouping messages into distinct, separate conversations (like tabs).

---

## 🛠️ The Tech Stack

I chose tools that are fast, modern, and fun to work with:

**Backend:**
*   **FastAPI** (Python) - For blazing fast API endpoints and WebSocket handling.
*   **SQLAlchemy** - For robust database ORM.
*   **JWT & Passlib** - For bulletproof security and password hashing.
*   **Groq API** - The brain behind the AI.

**Frontend:**
*   **Electron.js** - To package this into an awesome desktop app.
*   **HTML/CSS/Vanilla JS** - No heavy frameworks, just pure, lightweight DOM manipulation for maximum speed.

---

## 🚦 Getting Started

Ready to fire this up on your own machine? It’s easier than you think. You'll need two terminal windows: one for the backend, and one for the frontend.

### Prerequisites
*   [Python 3.8+](https://www.python.org/downloads/)
*   [Node.js & npm](https://nodejs.org/)
*   A free API key from [Groq](https://console.groq.com/)

### Step 1: Set up the Backend (The Brains 🧠)

1. Navigate to the backend folder:
   ```bash
   cd backend

```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

```


3. Install the required Python packages:
```bash
pip install fastapi uvicorn sqlalchemy passlib bcrypt python-jose websockets python-dotenv

```


4. Create a `.env` file in your `backend` folder and add your keys:
```env
GROQ_API_KEY="your_actual_api_key_here"
SECRET_KEY="make_up_a_super_secret_string_here"

```


5. Start the backend server:
```bash
uvicorn app.main:app --reload

```


*Your backend is now humming along at `http://127.0.0.1:8000`!*

### Step 2: Set up the Frontend (The Beauty 🎨)

1. Open a new terminal and navigate to the frontend folder (or your project root where `package.json` is):
```bash
# Make sure you are in the directory containing package.json

```


2. Install the Electron dependencies:
```bash
npm install

```


3. Launch the desktop app:
```bash
npm start

```



Boom! 💥 The app should pop up on your screen. Create an account, log in, and start chatting!

---

## 📂 Project Structure

A quick map of the codebase so you don't get lost:

├── backend
|  ├── alembic
|  |  ├── env.py
|  |  ├── README
|  |  ├── script.py.mako
|  |  └── versions
|  |  |  └── 6544f581e127_create_initial_tables.py
|  ├── alembic.ini
|  ├── app
|  |  ├── auth.py
|  |  ├── database.py
|  |  ├── llm.py
|  |  ├── main.py
|  |  ├── models.py
|  |  ├── schemas.py
|  |  └── socket_manager.py
|  ├── Dockerfile
|  └── requirements.txt
├── docker-compose.yml
├── frontend
|  ├── index.html
|  ├── main.js
|  ├── package-lock.json
|  ├── package.json
|  └── renderer.js
└── README.md
---

## 🔮 What's Next? (Future Roadmap)

This app is totally usable right now, but there's always room to grow. Future updates might include:

* [ ] **Export Chat:** A button to download your chat history as a PDF or Markdown file.
* [ ] **Custom Settings:** Letting users change AI models or adjust temperature directly from the UI.

---

## 🤝 Contributing & Feedback

If you find a bug, want to add a feature, or just want to fix a typo, feel free to fork the repo and submit a Pull Request! I’d love to see what you build on top of this.

If you like the project, give it a ⭐—it keeps the coding fuel burning!

Made with ❤️ and way too much coffee.
