import dotenv
import asyncio
import pprint
from utils.llmFunctions import process_and_validate_products
from scrapers.bestBuy import BestBuyScraper

dotenv.load_dotenv()

# List of input products
Products = [
  { "name": "Hisense 50\" 4K Smart Google AI Upscaler LED TV - 50A68N" },
  { "name": "Hisense 55\" 4K Smart Google AI Upscaler LED TV - 55A68N" },
  { "name": "Samsung 75\u201d 4K Tizen Smart CUHD TV - UN75DU7100FXZC" },
  { "name": "LG 50\" UHD 4K Smart LED TV - 50UT7570PUB" },
  { "name": "Samsung 65\u201d 4K Tizen Smart QLED TV - QN65Q60DAFXZC" },
  { "name": "Hisense 32\" HD Smart VIDAA LED TV - 32A4KV" },
  { "name": "Samsung 43\u201d 4K Tizen Smart CUHD TV-UN43DU7100FXZC" },
  { "name": "LG 65\" UHD 4K Smart LED TV - 65UT7570PUB" },
  { "name": "Samsung 75\u201d 4K Tizen Smart QLED TV - QN75Q60DAFXZC" },
  { "name": "Samsung 65\u201d Neo QLED 4K Tizen Smart TV QN85D - QN65QN85DBFXZC" },
  { "name": "LG 65\" 4K Smart evo C4 OLED TV - OLED65C4PUA" },
  { "name": "LG 86\" UHD 4K Smart LED TV - 86UT7590PUA" },
  { "name": "SONY 75\" X77L 4K HDR LED TV Google TV - KD75X77L" },
  { "name": "LG 55\" QNED80 4K Smart QLED TV - 55QNED80TUC" },
  { "name": "Samsung 65\u201d OLED 4K Tizen Smart TV S90D - QN65S90DAFXZC" },
  { "name": "Samsung 75\u201d 4K Tizen Smart QLED TV - QN75Q80DAFXZC" },
  { "name": "Samsung 65\u201d 4K Tizen Smart QLED TV - QN65Q80DAFXZC" },
  { "name": "Samsung 65\u201d 4K Tizen Smart CUHD TV - UN65DU7100FXZC" },
  { "name": "Samsung 75\u201d 4K Tizen Smart CUHD TV - UN75DU8000FXZC" }, 
]

def scrape_bestbuy_products(validated_products, max_products=18, headless=True):
    """
    Scrape Best Buy for product information using the validated products data
    
    Args:
        validated_products: List of products with brand, model_no, and search terms
        max_products: Maximum number of products to scrape (to limit runtime)
        headless: Whether to run the browser in headless mode
        
    Returns:
        Dictionary of results keyed by model number
    """
    print("\nScraping Best Buy for product information...")
    
    # Create a dictionary of search terms to model numbers for batch processing
    # Use the medium search term for each product
    search_model_pairs = {}
    
    # Limit to max_products if specified
    products_to_process = validated_products[:max_products] if max_products else validated_products
    
    for product in products_to_process:
        model_no = product.get('model_no')
        search_term = product.get('search_terms', {}).get('medium')
        
        if model_no and search_term:
            search_model_pairs[search_term] = model_no
    
    # Initialize the scraper and perform batch search
    scraper = BestBuyScraper(headless=headless, use_delays=True)
    
    try:
        # Perform the batch search
        results = scraper.batch_search(search_model_pairs)
        
        # Enhance results with original product data
        enhanced_results = {}
        for model_no, product_data in results.items():
            # Find the original product info
            original_product = next((p for p in validated_products if p.get('model_no') == model_no), {})
            
            if product_data:
                # Combine the scraper results with original product info
                enhanced_results[model_no] = {
                    "bestbuy_data": product_data,
                    "original_info": original_product
                }
            else:
                enhanced_results[model_no] = {
                    "bestbuy_data": None,
                    "original_info": original_product
                }
        
        return enhanced_results
    finally:
        # Ensure the scraper is closed properly
        scraper.close()

async def main():
    """Main entry point for the application."""
    print("Processing products with LLM...")
    
    """
    Step 1:
    Generate the brand, model, and search terms for each product with a LLM
    Uses gemini-2.0-flash as it's only $0.40 per 1M output tokens and scores highly on benchmarks, arguably the best price to perfomance for LLMs
    """
    validated_products, success = await process_and_validate_products(Products)
    
    if not success:
        print("Failed to process products. Exiting...")
        return
    
    print("\nValidated Products:")
    pprint.pprint(validated_products[:2])  # Print just the first two for brevity
    print(f"Total validated products: {len(validated_products)}")
    
    """
    Step 2:
    Scrape websites for product information
    """
    # Scrape Best Buy - limit to 3 products for testing
    bestbuy_results = scrape_bestbuy_products(validated_products, max_products=18, headless=False)
    
    print("\nBest Buy Scraping Results:")
    print("="*80)
    
    for model_no, data in bestbuy_results.items():
        bestbuy_data = data.get('bestbuy_data')
        original_info = data.get('original_info', {})
        
        print(f"\nModel: {model_no} ({original_info.get('brand', 'Unknown')})")
        print(f"Original Name: {original_info.get('input_name', 'N/A')}")
        
        if bestbuy_data:
            print(f"✅ Found at Best Buy:")
            print(f"   Name: {bestbuy_data.get('name', 'N/A')}")
            print(f"   Price: {bestbuy_data.get('price', 'N/A')}")
            print(f"   Rating: {bestbuy_data.get('rating', 'N/A')}")
            print(f"   SKU: {bestbuy_data.get('sku', 'N/A')}")
            print(f"   URL: {bestbuy_data.get('url', 'N/A')}")
        else:
            print(f"❌ Not found at Best Buy")
            
    """
    Step 3:
    Export the results as structured JSON data grouped by brand
    """
    # Create a structure to organize products by brand
    structured_data = {"brands": {}}
    
    # Organize all products by brand
    for model_no, data in bestbuy_results.items():
        bestbuy_data = data.get('bestbuy_data')
        original_info = data.get('original_info', {})
        brand = original_info.get('brand', 'unknown').lower()
        
        # Initialize the brand in our structure if it doesn't exist
        if brand not in structured_data["brands"]:
            structured_data["brands"][brand] = []
        
        # Create a product entry
        product_entry = {
            "model_no": model_no,
            "original_name": original_info.get('input_name', 'N/A'),
            "bestbuy": {
                "found": bestbuy_data is not None
            }
        }
        
        # Add BestBuy data if available
        if bestbuy_data:
            product_entry["bestbuy"].update({
                "name": bestbuy_data.get('name', 'N/A'),
                "price": bestbuy_data.get('price', 'N/A'),
                "rating": bestbuy_data.get('rating', 'N/A'),
                "sku": bestbuy_data.get('sku', 'N/A'),
                "url": bestbuy_data.get('url', 'N/A')
            })
        
        # Add the product to its brand's list
        structured_data["brands"][brand].append(product_entry)
    
    # Print the structured data
    print("\n\nFINAL STRUCTURED DATA")
    print("="*80)
    pprint.pprint(structured_data, width=100, sort_dicts=False)
    
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())