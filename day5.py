import anthropic
import time
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

def get_message(messages):
    """
    Sends a list of messages to the Anthropic Claude model and returns the model's response text,
    along with the number of input and output tokens used.

    Args:
        messages (list): A list of message dictionaries to send to the model. Each dictionary
            should contain at least a 'role' and 'content' key.

    Returns:
        tuple: (response_text, input_token_count, output_token_count)
            - response_text (str): The AI model's response as text. Adds a truncation note if the
              response hit the max tokens limit.
            - input_token_count (int): The number of tokens input in the request.
            - output_token_count (int): The number of tokens output in the response.
    """
    response = client.messages.create(
                model = 'claude-haiku-4-5-20251001',
                system = 'You are a CLI chatbot that respond gracefully',
                max_tokens = 1024,
                messages = messages
            )
    
    input_token = response.usage.input_tokens
    output_token = response.usage.output_tokens
    result = next((b.text for b in response.content if b.type == 'text'),'No responses')
    return result,input_token,output_token

def stream_message(messages):
    """
    Streams the model's response to a list of messages using Anthropic Claude,
    printing each token as it arrives.

    Args:
        messages (list): A list of message dictionaries to send to the model. Each dictionary
            should contain at least a 'role' and 'content' key.

    Returns:
        tuple: (response_text, input_token_count, output_token_count)
            - response_text (str): The full AI model's response as combined text.
                If the response hits the max tokens limit, appends a truncation note.
            - input_token_count (int): The number of tokens input in the request.
            - output_token_count (int): The number of tokens output in the response.
    """
    print(f'Claude: ',end = '',flush = True)
    with client.messages.stream(
                model = 'claude-haiku-4-5-20251001',
                system = 'You are a CLI chatbot that respond gracefully',
                max_tokens = 1024,
                messages = messages
            ) as stream:
        for text in stream.text_stream:
            print(text, end ='', flush = True)
        print()
        message = stream.get_final_message()
        text = stream.get_final_text()

    input_token = message.usage.input_tokens
    output_token = message.usage.output_tokens
    if message.stop_reason == 'max_tokens':
        text = f'{text} (Max tokens reached, response truncated)'
    return text,input_token,output_token

def count_tokens(messages):
    """
    Counts the number of input tokens in a list of messages using the Anthropic Claude model.

    Args:
        messages (list): A list of message dictionaries to be counted. Each dictionary should include at least
            a 'role' and 'content' key.

    Returns:
        int: The number of input tokens for the given messages.
    """
    count = client.messages.count_tokens(
                model = 'claude-haiku-4-5-20251001',
                system ='You are a CLI chatbot that respond gracefully',
                messages = messages
    )
    return count.input_tokens
def main():
    total = 0
    sec_exp = 0
    max_retry = 5
    messages = []
    print('"Press ctrl+c or type quit to exit, type /help for list of commands"')
    while True:
        if sec_exp == 0:
            try:
                message = input('User: ')
                if message.startswith('/'):
                    if message == '/help':
                        print('Commands: /help /clear /cost')
                    elif message == '/clear':
                        messages = []
                    elif message == '/cost':
                        print(f'Total cost: ${total:.6f}')
                    else:
                        print(f'Unknown command {message}, type /help for list of commands')
                    continue
            except KeyboardInterrupt:
                break
            if message.strip() == 'quit':
                break
            if not message.strip():
                continue
        messages.append({'role':'user', 'content':message})  
        # Error handling
        try:
            if count_tokens(messages) > 500: #Token limit for conversation history
                # Compress history with a one line summary to limit token usage
                messages.pop()
                messages.append({'role':'user','content':'Summarize this conversation into a single concise message.Only respond with the message'})
                summary, input_tokens, output_tokens = get_message(messages)
                print('Compressing chat history...')
                cost = (input_tokens/1000000) * 1.00 + (output_tokens/1000000) * 5.00 # Token costs for Claude-Haiku
                total += cost
                print(f"\nInput_tokens: {input_tokens}, Output_tokens: {output_tokens}, Estimated cost: ${cost:.6f}, Total cost: ${total:.6f}\n")
                messages = [{'role':'user','content':f'Context summary: {summary}. {message}'}]
            reply, input_tokens, output_tokens = stream_message(messages)
        except anthropic.RateLimitError:
            if sec_exp >= max_retry:
                print('Max retries reached, exiting')
                break
            wait = min(2**sec_exp, 60) # Cap at 60s
            print(f'Too many requests, retrying in {wait}s')
            time.sleep(wait)
            sec_exp += 1
            messages.pop()
            continue
        except anthropic.AuthenticationError:
            print('Invalid or missing API key, check .env file')
            break
        except anthropic.InternalServerError:
            if sec_exp >= max_retry:
                print('Max retries reached, exiting')
                break
            wait = min(2**sec_exp, 60) # Cap at 60s
            print(f'Server too busy, retrying again in {wait}s')
            time.sleep(wait)
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
        cost = (input_tokens/1000000) * 1.00 + (output_tokens/1000000) * 5.00 # Token costs for Claude-Haiku
        total += cost
        print(f"\nInput_tokens: {input_tokens}, Output_tokens: {output_tokens}, Estimated cost: ${cost:.6f}, Total cost: ${total:.6f}\n")
        messages.append({'role':'assistant', 'content':reply}) # Add response to chat history to preserve context
    print('Exiting...')

if __name__ == '__main__':
    main()