from tenacity import retry, stop_after_attempt, wait_exponential
from config import llm_mistral, llm_gemini
import logging 


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True 
)
def call_mistral(messages):
    logger.info(f"Calling Mistral with messages: {messages}")
    response = llm_mistral.invoke(messages)
    logger.info(f"Mistral response: {response.content}")
    return response.content

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True 
)
def call_gemini(messages):
    logger.info(f"Calling Gemini with messages: {messages}")
    response = llm_gemini.invoke(messages)
    logger.info(f"Gemini response: {response.content}")
    return response.content

def invoke_with_fallback(messages, fallback=None):
    try:
        return call_mistral(messages)
    except Exception as e:
        logger.error(f"Mistral failed: {type(e).__name__}: {e}")
    
    try:
        return call_gemini(messages)
    except Exception as e:
        logger.error(f"Gemini failed: {type(e).__name__}: {e}")

    logger.warning(f"Both LLM models unavailable, returning fallback response")
    return fallback

def invoke_with_fallback_tracked(messages, fallback=None):
    try:
        return call_mistral(messages), "mistral"
    except Exception as e:
        logger.error(f"Mistral failed: {type(e).__name__}: {e}")
    
    try:
        return call_gemini(messages), "gemini"
    except Exception as e:
        logger.error(f"Gemini failed: {type(e).__name__}: {e}")

    logger.warning(f"Both LLM models unavailable, returning fallback response")
    return fallback, "fallback"