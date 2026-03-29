import anthropic
from dotenv import load_dotenv
from pprint import pprint
import json

load_dotenv()
client = anthropic.Anthropic()
# CoT prompts
print('Responses with CoT')
for i in range(5):
    message = client.messages.create(
        model = 'claude-haiku-4-5-20251001',
        max_tokens = 1024,
        temperature = 1.0,
        system = 'You are a mathematician that respond direct answers. Respond according to the logic in steps given. No prose, no explanation, do not wrap output in markdown code fences.',
        messages = [{
            'role': 'user',
            'content': """<instructions>
            A store sells apples for RM2 each and oranges for RM3 each.
            Ali buys some fruits and pays RM24 total.
            He bought more apples than oranges.
            How many of each did he buy?
            Solve this step by step as shown
            </instructions>
            <steps>
            1)Let apple be a, orange be o
            2)compute possible a and o for 2a + 3o = 24
            3)Find combinations where a > o
            4)state your final answer in <answer> tags
            </steps>

            """
        }]
    )
    result = message.content[0].text.strip()
    print(f'{i+1})\n{result}')
# No shots prompts
print('Responses without CoT (no shots)')
for i in range(5):
    message = client.messages.create(
        model = 'claude-haiku-4-5-20251001',
        max_tokens = 1024,
        temperature = 1.0,
        system = 'You are a mathematician that respond direct answers. No prose, no explanation, do not wrap output in markdown code fences.',
        messages = [{
            'role': 'user',
            'content': """
            A store sells apples for RM2 each and oranges for RM3 each.
            Ali buys some fruits and pays RM24 total.
            He bought more apples than oranges.
            How many of each did he buy?

            """
        }]
    )
    result = message.content[0].text.strip()
    print(f'{i+1})\n{result}')
# Few shots prompts
print('Responses with few shots')
def checktone(sentance):
    message = client.messages.create(
        model = 'claude-haiku-4-5-20251001',
        max_tokens = 1024,
        system = """You are a tone analyser that analyses tone of a sentance base on the logic in 
        given examples, respond only a valid JSON object,DO NOT explain,DO NOT prose, DO NOT wrap answer in
        markdown code fences""",
        messages = [{
            'role':'user',
            'content':f"""<instructions>
            Analyse the tone of this sentance: {sentance}, respond only a valid JSON object 
            using the logic in examples in this format
            ,
            {"{'tone':}"}</instructions>
            <examples>
            1) Hey wassup, wanna go out for lunch later? -> casual
            2) Do that again and i'm going to confiscate your phone. -> aggresive
            Otherwise -> formal
            </examples>
        """}]
    )
    result = message.content[0].text
    return result
    
sentances = ["I would like to formally request a meeting at your earliest convenience.",
             "yo wanna grab lunch later lol",
             "If you don't fix this now, there will be consequences.",
             "Please find attached the report for your review.",
             "bro that's actually insane haha"]
for sentance in sentances:
    data = checktone(sentance)
    try:
        tone = json.loads(data)
        print('JSON parse success')
        print(f'Sentance: {sentance}')
        pprint(tone) 
    except Exception as e:
        print(f'JSON parse fail: {e}')
        print(f'Sentance: {sentance}')
        print(data)

# XML tags prompts
print('responses with XML tags')
message = client.messages.create(
    model = 'claude-haiku-4-5-20251001',
    max_tokens = 1024,
    system = 'You are a data extraction API. Respond with only valid JSON. DO NOT prose, DO NOT, DO NOT respond markdown code fences.',
    messages = [{
        'role': 'user',
        'content': """<news_article>
        KUALA LUMPUR, March 29 — Malaysian tech startup Mereka announced yesterday 
        that it has secured RM12 million in Series A funding led by Vertex Ventures. 
        The company, founded in 2021 by Ahmad Zaki and Priya Nair, plans to expand 
        its upskilling platform to Indonesia and Thailand by Q3 2026. CEO Ahmad Zaki 
        said the funds will also be used to double their engineering headcount from 
        40 to 80 by year end.</news_article>
        <instructions>
        Extract company, funding amount, funding round, lead investor, founded year, founders, 
        expansion targets, expansion timeline, current headcount and target headcount from this
        news article.Respond only a JSON object in the given format,no other text,store values in list for a key with Multiple
        values </instructions>
        <format>
                {
        "company":,
        "funding_amount":,
        "funding_round":,
        "lead_investor":,
        "founded_year":,
        "founders":,
        "expansion_targets":,
        "expansion_timeline":,
        "headcount_current":,
        "headcount_target":
        }
        </format>
        """
    }]
)
result = message.content[0].text
try:
    data = result.json.loads()
    pprint(data)
except Exception as e:
    print(f'JSON parse fail: {e}')
    print(result)
