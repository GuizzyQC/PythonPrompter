# Python Prompter
# By: GuizzyQC

import argparse
import requests
import json
import os
import io
import sys
import re
import shlex 
import sseclient
import tiktoken

from bs4 import BeautifulSoup

printer_target = "/tmp/DEVTERM_PRINTER_IN"
max_text_length = 999999
banner = "*************************\nWelcome to PythonPrompter\n*************************\nType (quit) at the main prompt to exit\nType (search:search term) at the start of a prompt to feed search results\nType (continue) to continue previous answer\n"

default = dict()
history = []

parser = argparse.ArgumentParser(description='OpenAI API Prompter')
parser.add_argument('prompt', type=str, nargs="?",
                help='text to prompt the API with')
parser.add_argument('--url', type=str,
                help='enter OpenAI API address')
parser.add_argument('--api_key', type=str,
                help='enter OpenAI API key')
parser.add_argument('--enforce', action='store_true',
                help='force model loading')
parser.add_argument('--no_enforce', action='store_true',
                help='disable model loading')
parser.add_argument('--model', type=str,
                help='enter model to load')
parser.add_argument('--streaming', action='store_true',
                help='enable streaming')
parser.add_argument('--no_streaming', action='store_true',
                help='disable streaming')
parser.add_argument('--preset', type=str,
                help='enter preset to load')
parser.add_argument('--history', type=str,
                help='enter history file to save chats to')
parser.add_argument('--instruct_template', type=str,
                help='enter name of instruct template')
parser.add_argument('--searx_url', type=str,
                help='enter searx instance url')
parser.add_argument('--searx_api_key', type=str,
                help='enter searx instance api key')
parser.add_argument('--mode', choices=['instruct', 'chat'],
                help='select prompting mode')
parser.add_argument('--direct', action='store_true',
                help='skip settings and use defaults')
parser.add_argument('--character', type=str,
                help='enter character to prompt with')
parser.add_argument('--system', type=str,
                help='enter system prompt to use')
parser.add_argument('--search', type=str, action='append',
                help='enter search terms to find')
parser.add_argument('--max_tokens', type=int, choices=range(1, 200000),
                help='enter the maximum number of tokens in the context')
parser.add_argument('--max_urls', type=int, choices=range(1, 11),
                help='enter the number of search results or the maximum number of urls to read')
parser.add_argument('--printer', action='store_true', help=argparse.SUPPRESS)
parser.add_argument('rest', nargs=argparse.REMAINDER, help=argparse.SUPPRESS)

args = parser.parse_args()

default['url'] = os.environ.get("OPENAI_API_BASE") or "https://api.openai.com/v1"
default['api_key'] = os.environ.get("OPENAI_API_KEY") or ""
default['model'] = (os.environ.get("PYPROMPT_MODEL") or "n")
default['mode'] = (os.environ.get("PYPROMPT_MODE") or "instruct").lower()
default['preset'] = os.environ.get("PYPROMPT_PRESET") or "Divine Intellect"
default['instruct_template'] = os.environ.get("PYPROMPT_INSTRUCT_TEMPLATE") or ""
default['character'] = os.environ.get("PYPROMPT_CHARACTER") or ""
default['system'] = os.environ.get("PYPROMPT_SYSTEM") or "You are a helpful assistant, answer any request from the user."
default['enforce'] = (os.environ.get("PYPROMPT_ENFORCE_MODEL") or "n").lower()
default['streaming'] = (os.environ.get("PYPROMPT_STREAMING") or "n").lower()
default['history'] = (os.environ.get("PYPROMPT_HISTORY") or "n").lower()
default['searx_url'] = (os.environ.get("PYPROMPT_SEARX_URL") or "n").lower()
default['searx_api_key'] = (os.environ.get("PYPROMPT_SEARX_API_KEY") or "n")
default['max_urls'] = int(os.environ.get("PYPROMPT_MAX_URLS") or 1)
default['max_tokens'] = int(os.environ.get("PYPROMPT_MAX_TOKENS") or 15000)
default['printer'] = (os.environ.get("PYPROMPT_PRINTER") or "n").lower()


# This function takes an output string and an optional echo parameter (default is 1) and prints the output to the console if echo is True. If the parameter output_to_printer is set to 'y', it also sends the output to a printer specified by the printer variable using the os.system command. 
def output_result(string, output_to_printer=False, echo=True):
    if echo:
        print(string)
    if output_to_printer:
        printer_command = "echo " + shlex.quote(string)
        os.system(printer_command + " > " + printer_target)

# Hide a string for display, will only show the length of the string
def star(string):
    return ''.join('*' * len(string))

# This function starts the interface by printing the banner, displaying the current settings, and asking the user if they want to change the settings. 
# It returns a string indicating whether the user wants to change the settings or not. 
def start_interface(default):
    change_options = "y"
    os.system('cls||clear')
    print(banner)
    if str(default['url']) != "https://api.openai.com/v1" and str(default['api_key']) != "":
        print("Current settings:")
        print("API URL: " + str(default['url']))
        if str(default['api_key']) != "":
            print("API Key: " + str(star(default['api_key'])))
        print("Enforce model: " + str(default['enforce']))
        print("Streaming: " + str(default['streaming']))
        if str(default['enforce']) == "y":
            if str(default['model']) != "n":
                print("Model: " + str(default['model']))
        if str(default['history']) == "n":
            print("History file: Do not save conversation history")
        if str(default['history']) != "n":
            print("History file: " + str(default['history']))
        print("Mode: " + str(default['mode']))
        if str(default['instruct_template']) != "" and str(default['instruct_template']) != "n":
            print("Instruct template: " + str(default['instruct_template']))
        if str(default['mode']) == "chat":
            print("Character: " + str(default['character']))
        if str(default['mode']) == "instruct":
            print("System prompt: " + str(default['system']))
        if str(default['searx_url']) != "n":
            print("Searx instance URL: " + str(default['searx_url']))
            print("Number of search results to fetch: " + str(default['max_urls']))
        if os.path.exists(printer_target):
            print("\nDevterm thermal printer detected!")
            print("Printer toggle: " + str(default['printer']))
        answer = ""
        while answer != "y" and answer != "n":
            answer = str(input("\nEnter y to change the settings: ")) or "n"
        change_options = answer 
    return change_options

# This function clears the terminal screen and prints a banner. 
def reset_screen():
    if not args.prompt:
        os.system('cls||clear')
        print(banner)

# To summarize the behavior of this function in one line, it loads a model into the system by sending a POST request to the specified URL with the model's settings as JSON data in the request body. The function handles any exceptions that may occur during the request and prints an error message if there is a problem. 
def enforce_model(settings):
    try:
        response = requests.get(settings['url'] + "/internal/model/info", headers=settings['headers'], timeout=15, verify=True)
        answer_json = response.json()
        if answer_json["model_name"] != settings['model']:
            print(">>> Please be patient, changing model to " + str(settings['model']))
            data = {
                'model_name': settings['model'],
                'settings': { "preset": settings['preset'] }
                }
            response = requests.post(settings['url'] + "/internal/model/load", headers=settings['headers'], json=data, timeout=60, verify=True)
    except Exception as e:
        print(f"Error setting model: {str(e)}")

# This function generates an AI response based on the chat history and new question provided. It uses the given settings to determine the behavior of the AI. It first checks if the model is not set to "n" and enforces the model if necessary. Then, it creates a list of messages based on the chat history and new questions. Depending on the mode, it adds either a user or system message to the messages list. Finally, it sends a POST request to the URL with the data and headers, and returns the AI's response message. If there is an error during the process, it prints an error message.
def generate_ai_response(chat_history, prompt, settings, mode):
    messages = []
    try:
        if settings['model'] != "n":
            enforce_model(settings)
        if mode == "completion":
            data = {
                'stream': False,
                'max_tokens': 4096,
                'prompt': prompt,
            }
            response = requests.post(settings['url'] + "/completions", headers=settings['headers'], json=data, timeout=3600, verify=True)
            assistant_message = response.json()['choices'][0]['text']
        if mode == "chat":
            for question, answer in chat_history:
                messages.append({"role": "user", "content": question})
                messages.append({"role": "assistant", "content": answer})
            messages.append({"role": "user", "content": prompt})
            data = {
                'stream': False,
                'max_tokens': 4096,
                'messages': messages,
                'instruction_template': settings['instruct_template'],
                'mode': 'chat-instruct',
                'character': settings['character'],
            }
            response = requests.post(settings['url'] + "/chat/completions", headers=settings['headers'], json=data, timeout=3600, verify=True)
            assistant_message = response.json()['choices'][0]['message']['content']

        if mode == "instruct":
            messages.append({"role": "system", "content": settings['system']})
            messages.append({"role": "user", "content": prompt})
            data = {
                'stream': False,
                'mode': 'instruct',
                'instruction_template': settings['instruct_template'],
                'max_tokens': 4096,
                'messages': messages,
            }
            response = requests.post(settings['url'] + "/chat/completions", headers=settings['headers'], json=data, timeout=3600, verify=True)
            assistant_message = response.json()['choices'][0]['message']['content']
        return(assistant_message)
    except Exception as e:
        print(f"Error generating response: {str(e)}")

def generate_streaming_response(chat_history, prompt, settings, mode):
    messages = []
    if settings['model'] != "n":
        enforce_model(settings)
    if mode == "completion":
        data = {
            'stream': True,
            'max_tokens': 4096,
            'prompt': prompt,
        }
        response = requests.post(settings['url'] + "/completions", headers=settings['headers'], json=data, timeout=3600, verify=True, stream=True)
        client = sseclient.SSEClient(response)
        assistant_message = ""
        for event in client.events():
            payload = json.loads(event.data)
            chunk = payload['choices'][0]['text']
            assistant_message += chunk
            print(chunk, end='')
    if mode == "chat":
        for question, answer in chat_history:
            messages.append({"role": "user", "content": question})
            messages.append({"role": "assistant", "content": answer})
        messages.append({"role": "user", "content": prompt})
        data = {
            'stream': True,
            'max_tokens': 4096,
            'messages': messages,
            'mode': 'chat-instruct',
            'instruction_template': settings['instruct_template'],
            'character': settings['character'],
        }
        response = requests.post(settings['url'] + "/chat/completions", headers=settings['headers'], json=data, timeout=3600, verify=True, stream=True)
        client = sseclient.SSEClient(response)
        assistant_message = ""
        for event in client.events():
            payload = json.loads(event.data)
            chunk = payload['choices'][0]['message']['content']
            assistant_message += chunk
            print(chunk, end='')
    if mode == "instruct":
        messages.append({"role": "system", "content": settings['system']})
        messages.append({"role": "user", "content": prompt})
        data = {
            'stream': True,
            'mode': 'instruct',
            'instruction_template': settings['instruct_template'],
            'max_tokens': 4096,
            'messages': messages,
        }
        response = requests.post(settings['url'] + "/chat/completions", headers=settings['headers'], json=data, timeout=3600, verify=True, stream=True)
        client = sseclient.SSEClient(response)
        assistant_message = ""
        for event in client.events():
            payload = json.loads(event.data)
            chunk = payload['choices'][0]['message']['content']
            assistant_message += chunk
            print(chunk, end='')
    return(assistant_message)

# This function initializes settings for an application by prompting the user for input and using default values if specified. It returns a dictionary containing the settings. 
def initialize_settings(change_options, default):
    def generate_headers(api_key):
        headers = {
            "Content-Type": "application/json",
        }
        if (api_key != "" and api_key != " " and api_key != "none"):
            headers['Authorization'] = f"Bearer " + api_key
        return headers
    settings = dict()
    reset_screen()
    settings['url'] = ""
    settings['api_key'] = ""
    settings['headers'] = ""
    settings['model'] = ""
    settings['mode'] = ""
    settings['instruct_template'] = ""
    settings['system'] = ""
    settings['character'] = ""
    settings['streaming'] = False
    settings['preset'] = ""
    settings['searx_url'] = ""
    settings['searx_headers'] = ""
    settings['max_urls'] = 1
    settings['printer'] = False
    settings['history'] = ""
    if change_options == "n":
        settings['url'] = str(default['url'])
        settings['api_key'] = str(default['api_key'])
        settings['headers'] = generate_headers(settings['api_key'])
        if str(default['enforce']) == "y":
            settings['model'] = str(default['model'])
        else:
            settings['model'] = "n"
        settings['preset'] = str(default['preset'])
        settings['mode'] = str(default['mode'])
        settings['instruct_template'] = str(default['instruct_template'])
        if settings['mode'] == "chat":
            settings['character'] = str(default['character'])
        if settings['mode'] == "instruct":
            settings['system'] = str(default['system'])
        settings['history'] = str(default['history'])
        settings['searx_url'] = str(default['searx_url'])
        settings['searx_api_key'] = str(default['searx_api_key'])
        if settings['searx_api_key'].lower() == 'n':
            settings['searx_api_key'] = ''
        else:
            settings['searx_headers'] = generate_headers(settings['searx_api_key'])
        settings['max_urls'] = default['max_urls']
        settings['max_tokens'] = default['max_tokens']
        if str(default['streaming']) == "y":
            settings['streaming'] = True
        if os.path.exists(printer_target):
            if str(default['printer']) == "y":
                settings['printer'] = True
    if change_options == "y":
        settings['url'] = str(input("Enter the endpoint (empty for default: " + str(default['url']) + "): ") or default['url'])
        reset_screen()
        if str(default['api_key']) != "":
            settings['api_key'] = str(input("Enter the api key (empty for default): ") or default['api_key'])
        else:
            settings['api_key'] = str(input("Enter the api key: ") or default['api_key'])
        settings['headers'] = generate_headers(settings['api_key'])
        reset_screen()
        try:
            response = requests.get(settings['url'] + "/internal/model/info", headers=settings['headers'], timeout=2, verify=True)
            answer_json = response.json()
            print("Currently loaded model: " + answer_json["model_name"])
        except:
            print("Endpoint did not respond to model info request")
        while settings['model'] != "n" and settings['model'] != "y":
            settings['model'] = str(input("Enter y if you want to run another model than currently loaded (empty for no): ") or "n")
        if settings['model'] == "y":
            try:
                response = requests.get(settings['url'] + "/internal/model/list", headers=settings['headers'], timeout=5, verify=True)
                print("Available models:")
                answer_json = response.json()
                i = 0 
                model_table = {}
                for name in answer_json["model_names"]:
                    model_table[i] = name
                    print(str(i) + ": " + name)
                    i = i + 1
            except Exception as e:
                print(f"Error fetching available models: {str(e)}")
            if str(default['model']) == "n":
                selected_model = input("\nEnter the number of the model to run (empty to keep currently loaded model): ")
            else:
                if default['model'] != "":
                    selected_model = input("\nEnter the number of the model to run (empty for default: " + str(default['model']) + "): ")
            if (selected_model):
                settings['model'] = model_table[int(selected_model)]
            else:
                settings['model'] = str(default['model'])
            reset_screen()
            settings['preset'] = str(input("Enter the preset to use (empty for default: " + str(default['preset']) + "): ") or default['preset'])
        reset_screen()
        while settings['mode'] != "chat" and settings['mode'] != "instruct":
            if default['mode'] != "chat" and default['mode'] != "instruct":
                settings['mode'] = str(input("Enter the the mode to run in, either chat or instruct: ")).lower()
            else:
                settings['mode'] = str(input("Enter the the mode to run in, either chat or instruct (empty for " + str(default['mode']) + "): ") or str(default['mode'])).lower()
        reset_screen()
        while settings['instruct_template'] == "":
            settings['instruct_template'] = str(input("Enter the instruct template to use (empty for default: " + str(default['instruct_template']) + "): ") or default['instruct_template'])
        reset_screen()
        while settings['mode'] == "chat" and settings['character'] == "":
            settings['history'] = str(input("Enter the history filename to load from and save history to, or n to not save (empty for default: " + str(default['history']) + "): ") or default['history'])
            reset_screen()
            if default['character'] == "":
                settings['character'] = str(input("Enter the character to embody: "))
            else:
                settings['character'] = str(input("Enter the character to embody (empty for default: " + str(default['character']) + "): ") or str(default['character']))
        if settings['mode'] == "instruct":
            settings['system'] = str(input("Enter the base system prompt to use (empty for default: " + str(default['system']) + "): ") or str(default['system']))
        reset_screen()
        settings['searx_url'] = str(default['searx_url'])
        reset_screen()
        settings['searx_api_key'] = str(default['searx_api_key'])
        if (settings['searx_api_key'].lower() == 'n' or settings['searx_api_key'] == ''):
            settings['searx_headers'] = ''
        else:
            settings['searx_headers'] = generate_headers(settings['searx_api_key'])
        reset_screen()
        settings['max_urls'] = int(default['max_urls'])
        settings['max_tokens'] = int(default['max_tokens'])
        reset_screen()
        answer = ""
        while answer != "y" and answer != "n":
            answer = str(input("Enter y to enable streaming (empty for default: " + str(default['streaming']) +"): ") or str(default['streaming'])).lower()
        if answer == "y":
            settings['streaming'] = True
        else:
            settings['streaming'] = False
        reset_screen()
        if os.path.exists(printer_target):
            answer = ""
            while answer != "y" and answer != "n":
                answer = str(input("Enter y to enable the printer (empty for default: " + str(default['printer'] +"): ")).lower() or str(default['printer'])).lower()
            if answer == "y":
                settings['printer'] = True
            else:
                settings['printer'] = False
    if len(sys.argv)==1:
        os.system('cls||clear')
        output_result(banner, settings['printer'])
    return settings

def extract_url(prompt):
    url = ""
    # Regular expression to match URLs
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    # Find all URLs in the text
    urls = re.findall(url_pattern, prompt.lower())
    return urls

def trim_to_x_words(prompt, limit):
    rev_rs = []
    words = prompt.split(" ")
    rev_words = reversed(words)
    for w in rev_words:
        rev_rs.append(w)
        limit -= 1
        if limit <= 0:
            break
    rs = reversed(rev_rs)
    return " ".join(rs)

def expand_url(url):
    text = f"The web page at {url} doesn't have any useable content. Sorry."
    try:
        response = requests.get(url, timeout=5)
        print("Fetched " + str(url))
    except:
        return f"The page {url} could not be loaded"
    soup = BeautifulSoup(response.content, "html.parser")
    paragraphs = soup.find_all("p")
    if len(paragraphs) > 0:
        text = "\n".join(p.get_text() for p in paragraphs)
        text = f"\n\n---\n\nContent of {url} : \n{trim_to_x_words(text, max_text_length)}[...]"
    else:
        text = f"The web page at {url} doesn't seem to have any readable content."
        metas = soup.find_all("meta")
        for m in metas:
            if "content" in m.attrs:
                try:
                    if (
                        "name" in m
                        and m["name"] == "page-topic"
                        or m["name"] == "description"
                    ):
                        if "content" in m and m["content"] != None:
                            text += f"It's {m['name']} is '{m['content']}'"
                except:
                    pass
    return text

def write_history(text, file):
    f=open(file,'w+')
    json.dump(text, f)

def read_history(file):
    f=open(file,'r')
    history = json.load(f)
    return history

def trim_to_max_tokens(string, maximum, reverse=False):
    def count_token(string):
        token_counter = tiktoken.get_encoding("cl100k_base")
        return len(token_counter.encode(string))
    if count_token(string) > maximum:
        print("Context too long, truncating context")
        print("Original context: " + str(count_token(string)))
        while count_token(string) > maximum:
            step = 100
            if (count_token(string) - maximum) > 10000:
                step = 10000
            if (count_token(string) - maximum) > 100000:
                step = 10000
            if (count_token(string) - maximum) > 300000:
                step = 100000
            new_length = len(string) - step
            if reverse:
                string = string[new_length:]
            else:
                string = string[:new_length]
        print("New context: " + str(count_token(string)))
    return string


def search_routine(string, settings, direct=False):
    def search_string(search_term, settings):
        def html_table_to_text(html_string):
            soup = BeautifulSoup(html_string, 'html.parser')
            tables = soup.find_all('table')
            rows = []
            text = ""
            for table in tables:
                for row in table.find_all('tr'):
                    row_text = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                    rows.append(row_text)
            for row in rows:
                    text = text + " ".join(row) + "\n"
            return text

        print("Searching for " + search_term + "...")
        r = requests.get(settings['searx_url'], params={'q': search_term,'format': 'json','pageno': '1'}, headers=settings['searx_headers'], timeout=30, verify=True)
        new_context = ""
        try:
            searchdata = r.json()
            resultsdata = searchdata['results']
            infodata = searchdata['infoboxes']
            answerdata = searchdata['answers']
        except: 
            new_context = "Could not find the results asked for"
        try:
            if resultsdata[0]['url']:
                i = 0
                while i < settings['max_urls']:
                    if resultsdata[i]['engine'] == "meilisearch":
                        print("Found " + str(resultsdata[i]['title']) + " on local Meilisearch instance")
                        new_context = new_context + "Contents of " + str(resultsdata[i]['title']) + ":\n" + str(resultsdata[i]['content']) + "\n"
                    else:
                        print("Found " + str(resultsdata[i]['url']))
                        if str(resultsdata[i]['url']).endswith('.pdf'):
                            response = requests.get(resultsdata[i]['url'])
                            with io.BytesIO(response.content) as pdf_file:
                                read_pdf = PyPDF2.PdfFileReader(pdf_file)
                                number_of_pages = read_pdf.getNumPages()
                                p = 0
                                while p < number_of_pages:
                                    page = read_pdf.pages[p]
                                    text = text + "\n\n\n" + page.extractText()
                        else:
                            new_context = new_context + expand_url(resultsdata[i]['url']) + "\n"
                    i = i + 1
        except:
            pass
        try:
            if infodata[0]['infobox']:
                i = 0
                while i < settings['max_urls']:
                    print("Found " + str(infodata[i]['infobox']))
                    new_context = new_context + "Information in HTML format: " + trim_to_x_words(html_table_to_text(str(infodata[i]['content'])), max_text_length) + "\n"
                    i = i + 1
        except:
            pass
        try:
            if answerdata[0]['answer']:
                i = 0
                while i < settings['max_urls']:
                    print("Found " + str(answerdata[i]['answer']))
                    new_context = new_context + "Answer found online: " + trim_to_x_words(str(answerdata[i]['content']), max_text_length) + "\n"
                    i = i + 1
        except:
            pass
        if new_context == "":
            new_context = "Could not find the results asked for"
        return trim_to_max_tokens(new_context, settings['max_tokens'])
    if direct:
        return str("\nHere is information about " + string + " found online: " + search_string(string, settings))
    else:
        interfering_symbols = ['\"', '\'']
        commands = ['search']
        marker = ['for']
        lowstr = string.lower()
        for s in interfering_symbols:
            lowstr = lowstr.replace(s, '') 
        if any(command in lowstr for command in commands) and any(case in lowstr for case in marker):
            print("Found search term")
            try:
                instruction = string.split('search',1)[0]
                search_command = string.split('search',1)[1]
            except:
                instruction = string.split('Search',1)[0]
                search_command = string.split('Search',1)[1]
            subject = search_command.split('for',1)[1].lstrip()
            return str(instruction + "\nHere is information about " + subject + " found online: " + search_string(subject, settings))
        else:
            return string

def argument_parsing(new_default):
    boolkeys = ['enforce', 'streaming']
    antiboolkeys = ['no_enforce', 'no_streaming']
    for key in new_default:
       if args.__getattribute__(key):
            try:
                new_default[key] = args.__getattribute__(key)
            except:
                pass
    for key in boolkeys:
        if args.__getattribute__(key):
            new_default[key] = "y"
    for key in antiboolkeys:
        if key == 'no_enforce':
            if args.__getattribute__(key):
                new_default['enforce'] = "n"
        if key == 'no_streaming':
            if args.__getattribute__(key):
                new_default['streaming'] = "n"
    return new_default

if args.prompt:
    settings = initialize_settings("n", argument_parsing(default))

    user_message = ""
    url = ""
    if settings['mode'] == "chat":
        if settings['history'] != "n":
            try:
                history = read_history(settings['history'])
            except:
                pass
    user_message = args.prompt
    if args.rest:
        for arg in args.rest:
            user_message = user_message + " " + arg

    extracted_urls = extract_url(user_message)
    if len(extracted_urls) > 0:
        i = 0
        for url in extracted_urls:
            if i < settings['max_urls']:
                user_message = user_message + "\n" + expand_url(url)
            i = i + 1
    else:
        if settings['searx_url'] != "n":
            user_message = search_routine(user_message, settings)
    if args.search:
        for s in args.search:
            user_message = user_message + search_routine(s, settings, True)
    if settings['streaming']:
        assistant_message = generate_streaming_response(history, user_message, settings, settings['mode'])
    else:
        assistant_message = generate_ai_response(history, user_message, settings, settings['mode'])
    if settings['mode'] == "chat":
        history.append((user_message, assistant_message))
        if settings['history'] != "n":
            write_history(history,settings['history'])
    if settings['streaming']:
        output_result(assistant_message, settings['printer'], False)
    else:
        output_result(assistant_message, settings['printer'])

if not args.prompt:
# This code initializes the user interface, retrieves the user's settings, and resets the screen. 

    if args.direct:
        reset_screen()
        settings = initialize_settings("n", argument_parsing(default))
    else:
        change_options = start_interface(argument_parsing(default))
        settings = initialize_settings(change_options, argument_parsing(default))

    if settings['history'] != "n":
        try:
            history = read_history(settings['history'])
        except:
            pass
    reset_screen()

    # This code snippet is a simple chatbot that takes user input, generates an AI response, and outputs the result. It continues to do so indefinitely until the program is terminated. The chatbot stores the conversation history if the mode is set to "chat". 
    while True:
        user_message = input("> ")
        if user_message == "(quit)":
            sys.exit()
        if user_message == "(continue)":
            if settings['streaming']:
                assistant_message = generate_streaming_response([], previous_message + "\n" + assistant_message, settings, "completion")
                print("\n")
            else:
                assistant_message = generate_ai_response([], previous_message + "\n" + assistant_message, settings, "completion")
                print("\n")
        else:
            output_result(str("> " + user_message + "\n\n"), settings['printer'], False)
            extracted_urls = extract_url(user_message)
            if len(extracted_urls) > 0:
                i = 0
                for url in extracted_urls:
                    if i < settings['max_urls']:
                        user_message = user_message + "\n" + expand_url(url)
                    i = i + 1
            else:
                if settings['searx_url'] != "n":
                    if ("(search:" in user_message and ")" in user_message):
                        search_terms = re.findall(r"(?<=\(search:)(.*?)(?=\))", user_message)
                        user_message = user_message.rsplit(")",1)[1] 
                        for s in search_terms:
                            user_message = user_message + search_routine(s, settings, True)
                    else:
                        user_message = search_routine(user_message, settings)

            if settings['streaming']:
                assistant_message = generate_streaming_response(history, user_message, settings, settings['mode'])
                print("\n")
            else:
                assistant_message = generate_ai_response(history, user_message, settings, settings['mode'])
        if settings['mode'] == "chat":
            history.append((user_message, assistant_message))
        if settings['streaming']:
            output_result(assistant_message, settings['printer'], False)
        else:
            output_result(assistant_message, settings['printer'])
        if settings['history'] != "n" and settings['history'] != "":
            write_history(history,settings['history'])
        previous_message = user_message
