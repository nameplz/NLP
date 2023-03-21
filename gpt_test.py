import openai

API_KEY = input("Your api key")
model = 'gpt-3.5-turbo'

def GPT(query, API_KEY=API_KEY):
    
    # set api key
    openai.api_key = API_KEY

    messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]

    # Call the chat GPT API
    response = openai.ChatCompletion.create(
        model = model,
        messages = messages
    )
    return response['choices'][0]['message']['content']


def main():
    query = input("Insert a prompt: ")
    print(GPT(query).strip())

if __name__ == '__main__':
    main()