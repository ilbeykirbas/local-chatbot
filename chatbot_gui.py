import os
import json
import threading
import customtkinter as ctk
from tkinter import messagebox
import requests

class ChatbotGUI:
    def __init__(self):
        appearance, color = self.load_settings()
        ctk.set_appearance_mode(appearance)
        ctk.set_default_color_theme(color)

        self.history = []
        self.model = "mistral"

        self.window = ctk.CTk()
        self.window.title("Local Chatbox")
        self.window.geometry("600x600")

        self.options_frame = ctk.CTkFrame(self.window)
        self.options_frame.pack(pady=10)        

        # Theme selection
        ctk.CTkLabel(self.options_frame, text="Select Theme:", font=("Arial", 13, "bold")).pack(pady=(10, 0))
        self.theme_var = ctk.StringVar(value=appearance)
        theme_menu = ctk.CTkOptionMenu(
            self.options_frame,
            variable=self.theme_var,
            values=["System", "Light", "Dark"],
            command=self.change_appearance # Callback on selection
        )
        theme_menu.pack()

        # Color Theme Selection
        ctk.CTkLabel(self.options_frame, text="Select Color Theme:", font=("Arial", 13, "bold")).pack(pady=(5, 0))
        self.color_var = ctk.StringVar(value=color)
        ctk.CTkOptionMenu(
            self.options_frame,
            variable=self.color_var,
            values=["blue", "green", "dark-blue"],
            command=self.change_color_theme
        ).pack()

        # Model selection
        ctk.CTkLabel(self.options_frame, text="Select Model:", font=("Arial", 13, "bold")).pack(pady=(5, 0))
        self.model_var = ctk.StringVar(value="mistral")
        model_options = ["mistral", "phi", "llama2", "gemma"] # Supported models
        self.model_menu = ctk.CTkOptionMenu(self.options_frame, variable=self.model_var, values=model_options)
        self.model_menu.pack()

        # Assign a role
        ctk.CTkLabel(self.window, text="System prompt:", font=("Arial", 13, "bold")).pack()
        self.system_entry = ctk.CTkEntry(self.window)
        self.system_entry.pack(padx=10, pady=(0, 10), fill="x")
        self.system_entry.insert(0, "You are a helpful assistant.")

        # Chat box (history)
        self.chat_area = ctk.CTkTextbox(self.window, wrap="word", font=("Arial", 12))
        self.chat_area.pack(padx=10, pady=10, fill="both", expand=True)
        self.chat_area.configure(state="disabled")

        # Input box
        self.input_entry = ctk.CTkEntry(self.window, placeholder_text="Type your message...")
        self.input_entry.pack(padx=10, pady=(0, 10), fill="x")
        self.input_entry.bind("<Return>", self.send_message)

        # Send button
        self.send_button = ctk.CTkButton(self.window, text="Send", command=self.send_message)
        self.send_button.pack(pady=(0, 10))

        self.window.mainloop()

    def change_appearance(self, selected):
        ctk.set_appearance_mode(selected) 
        self.save_settings(selected, self.color_var.get())

    def change_color_theme(self, selected):
        # May require a reboot to take effect
        self.save_settings(self.theme_var.get(), selected)
        messagebox.showinfo("Info", "Color theme applied. Please restart the app to fully see the changes.")

    def send_message(self, event=None):
        # If the history is empty and the user wrote a system prompt, add
        if not self.history:
            system_prompt = self.system_entry.get().strip()
            if system_prompt:
                self.history.append({"role": "system", "content": system_prompt})
            else:
                self.system_entry.insert(0, "You are a helpful assistant.")

        user_input = self.input_entry.get().strip()

        if not user_input:
            return
        
        self.display_message("You", user_input)
        self.input_entry.delete(0, "end")
        
        self.history.append({"role": "user", "content": user_input})

        # Run the response handler in a seperate thread
        threading.Thread(target=self.stream_response, daemon=True).start()
    
    def stream_response(self):
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": self.model_var.get(),
                    "messages": self.history,
                    "stream": True
                }
                ,stream=True
            )
            response.raise_for_status()

            self.typing_timer = self.window.after(500, self.append_typing_message)
            
            # Show Bot tag
            self.window.after(0, self.append_bot_label)

            partial = ""
            first_token = True
            for line in response.iter_lines():
                if line:
                    if first_token:
                        self.window.after_cancel(self.typing_timer)
                        self.remove_typing_message()
                        first_token = False
                    try:
                        data = json.loads(line.decode("utf-8"))
                        token = data.get("message", {}).get("content", "")
                        partial += token
                        self.window.after(0, self.append_token_to_chat, token)
                    except Exception as parse_err:
                        continue    # skip malformed chunks

            self.window.after(0, lambda: self.append_token_to_chat("\n\n"))

            self.history.append({"role": "assistant", "content": partial}) 

        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Error", str(e)))

    def append_bot_label(self):
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", "Bot: ")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")
    
    def append_token_to_chat(self, token):
        self.chat_area.configure(state='normal')
        self.chat_area.insert("end", token)
        self.chat_area.configure(state='disabled')
        self.chat_area.see("end")

    def append_typing_message(self):
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", "Bot: Typing...\n")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")

    def remove_typing_message(self):
        self.chat_area.configure(state='normal')
        start = self.chat_area.search("Bot: Typing...", "1.0", "end")
        if start:
            line_start = f"{start} linestart"
            line_end = f"{start} lineend+1c"
            self.chat_area.delete(line_start, line_end)
        self.chat_area.configure(state='disabled')
        
    def display_message(self, sender, message):
        self.chat_area.configure(state="normal")
        self.chat_area.insert("end", f"{sender}: {message}\n\n")
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end") # Auto scroll
        self.log_message(sender, message) 

    def log_message(self, sender, message):
        os.makedirs("config", exist_ok=True)
        with open("config/chat_log.txt", "a", encoding="utf-8") as file:
            file.write(f"{sender}: {message}\n\n")

    def save_settings(self, appearance, color_theme):
        os.makedirs("config", exist_ok=True)
        with open("config/settings.json", "w") as f:
            json.dump({
                "appearance": appearance,
                "color_theme": color_theme
            }, f, indent=4)

    def load_settings(self):
        try:
            with open("config/settings.json", "r") as f:
                settings = json.load(f)
                return settings.get("appearance", "System"), settings.get("color_theme", "blue")
        except FileNotFoundError:
            return "System", "blue"  # Default values

if __name__ == "__main__":
    ChatbotGUI()
