## Description:
An OpenAI-compatible API client for the command line

When invoked without arguments, will open an interface for sending prompt to an OpenAI-compatible API. When invoked with an argument, will send prompt directly to the API and respond with the answer.

Compatible and tested on Linux and Windows.

Detects and supports the DevTerm's printer to make wee thermal paper printouts of your prompts if you want.

Caution: Tested with Oobabooga's text-generation-webui, not tested with another OpenAI-compatible API, including OpenAI itself.

## Requirements:
Python 3

Libraries: tiktoken, requests, sseclient and BeautifulSoup4

## Installation:
git clone https://github.com/GuizzyQC/PythonPrompter

pip install -r PythonPrompter/requirements.txt

## Configuration:
The software is configured using environmental variables. You can either supply them to your command before launching it or save them in your command line shell's profile.

Here's what the environmental variables are and do:

OPENAI_API_BASE: Sets your API's endpoint. Defaults to "https://api.openai.com/v1". Note that I have never tested this with openai, it holds no interest for me. But in theory it should probably be compatible if you supply an API key.

OPENAI_API_KEY: Sets your API key.

PYPROMPT_ENFORCE_MODEL: Choose "y" or "n" to define whether you want the software to force the API endpoint to use another model than is currently running on it, useful for text-generation-webui which exposes multiple possible models.

PYPROMPT_MODEL: Sets the model used by your endpoint of you set y to PYPROMPT_ENFORCE_MODEL, useful for text-generation-webui which exposes multiple possible models.

PYPROMPT_PRESET: Sets the preset used by your endpoint, provided you are enforcing the model. Useful for text-generation-webui which exposes multiple possible presets. Defaults to "Divine Intellect"

PYPROMPT_MODE: Sets whether to use "chat" mode or "instruct" mode. Defaults to "instruct"

PYPROMPT_CHARACTER: Sets the name of the character to interact with in "chat" mode. Make sure this character exists.

PYPROMPT_SYSTEM: Sets the "system" prompt used in "instruct" mode. Defaults to a boring but multipurpose: "You are a helpful assistant, answer any request from the user."

PYPROMPT_HISTORY: If you want to save and load a conversation history in chat mode, this is where you would set it; write a full path that you have write access to. If you enter "n" it will not save history between sessions. Defaults to "n".

PYPROMPT_PRINTER: If you are the lucky owner of a DevTerm, setting "y" here will enable printouts on the thermal printer. Defaults to "n".

Setting variables in Bash can be done with the command:
``` bash
export PYPROMPT_MODEL=Nous-Capybara-34b.Q5_K_M-GGUF
```

And in Powershell with:
``` powershell
[System.Environment]::SetEnvironmentVariable('PYPROMPT_MODEL','Nous-Capybara-34b.Q5_K_M-GGUF')
```
You can set them permanently in \~/.bashrc for a Linux bash shell or $PROFILE on Windows.

## Command-line options:
usage: pyprompt.py [-h] [--mode {instruct,chat}] [--character CHARACTER] [--system SYSTEM] [--search SEARCH] [prompt]

OpenAI API Prompter

positional arguments:
  prompt                text to prompt the API with

options:
  -h, --help            show this help message and exit
  --mode {instruct,chat}
                        select prompting mode
  --character CHARACTER
                        enter character to prompt with
  --system SYSTEM       enter system prompt to use
  --search SEARCH       enter search terms to find

## Usage:
python pyprompt.py
or
python pyprompt.py Tell me a story about a brave sick girl
or
python pyprompt.py --mode chat Hi! What's your name?
or
python pyprompt.py --mode instruct --system "You are a helpful AI" Give me step-by-step instructions to put caramel at the center of a candy chocolate bar.

## Recommendation:
For Powershell, I recommend setting the variables in your profile and making a function to invoke the command. To accomplish this in Powershell, you can add this to your $PROFILE:
``` powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_BASE','https://api.openai.com/v1')
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY','')
[System.Environment]::SetEnvironmentVariable('PYPROMPT_MODE','instruct')
[System.Environment]::SetEnvironmentVariable('PYPROMPT_SYSTEM','You are a helpful assistant, helping the user accomplish any task on their computer.')
[System.Environment]::SetEnvironmentVariable('PYPROMPT_CHARACTER','')
[System.Environment]::SetEnvironmentVariable('PYPROMPT_ENFORCE_MODEL','y')
[System.Environment]::SetEnvironmentVariable('PYPROMPT_MODEL','Nous-Capybara-34b.Q5_K_M-GGUF')
function Call-AI { C:\Users\YOURUSER\AppData\Local\Programs\Python\Python311\python.exe C:\PATH\TO\PythonPrompter\pyprompt.py $args }
```
Making sure of course to change the variables and that the path to your Python interpreter is correct and the path to pyprompt.py is correct.
