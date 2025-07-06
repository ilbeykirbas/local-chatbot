
# Local Chatbox (Ollama + CustomTkinter)

This project is a modern Python application that allows you to chat with a local large language model (LLM) through a graphical user interface. The chatbot communicates with models like *Mistral*, *Phi*, *LLaMA2*, and *Gemma* using the [Ollama](https://ollama.com/) backend. The GUI is built with `customtkinter`.

---

## Features

- **Local model usage:** Chat with models running directly on your machine.
- **Theme and color customization:** Choose from Light/Dark/System themes and color schemes.
- **Set system role:** Define chatbot behavior via a system prompt.
- **Chat history logging:** All messages are saved to a `chat_log.txt` file.
- **Typing indicator:** Displays a "Typing..." message if response is delayed.
- **Model selection:** Choose the model to use via dropdown.

---

## Installation

### 1. Requirements

- Python 3.10+
- Ollama (Install from: https://ollama.com/download)

### 2. Install Python dependencies

```bash
pip install customtkinter requests
```

---

## Usage

### 1. Start a model in Ollama (e.g., mistral):

```bash
ollama run mistral
```

> If the model is not available locally, it will be downloaded automatically.

### 2. Run the GUI:

```bash
python chatbot_gui.py
```

### 3. Interface Overview:

- Type your message and press **Enter** or click **Send**.
- Change themes and color schemes using the dropdowns at the top.
- Use the system prompt field to assign a custom role to the bot.

---

## File Structure

```
project/
│
├── chatbot_gui.py         # Main Python script
├── config/
│   ├── settings.json      # Stores user theme preferences
│   └── chat_log.txt       # Chat history
```

---

## Supported Models

- `mistral`
- `phi`
- `llama2`
- `gemma`

> Make sure to pull these models in Ollama:

```bash
ollama pull phi
ollama pull gemma
```

---

## Notes

- The `Bot: Typing...` message only appears if the response is delayed (500ms+).
- Some GUI color theme changes may require restarting the application.

---

## License

This project is licensed under the MIT License. Feel free to use and modify it.

---

## Author

Developed by İlbey Kırbaş  
GitHub: [@ilbeykirbas](https://github.com/ilbeykirbas)
