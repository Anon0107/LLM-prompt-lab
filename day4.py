import anthropic
import time
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

def get_message(messages):
    response = client.messages.create(
                model = 'claude-haiku-4-5-20251001',
                system = 'You are a CLI chatbot that respond gracefully',
                max_tokens = 1024,
                messages = messages
            )
    
    input_token = response.usage.input_tokens
    output_token = response.usage.output_tokens
    if response.stop_reason == 'max_tokens':
        result = next((f'{b.text} (Max tokens reached, response truncated)' for b in response.content if b.type == 'text'),'No responses')
    else:
        result = next((b.text for b in response.content if b.type == 'text'),'No responses')
    return result,input_token,output_token

def count_tokens(messages):
    count = client.messages.count_tokens(
                model = 'claude-haiku-4-5-20251001',
                system ='You are a CLI chatbot that respond gracefully',
                messages = messages
    )
    return count.input_tokens
def main():
    total = 0
    sec_exp = 0
    messages = []
    print('"Press ctrl+c or type quit to exit"')
    while True:
        if sec_exp == 0:
            try:
                message = input('User: ')
            except KeyboardInterrupt:
                break
            if message == 'quit':
                break
            if not message.strip():
                continue
        messages.append({'role':'user', 'content':message})  
        try:
            if count_tokens(messages) > 500:
                messages.pop()
                messages.append({'role':'user','content':'Summarize this conversation into a single concise message.Only respond with the message'})
                summary, input_tokens, output_tokens = get_message(messages)
                print('Compressing chat history...')
                cost = (input_tokens/1000000) * 1.00 + (output_tokens/1000000) * 5.00 
                total += cost
                print(f"\nInput_tokens: {input_tokens}, Output_tokens: {output_tokens}, Estimated cost: ${cost:.6f}, Total cost: ${total:.6f}\n")
                messages = [{'role':'user','content':f'Context summary: {summary}. {message}'}]
            reply, input_tokens, output_tokens = get_message(messages)
        except anthropic.RateLimitError:
            print(f'Too many requests, retrying in {2**sec_exp}s')
            time.sleep(2**sec_exp)
            sec_exp += 1
            messages.pop()
            continue
        except anthropic.AuthenticationError:
            print('Invalid or missing API key, check .env file')
            break
        except anthropic.InternalServerError:
            print(f'Server too busy, retrying again in {2**sec_exp}s')
            time.sleep(2**sec_exp)
            sec_exp += 1
            messages.pop()
            continue
        except anthropic.APIConnectionError:
            print('Bad connection, try again')
            sec_exp = 0
            messages.pop()
            continue
        except Exception as e:
            print(f'Unexpected error: {e}')
            break
        sec_exp = 0
        print(f'Claude: {reply}')
        cost = (input_tokens/1000000) * 1.00 + (output_tokens/1000000) * 5.00
        total += cost
        print(f"\nInput_tokens: {input_tokens}, Output_tokens: {output_tokens}, Estimated cost: ${cost:.6f}, Total cost: ${total:.6f}\n")
        messages.append({'role':'assistant', 'content':reply})
    print('Exiting...')

if __name__ == '__main__':
    main()