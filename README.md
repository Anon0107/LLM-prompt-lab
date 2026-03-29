# LLM Prompt Lab

Prompt engineering experiments built during my AI engineering learning journey using Anthropic API.

## Tools
- Anthropic API — claude-haiku-4-5
- Python 3.11

## Day 1 — How LLMs Work + Temperature
**Experiment:** Same prompt at temperature 0.0 / 0.5 / 1.0, 5 runs each.  

**Finding:** 
-Temperature = 0.0: same response every run.  
-Temperature = 0.5: almost same response every run with 1-2 different respond each run.  
-Temperature = 1.0: diverse response every run.  
-Conclusion: More consistency for lower temperature, more creativity for higher temperature.  

## Day 2 — Prompt Engineering techniques
**Overall:** Accurate system prompts to format and specify responses.  

**Experiment 1: XML tags**  
**Technique:** Tags in prompts to let Claude detect context blocks.  
**Finding:** Tags together with format specification contributes to a more consistent and desired response by Claude, error handling included when parsing JSON object to handle unintended code fences in response.  

**Experiment 2: Chain-of-Thought and Zero-Shot**  
**Technique:** CoT(with steps includedin prompt) vs no CoT(Zero-Shot)  
**Finding:** For insturctions such as a math problems with multiple solutions, CoT and no CoT both produces similar responses. Differences: the working for CoT is consistent,following the steps in the prompt but diverse for no CoT.  

**Experiment 3: Few-Shot**  
**Technique:** Example logic in prompts, 1 Example provided per class  
**Finding:** 
-Missing examples for some class: Claude inferred correctly 
using pretrained knowledge, not examples.  
-1 Example for each class: Claude response correctly based on logic of given examples but rarely response with unknown class  
-Conclusion: minimum 1 example per class, 2 recommended when class boundaries are more ambiguous.  