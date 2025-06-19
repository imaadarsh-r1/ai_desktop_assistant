import os
import subprocess
import pyscreenshot as ImageGrab
import tkinter as tk
from tkinter import scrolledtext
from langchain_community.llms import LlamaCpp

# Since i m using the mac so i have to simulate the function keys to reduce/increase the brightness
def increase_brightness():
    subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 144'])
    return "Tried increasing brightness."

def decrease_brightness():
    subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 145'])
    return "Tried decreasing brightness."

def take_screenshot():
    os.makedirs("screenshots", exist_ok=True)
    path = "screenshots/screenshot.png"
    im = ImageGrab.grab()
    im.save(path)
    return f"Screenshot saved to {path}."

# loading Phi-2 model (locally) approximately 1.7GB
llm = LlamaCpp(
    model_path="models/phi-2.Q4_K_M.gguf",
    n_ctx=1024,
    n_threads=4,
    temperature=0.3,
    verbose=False
)

# Here the Main role of LLM: to classify the user input into three categories and i haved used few shot learning method to make the LLM model to learn the thing without an additional fine tuning the instructions
def classify_and_generate(user_input):
    prompt = f"""
You are a helpful desktop AI assistant.

You can perform ONLY these actions:
- increase_brightness
- decrease_brightness
- take_screenshot

Your job:
1. Read the user's input
2. Select one of the valid actions
3. Respond in this EXACT format:

Action: <action_name>
Reply: <friendly message>

Examples:

User: "Can you make my screen brighter?"
Action: increase_brightness
Reply: Sure, I increased the brightness for you!

User: "Dim the screen."
Action: decrease_brightness
Reply: Got it, I decreased the brightness.

User: "Take a screenshot."
Action: take_screenshot
Reply: I’ve taken a screenshot and saved it.

Now respond to this:
User: "{user_input}"
Action:"""

    try:
        response = llm.invoke(prompt).strip()
        print(f"[DEBUG] LLM Raw Response:\n{response}")

        action = None
        reply = None

        for line in response.splitlines():
            if line.lower().startswith("action:"):
                action = line.split(":", 1)[1].strip().lower()
            elif line.lower().startswith("reply:"):
                reply = line.split(":", 1)[1].strip()

        if action in ["increase_brightness", "decrease_brightness", "take_screenshot"] and reply:
            return action, reply

        return "unknown", "Sorry, I couldn't understand that clearly."
    except Exception as e:
        print(f"[ERROR] LLM failed: {str(e)}")
        return "unknown", "Sorry, something went wrong."
    


#fallback matching
def fallback_classify(user_input):
    text = user_input.lower()
    if "bright" in text or ("increase" in text or "up" in text or "more" in text or "make" in text):
        return "increase_brightness", "Sure, I increased the brightness for you!"
    elif "bright" in text or ("decrease" in text or "less" in text or "dim" in text or "down" in text):
        return "decrease_brightness", "Okay, I dimmed the screen."
    elif "screenshot" in text or "screen shot" in text or "capture" in text:
        return "take_screenshot", "Screenshot has been taken!"
    return "unknown", "Sorry, I couldn't understand what to do."



#Main logic and function calling happens based on the LLM(Agent) tool selection
def route_and_respond(user_input):
    intent, reply = classify_and_generate(user_input)
    if intent not in ["increase_brightness", "decrease_brightness", "take_screenshot"]:
        intent, reply = fallback_classify(user_input)
    if intent == "increase_brightness":
        _ = increase_brightness()
    elif intent == "decrease_brightness":
        _ = decrease_brightness()
    elif intent == "take_screenshot":
        _ = take_screenshot()
    else:
        return "Sorry, I didn't understand that command."
    return reply

#tkinter set up
def send_input():
    user_input = entry.get()
    if not user_input.strip():
        return
    chatbox.insert(tk.END, f"You: {user_input}\n")
    reply = route_and_respond(user_input)
    chatbox.insert(tk.END, f"Assistant: {reply}\n\n")
    entry.delete(0, tk.END)

root = tk.Tk()
root.title("AI Desktop Assistant")
root.geometry("600x400")

chatbox = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
chatbox.pack(padx=10, pady=10)
chatbox.insert(tk.END, "Hi Adarsh, How can i help you today.\n\n")

entry = tk.Entry(root, width=60)
entry.pack(padx=10, pady=(0, 10))
entry.bind("<Return>", lambda event: send_input())

send_button = tk.Button(root, text="Send", command=send_input)
send_button.pack()

root.mainloop()