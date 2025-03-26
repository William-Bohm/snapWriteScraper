import dotenv
import asyncio

from utils.llmFunctions import process_and_validate_products

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

async def main():
    """Main entry point for the application."""
    print("Processing products with LLM...")
    
    # Process and validate products with LLM
    validated_products, success = await process_and_validate_products(Products)
    
    if success:
        print(f"\nTotal products with valid data: {len(validated_products)}")
        # validated_products now contains the structured data ready for use
    
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(main())