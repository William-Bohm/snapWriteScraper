import os
import json
import pprint
import asyncio

import aiohttp
import dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def send_gemini_chat(
    session: aiohttp.ClientSession,
    messages: list,
    tools: list = None,
    model: str = "gemini-2.0-flash",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    top_p: float = 1.0,
):
    """
    Send a request to the Gemini LLM API 
    """
    api_key = os.getenv("GOOGLE_API_KEY")

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        url = f"{url}?key={api_key}"

        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "contents": messages,
            "generationConfig": {
                "temperature": temperature,
                "topP": top_p,
                "maxOutputTokens": max_tokens,
            }
        }

        if tools:
            payload["tools"] = tools
            payload["tool_config"] = None
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                print(f"Error response from Gemini API: {error_text}")
                response.raise_for_status()

            response_data = await response.json()
            return response_data

    except Exception as e:
        print(f"Error in Gemini API request: {str(e)}")
        raise


async def main():
    """Test the Gemini API functions"""
    dotenv.load_dotenv()
    
    # Sample message for testing
    messages = [
        {
            "role": "user",
            "parts": [
                {
                    "text": "Hello, can you tell me a short joke?"
                }
            ]
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        # Test non-streaming function
        response = await send_gemini_chat(session, messages)
        
        # Extract and print just the response text
        if response and "candidates" in response:
            text = response["candidates"][0]["content"]["parts"][0]["text"]
            print("\nJoke response:")
            print(text)
        else:
            print("No response from Gemini API")


if __name__ == "__main__":
    asyncio.run(main())
