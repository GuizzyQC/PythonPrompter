import requests
import json
import os

global default_url, default_api_key, default_model, default_mode, default_character, default_system

default_url = os.environ.get("OPENAI_API_BASE")
default_api_key = os.environ.get("OPENAI_API_KEY")
default_model = os.environ.get("OPENAI_API_MODEL")
default_mode = os.environ.get("OPENAI_API_MODE") or "chat"
default_character = os.environ.get("OPENAI_API_CHARACTER")
default_system = os.environ.get("OPENAI_API_SYSTEM") or "You are a helpful assistant, answer any request from the user."
printer = "/tmp/DEVTERM_PRINTER_IN"

history = []
banner = "*************************\nWelcome to PythonPrompter\n*************************\n\n\nYou can press Ctrl-C at any time to exit\n\n\n"


def output_result(output, echo=1):
    if echo:
        print(output)
    if enable_printer == "y":
        printer_command = "echo \"" + output + "\""
        os.system(printer_command + " > " + printer)

def start_interface():
    global enable_printer
    enable_printer = ""
    if os.path.exists(printer):
        print("Devterm thermal printer detected!\n")
        while enable_printer != "y" and enable_printer != "n":
            enable_printer = str(input("Enter y to enable the printer: ")) or "n"
    os.system('cls||clear')
    output_result(banner)
    change_options = "y"
    if str(default_url) != "None" and str(default_model) != "None" and str(default_mode) != "None":
        print("Current settings:")
        print("API URL: " + str(default_url))
        print("API Key: " + str(default_api_key))
        print("Model: " + str(default_model))
        print("Mode: " + str(default_mode))
        if str(default_mode) == "chat":
            print("Character: " + str(default_character))
        if str(default_mode) == "instruct":
            print("System prompt: " + str(default_system))
        answer = ""
        while answer != "y" and answer != "n":
            answer = str(input("\nEnter y to change the settings: ")) or "n"
        change_options = answer 
    return change_options

def reset_screen():
    os.system('cls||clear')
    print(banner)

def enforce_model(settings):
    try:
        response = requests.get(settings['url'] + "/internal/model/info", headers=settings['headers'], verify=True)
        answer_json = response.json()
        if answer_json["model_name"] != settings['model']:
            print(">>> Please be patient, changing model to " + str(settings['model']))
            data = {
                'model_name': settings['model'],
                'settings': { "preset": "Divine Intellect", "custom_stopping_strings": '\"</s>\"' }
            }
            response = requests.post(settings['url'] + "/internal/model/load", headers=settings['headers'], json=data, verify=True)
    except Exception as e:
        print(f"Error setting model: {str(e)}")

def generate_ai_response(chat_history, new_question, settings):
    try:
        enforce_model(settings)
        messages = []
        if settings['mode'] == "chat":
            for question, answer in chat_history:
                messages.append({"role": "user", "content": question})
                messages.append({"role": "assistant", "content": answer})
            messages.append({"role": "user", "content": new_question})
            data = {
                'stream': False,
                'messages': messages,
                'mode': 'chat',
                'character': settings['character'],
                'max_tokens': 2000,
                'temperature': 0.75
            }
        if settings['mode'] == "instruct":
            messages.append({"role": "system", "content": settings['system']})
            messages.append({"role": "user", "content": new_question})
            data = {
                'stream': False,
                'messages': messages,
                'max_tokens': 2000,
                'temperature': 0.75
            }
        response = requests.post(settings['url'] + "/chat/completions", headers=settings['headers'], json=data, verify=True)
        assistant_message = response.json()['choices'][0]['message']['content']
        return(assistant_message)
    except Exception as e:
        print(f"Error generating response: {str(e)}")


def initialize_settings(change_options, default_url, default_api_key, default_model, default_mode, default_character, default_system):
    def generate_headers(api_key):
        headers = {
            "Content-Type": "application/json",
        }
        headers['Authorization'] = f"Bearer " + api_key
        return headers
    settings = dict();
    reset_screen()
    settings['url'] = "None"
    if change_options == "n":
        settings['url'] = str(default_url)
    while settings['url'] == "None":
        settings['url'] = str(input("Enter the endpoint (empty for default: " + str(default_url) + "): ") or default_url)
        reset_screen()
    if change_options == "n":
        settings['api_key'] = str(default_api_key)
    else:
        settings['api_key'] = str(input("Enter the api key (empty for default: " + str(default_api_key) + "): ") or default_api_key)
    settings['headers'] = generate_headers(settings['api_key'])

    reset_screen()

    if change_options == "n":
        settings['model'] = str(default_model)
    else:
        try:
            response = requests.get(settings['url'] + "/internal/model/list", headers=settings['headers'], verify=True)
            print("Available models:")
            answer_json = response.json()
            i = 0 
            model_table = {}
            for name in answer_json["model_names"]:
                model_table[i] = name
                i = i + 1
            i = 0
            for entries in model_table:
                if (i >= 0):
                    print(str(i) + ": " + model_table[i])
                i = i + 1
        except Exception as e:
            print(f"Error fetching available models: {str(e)}")

        selected_model = input("\nEnter the number of the model to run (empty for default: " + str(default_model) + "): ")
        if (selected_model):
            settings['model'] = model_table[int(selected_model)]
        else:
            settings['model'] = str(default_model)
    reset_screen()
    if change_options == "n":
        settings['mode'] = str(default_mode)
    else:
        settings['mode'] = ""
        while settings['mode'] != "chat" and settings['mode'] != "instruct":
            settings['mode'] = str(input("Enter the the mode to run in, either chat or instruct (empty for " + str(default_mode) + "): ") or str(default_mode)).lower()
        settings['character'] = ""
    reset_screen()
    if settings['mode'] == "chat":
        if change_options == "n":
            settings['character'] = str(default_character)
        else:
            settings['character'] = str(input("Enter the character to embody (empty for default: " + str(default_character) + "): ") or str(default_character))
    if settings['mode'] == "instruct":
        if change_options == "n":
            settings['system'] = str(default_system)
        else:
            settings['system'] = str(input("Enter the base system prompt to use (empty for default: " + str(default_system) + "): ") or str(default_system))

    return settings

change_options = start_interface()
settings = initialize_settings(change_options, default_url, default_api_key, default_model, default_mode, default_character, default_system)
reset_screen()

while True:
    user_message = input("> ")
    output_result(str("> " + user_message + "\n\n"), 0)
    assistant_message = generate_ai_response(history, user_message, settings)
    if settings['mode'] == "chat":
        history.append((user_message, assistant_message))
    output_result(assistant_message)
