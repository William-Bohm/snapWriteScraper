import json
from typing import List, Dict, Any, Tuple
import aiohttp
from pydantic import BaseModel

from utils.geminiLLMService import send_gemini_chat

# Define Pydantic models for validation
class SearchTerms(BaseModel):
    short: str
    medium: str
    long: str

class ProductOutput(BaseModel):
    input_name: str
    brand: str
    model_no: str
    search_terms: SearchTerms

class ProductInput(BaseModel):
    name: str

async def process_products_with_llm(products: List[Dict[str, str]]) -> List[ProductOutput]:
    """Process products with the LLM to get structured search data."""
    # Create prompt for the LLM
    prompt = """
You are an expert at extracting structured information from product names and creating optimal search terms.

For each product name I provide, extract the following information and return it as JSON:
1. Brand name (lowercase)
2. Model number
3. Three search terms of varying length:
   - long: Comprehensive but without model number
   - medium: Moderate length focusing on key features
   - short: Very brief (2-4 words) with brand and key attributes

Important:
- DO NOT include the model number in any search term
- Keep all search terms lowercase
- Focus on what would work well in e-commerce search bars
- Return ONLY valid JSON with no additional text or explanation

Here's an example:

INPUT:
{ "name": "Hisense 50\" 4K Smart Google AI Upscaler LED TV - 50A68N" }

OUTPUT:
{
  "input_name": "Hisense 50\" 4K Smart Google AI Upscaler LED TV - 50A68N",
  "brand": "hisense",
  "model_no": "50A68N",
  "search_terms": {
    "short": "hisense 50 4k",
    "medium": "hisense 50 4k smart tv",
    "long": "hisense 50 inch 4k smart google ai upscaler led tv"
  }
}

Now process the following product list and return a JSON array with each product processed:
"""
    
    # Prepare messages for LLM
    messages = [
        {
            "role": "user",
            "parts": [
                {
                    "text": prompt + json.dumps(products)
                }
            ]
        }
    ]
    
    # Call the LLM
    async with aiohttp.ClientSession() as session:
        response = await send_gemini_chat(
            session=session, 
            messages=messages,
            temperature=0.2,  # Lower temperature for more deterministic results
            max_tokens=4096   # Ensure enough tokens for all products
        )
    
    # Extract and parse the response
    if response and "candidates" in response:
        response_text = response["candidates"][0]["content"]["parts"][0]["text"]
        
        # The LLM might wrap the JSON in ```json and ``` markers, so we need to extract just the JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        try:
            processed_data = json.loads(response_text)
            
            # Validate with Pydantic
            validated_products = []
            for item in processed_data:
                validated_product = ProductOutput(
                    input_name=item["input_name"],
                    brand=item["brand"],
                    model_no=item["model_no"],
                    search_terms=SearchTerms(
                        short=item["search_terms"]["short"],
                        medium=item["search_terms"]["medium"],
                        long=item["search_terms"]["long"]
                    )
                )
                validated_products.append(validated_product)
            
            return validated_products
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response text: {response_text}")
            return []
        except Exception as e:
            print(f"Error validating data: {e}")
            return []
    else:
        print("No valid response from LLM")
        return []


async def process_and_validate_products(products: List[Dict[str, str]]) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Process products with LLM and return validated results.
    
    Args:
        products: List of product dictionaries with 'name' key
        
    Returns:
        Tuple containing:
        - List of validated product dictionaries
        - Boolean indicating success
    """
    # Process products with LLM
    processed_products = await process_products_with_llm(products)
    
    # Print processing results
    if not processed_products:
        print("Failed to process products.")
        return [], False
    
    print(f"Successfully processed {len(processed_products)} products:")
    
    # Show examples of processed products (first 2)
    # for i, product in enumerate(processed_products[:2], 1):
    #     print(f"\nProduct {i}:")
    #     print(json.dumps(product.model_dump(), indent=2))
    
    # if len(processed_products) > 2:
    #     print(f"\n... and {len(processed_products) - 2} more products processed.")
    
    # Convert to dictionaries for easier handling
    validated_products = [p.model_dump() for p in processed_products]
    
    return validated_products, True
