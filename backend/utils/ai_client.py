import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEEPSEEK_MODEL_NAME = os.getenv("DEEPSEEK_MODEL_NAME") # Ensure this is set in .env

if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not found in .env file. AI functionality will not work.")

if not DEEPSEEK_MODEL_NAME:
    print("Warning: DEEPSEEK_MODEL_NAME not found in .env file. AI functionality will not work.")

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1/chat/completions",
    api_key=OPENROUTER_API_KEY,
)

async def get_ai_response(prompt: str, text_content: str) -> str:
    """
    Sends a prompt and text content to the DeepSeek V3 API via OpenRouter 
    and returns the AI's response.
    """
    if not OPENROUTER_API_KEY:
        return "Error: OPENROUTER_API_KEY not configured."
    
    try:
        completion = await client.chat.completions.create(
            model=DEEPSEEK_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": text_content
                },
            ],
            # You can add other parameters here, like temperature, max_tokens, etc.
        )
        ai_message = completion.choices[0].message.content
        return ai_message if ai_message is not None else "Error: No content in AI response"
    except Exception as e:
        # Log the exception e
        print(f"Error calling OpenRouter API: {e}")
        return f"Error interacting with AI model: {e}"

async def identify_core_topics(text_content: str) -> str:
    """
    Uses the AI model to identify core topics and subtopics from the given text.
    """
    prompt = "You are an expert academic assistant. Your task is to analyze the provided text and extract the key concepts, core topics, and main subtopics. Present them in a clear, structured format. For example:\n\nCore Topic 1:\n  - Subtopic 1.1\n  - Subtopic 1.2\nCore Topic 2:\n  - Subtopic 2.1\n\nPlease process the following text:"
    return await get_ai_response(prompt, text_content)

async def rank_topics_by_frequency(notes_text: str, questions_text: str) -> str:
    """
    Uses the AI model to rank topics by frequency based on notes and question sets.
    """
    prompt = "You are an expert academic assistant. Analyze the provided notes and question set texts. Identify all topics and rank them by their frequency of mention across both texts. Present the ranked topics clearly, indicating their frequency or a relative ranking. For example:\n\n1. Topic A (High Frequency)\n2. Topic B (Medium Frequency)\n3. Topic C (Low Frequency)\n\nPlease process the following texts:"
    combined_text = f"Notes Content:\n{notes_text}\n\nQuestions Content:\n{questions_text}"
    return await get_ai_response(prompt, combined_text)