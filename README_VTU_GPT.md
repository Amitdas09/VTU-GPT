# 🤖 VTU-GPT - A ChatGPT Clone Using Ollama & Streamlit

VTU-GPT is a custom, lightweight ChatGPT-style chatbot built using **Streamlit** and **Ollama**, powered by **LLaMA 3.2 3B model**. It supports multi-chat sessions, history management, real-time interactions, and export options—ideal for educational and personal AI use.

---

## 🚀 Features

- 💬 Real-time chat interface (ChatGPT-like UI)
- 🧠 Powered by local **LLaMA 3.2 3B** model via **Ollama**
- 🗂 Multi-chat sessions with history, titles, and timestamps
- 💾 Export individual or all chats to JSON
- 📊 Built-in statistics (total chats, messages, user vs. assistant count)
- ♻️ Reopen, rename, or delete past chats easily
- 🎨 Clean, responsive UI with Streamlit

---

## 🛠 Requirements

- Python 3.8+
- [Ollama](https://ollama.com) installed and running
- LLaMA 3.2 3B model downloaded:
  ```bash
  ollama pull llama3.2:3b
  ```
- Python packages:
  ```bash
  pip install streamlit
  ```

---

## ▶️ How to Run

1. Make sure **Ollama** is installed and running
2. Pull the required model:
   ```bash
   ollama pull llama3.2:3b
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run final.py
   ```
4. Visit `http://localhost:8501` in your browser

---

## 🧑‍💻 How It Works

- **Prompt Input** → Sent to `ollama run llama3.2:3b`
- **Response Handling** → Streamed or full output using `subprocess`
- **Session State** → Manages chat history, multiple chats, and UI status
- **Sidebar** → Controls for starting, switching, deleting, and exporting chats
- **Main Chat Area** → Shows user/assistant interaction in chat bubbles

---

## 💾 Export & Import

- Export **current chat** as JSON
- Export **all chats** together
- Saves include timestamps, roles, model info, and full conversation

---

## 📚 Example Prompts

- "Explain Python decorators with examples."
- "Summarize the water cycle for 5th-grade students."
- "Generate SQL query for joining two tables."

---

## ❗ Tips & Notes

- Make sure **Ollama is installed**: https://ollama.com
- Always pull the model before launching:
  ```bash
  ollama pull llama3.2:3b
  ```
- Use `Clear Chat` to reset your current conversation
- All chats are stored in memory until the app restarts

---

## 🧠 Powered By

- [Streamlit](https://streamlit.io)
- [Ollama](https://ollama.com)
- LLaMA 3.2 3B model

---

## 📜 License

MIT License © 2025 HKBK VTU-GPT Team