from dotenv import load_dotenv
import os
import anthropic
import requests

load_dotenv()
NEWS_API = os.getenv('NEWS_API_KEY')
client = anthropic.Anthropic()

tools = [{
    'name': 'get_weather',
    'description': 'Get the current weather for a city, use this tool when user asks about weather.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'latitude': {
                'type': 'string',
                'description': 'Latitude of the city, e.g. 3.1412 for Kuala Lumpur'
            },
            'longitude': {
                'type': 'string',
                'description': 'Longitude of the city, e.g. 101.6865 for Kuala Lumpur'
            }
        },
        'required': ['latitude','longitude']
    }
},
{
    'name': 'get_news',
    'description': 'Get the top news headline by keyword of the country, use this tool when user ask about news.',
    'input_schema': {
        'type': 'object',
        'properties': {
            'country': {
                'type': 'string',
                'description': '2-letter ISO 3166-1 code of the country, e.g. us for USA'
            },
            'keyword': {
                'type': 'string',
                'description': 'Keyword of news to search for if user mentioned one, e.g. AI'
            }
        },
        'required': ['country']
    }
}]

def get_weather(latitude,longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
	"latitude": float(latitude),
	"longitude": float(longitude),
	"current": ["temperature_2m", "weather_code"],
}
    try:
        response = requests.get(url,params = params)
        response.raise_for_status()
        data = response.json()
        return f"temperature:{data['current']['temperature_2m']}, WMO weather code:{data['current']['weather_code']}"
    except Exception as e:
        print(f'Error: {e}')
        return None

def get_news(country,keyword):
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'country': country,
        'pageSize': 3
    }
    if keyword:
        params['q'] = keyword
    headers = {
        'Authorization': f'Bearer {NEWS_API}'
    }
    try:
        response = requests.get(url,params = params, headers = headers)
        response.raise_for_status()
        data = response.json()
        if data['articles']:
            return f"Article: {data['articles'][0].get('title','No article found')}"
        else:
            return 'No news found'
    except Exception as e:
        print(f'Error: {e}')
        return None
def run_with_tools(message):
    messages = [{'role': 'user', 'content': message}]
    response = client.messages.create(
        model = 'claude-haiku-4-5-20251001',
        max_tokens = 1024,
        tools = tools,
        messages = messages
    )
    if response.stop_reason == 'max_tokens':
        print('Max token reached, response is limited.')
    while response.stop_reason == 'tool_use':
        contents = []
        for cont in response.content:
            if cont.type == 'tool_use':
                data = None
                if cont.name == 'get_weather':
                    latitude = cont.input['latitude']
                    longitude = cont.input['longitude']
                    data = get_weather(latitude,longitude)
                elif cont.name == 'get_news':
                    country = cont.input['country']
                    keyword = cont.input.get('keyword','')
                    data = get_news(country,keyword)
                if data is None:
                    contents.append({
                        'type': 'tool_result',
                        'tool_use_id': cont.id,
                        'content': f'{cont.name} API unavailable',
                        'is_error': True
                    })
                else:
                    contents.append({
                        'type': 'tool_result',
                        'tool_use_id': cont.id,
                        'content' : data
                    })
        messages.append({'role': 'assistant', 'content': response.content})
        messages.append({'role': 'user', 'content': contents})

        response = client.messages.create(
            model = 'claude-haiku-4-5-20251001',
            max_tokens = 1024,
            tools = tools,
            messages = messages
            )

    
    return next((b.text for b in response.content if b.type == "text"), "No response")

def main():
    message = input('User: ')
    print(run_with_tools(message))

if __name__ == '__main__':
    main()