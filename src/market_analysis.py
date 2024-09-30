import os
import re
import math
import string
import pandas as pd
import nltk
import openai
import textwrap
from io import open
from decimal import Decimal
from openai import OpenAI
from datetime import datetime, timedelta

# Download NLTK data
nltk.download('punkt', quiet=True)

def print_plain_text(chat_completion_message, line_width=120):
    paragraphs = chat_completion_message.content.split('\n\n')
    for paragraph in paragraphs:
        wrapped_lines = textwrap.wrap(paragraph, width=line_width)
        for line in wrapped_lines:
            formatted_line = re.sub(r'\*\*(.*?)\*\*', r'\033[1m\1\033[0m', line)
            formatted_line = re.sub(r'\*(.*?)\*', r'\033[3m\1\033[0m', formatted_line)
            if formatted_line.strip().startswith("- "):
                formatted_line = re.sub(r'^- (.*)$', r'\033[1m•\033[0m \1', formatted_line)
            elif re.match(r'^\d+\. ', formatted_line):
                formatted_line = re.sub(r'^(\d+)\. (.*)$', r'\033[1m\1.\033[0m \2', formatted_line)
            print(formatted_line)
    clean_text = re.sub("<[^>]*>", "", chat_completion_message.content).strip()
    return clean_text

def calculate_daily_usage(client):
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=1)
    
    usage = client.get_usage(start_date=start_date, end_date=end_date)
    total_tokens = sum(data.n_generated_tokens_total + data.n_context_tokens_total for data in usage.data)
    
    used_balance_in_dollars = (total_tokens * 0.002) / 1000
    return used_balance_in_dollars

def count_tokens_generic(input_string):
    tokens = nltk.word_tokenize(input_string)
    return len(tokens)

def trim_tokens_nltk(input_string, max_tokens=10000):
    tokens = nltk.word_tokenize(input_string)
    if len(tokens) > max_tokens:
        trimmed_tokens = tokens[:max_tokens]
        input_string = ' '.join(trimmed_tokens)
        estimated_tokens = count_tokens_generic(input_string)
        print(f"\nEstimated number of tokens after trimming: {estimated_tokens}")
    return input_string

def load_data(filename):
    with open(filename, 'r') as f:
        dataset = f.read()
    return dataset

def upload_file():
    print('Please select a dataset file for upload and analysis:')
    file_name = input("Enter the file path: ")
    
    if file_name.lower().endswith(('.txt', '.text')):
        return load_data(file_name)
    elif file_name.lower().endswith(('.xlsx', '.csv')):
        df = pd.read_excel(file_name) if file_name.lower().endswith('.xlsx') else pd.read_csv(file_name)
        print('\nDo you want to consider a single column of the dataset?')
        trim_data_bool = input('Type "yes" if you want to choose a single column, and "no" if you wish to use the entire dataset: ').lower()
        
        if trim_data_bool == 'yes':
            print('Please type the title of the column you wish to consider for analysis:')
            single_feature = input()
            if single_feature in df.columns:
                df = df[single_feature]
                print(f"\nDataset uploaded and column '{single_feature}' is selected for analysis.")
            else:
                print(f"\n'{single_feature}' is not found in the column titles of the dataset. \nTherefore, entire dataset uploaded and ready for analysis.")
        else:
            print("Entire dataset uploaded and ready for analysis.")
        
        text_data = df.to_string(index=False)
        estimated_tokens = count_tokens_generic(text_data)
        print(f"\nEstimated number of tokens: {estimated_tokens}")
        return text_data
    else:
        print("Unsupported file format. Please upload a .txt, .xlsx, or .csv file.")
        return None

def main_loop(client, chat_history_file, dataset):
    prompts_and_outputs = {}
    
    print('\n' + '-'*120 + '\n')
    print("User Guide")
    print('1) Please type your prompt to ask questions about the dataset.')
    print('2) You can use "q", "quit", or "exit" commands to stop the code from asking for prompts.')
    print('3) If asked for deleting the previous chat history or not, typing "yes" will delete it and then the model')
    print('   will not consider previous chat data in its answers. Otherwise, type "no" for using the previous chat data.')
    print('   (These words are case-sensitive)')
    print('\n' + '-'*120 + '\n')
    
    if os.path.exists(chat_history_file):
        user_input = input("Previous chat history exists. Do you want to delete it? (yes/no): ").lower()
        if user_input == 'yes':
            open(chat_history_file, 'w').close()
            print("Existing chat history deleted.")
            chat_history_string = ""
        else:
            with open(chat_history_file, 'r') as f:
                chat_history_string = ''.join(f.readlines())
            print("Existing chat history loaded.")
    else:
        open(chat_history_file, 'w').close()
        chat_history_string = ""
        print('chat_history.txt created to save the conversation history.')
    
    print('\n' + '-'*120 + '\n')
    
    while True:
        with open(chat_history_file, 'r') as f:
            chat_history_string = ''.join(f.readlines())
        
        user_prompt = input('Prompt: ')
        print('\n' + '-'*120 + '\n')
        
        if user_prompt.lower() in ['exit', 'q', 'quit']:
            daily_usage = calculate_daily_usage(client)
            if daily_usage is not None:
                print(f"Used balance in dollars for today: ${daily_usage:.6f}")
            break
        
        system_role = f"You are a market analyzer that reviews all of the text provided to you which may include customer feedbacks and reviews, sales data, price data, etc from a business. Then you should analyze that business, it's strength and weaknesses, analyzes the market and the gaps and needs in that market. Then having that data in memory, wait for the user prompt to analyze the business in the provided data according to the user prompt. \nHere is the provided data: \n{dataset}. Also, here is the chat history so far: {chat_history_string}."
        user_role = f"Here is the prompt: \n{user_prompt}."
        
        completion = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_role}
            ]
        )
        
        print('Analyzers Output: \n')
        prompt_output = print_plain_text(completion.choices[0].message)
        print('\n' + '-'*120 + '\n')
        
        prompts_and_outputs[user_prompt] = prompt_output
        
        with open(chat_history_file, 'a') as f:
            f.write(f'Prompt: {user_prompt}\nAnswer: {prompt_output}\n')

if __name__ == "__main__":
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        api_key = input("Please enter your OpenAI API key: ")
    
    client = OpenAI(api_key=api_key)
    chat_history_file = "chat_history.txt"
    
    dataset = upload_file()
    if dataset:
        dataset = trim_tokens_nltk(dataset)
        main_loop(client, chat_history_file, dataset)
    else:
        print("No dataset loaded. Exiting.")