from tenacity import retry, stop_after_attempt, wait_exponential
from config import llm_mistral, llm_gemini

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True 
)
def call_mistral(messages):
    response = llm_mistral.invoke(messages)
    return response.content

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True 
)
def call_gemini(messages):
    response = llm_gemini.invoke(messages)
    return response.content

def invoke_with_fallback(messages, fallback=None):
    try:
        return call_mistral(messages)
    except Exception as e:
        print(f"Mistral failed: {type(e).__name__}: {e}")
    
    try:
        return call_gemini(messages)
    except Exception as e:
        print(f"Gemini failed: {type(e).__name__}: {e}")
    
    return fallback