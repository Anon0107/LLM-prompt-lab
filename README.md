# LLM Prompt Lab

Prompt engineering experiments built during my AI engineering learning journey using Anthropic API.

## Tools
- Anthropic API — claude-haiku-4-5
- News API
- Open-Meteo API
- Python 3.11
- Environment variables required: see `.env.example`

## Day 1 — How LLMs Work + Temperature
**Experiment:** Same prompt at temperature 0.0 / 0.5 / 1.0, 5 runs each.  

**Findings:**   
Temperature = 0.0: same response every run.  
Temperature = 0.5: almost same response every run with 1-2 different respond each run.  
Temperature = 1.0: diverse response every run.  
Conclusion: More consistency for lower temperature, more creativity for higher temperature.  

## Day 2 — Prompt Engineering Techniques
**Overall:** Accurate system prompts to format and specify responses.  

**Experiment 1: XML tags**  
**Technique:** Tags in prompts to let Claude detect context blocks.  
**Findings:** Tags together with format specification contributes to a more consistent and desired response by Claude, error handling included when parsing JSON object to handle unintended code fences in response.  

**Experiment 2: Chain-of-Thought and Zero-Shot**  
**Technique:** CoT (with steps includedin prompt) vs no CoT (Zero-Shot).  
**Findings:** For insturctions such as a math problems with multiple solutions, CoT and no CoT both produces similar responses. Differences: the working for CoT is consistent,following the steps in the prompt but diverse for no CoT.  

**Experiment 3: Few-Shot**  
**Technique:** Example logic in prompts, 1 Example provided per class.  
**Findings:** 
Missing examples for some class: Claude inferred correctly 
using pretrained knowledge, not examples.  
1 Example for each class: Claude response correctly based on logic of given examples but rarely response with unknown class.  
Conclusion: minimum 1 example per class, 2 recommended when class boundaries are more ambiguous.  

## Day 3 — Tool Use and Multi-Tool Dispatch
**Experiment:** Multi-tool script where Claude dispatches to weather (Open-Meteo API) or news (NewsAPI) based on user query.  
**Technique:** Tool use loop, multi-tool response handling, and tool error handling.  
**Findings:** Claude ignores optional parameters when they are not relevant to the user query. Clearer parameter descriptions lead to more accurate tool calls. Passing `'is_error': True` in a tool result block causes Claude to acknowledge the failure and respond gracefully instead of hallucinating data.