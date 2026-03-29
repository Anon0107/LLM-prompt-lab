import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

def get_msg(temp):
    message = client.messages.create(
        model = 'claude-haiku-4-5-20251001',
        max_tokens = 1024,
        system = 'You are a philosopher that respond only 1 word, DO NOT prose, DO NOT explain',
        temperature = temp,
        messages = [{
            'role':'user',
            'content':'Define the meaning of life in one word'
        }]
    )
    return message.content[0].text
# Prompts with different temperatures
def main():
    temps = [0,0.5,1]
    for temp in temps:
        print(f'Temperature: {temp}')
        for i in range(5):
            data = get_msg(temp)
            print(f'{i+1}) {data}')

main()
