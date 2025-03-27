import time
import os
import sys
import random
import pprint
# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from webdriver_manager.chrome import ChromeDriverManager
import traceback
from bs4 import BeautifulSoup
from utils.userAgentRotation import get_desktop_user_agent
from utils.delayUtils import random_delay, random_typing_delay, human_like_delay, scroll_down_pause


class BestBuyScraper:
    def __init__(self, headless=True, use_delays=True):
        """Initialize the Best Buy scraper with Selenium webdriver"""
        self.base_url = "https://www.bestbuy.com/"
        self.use_delays = use_delays
        
        try:
            # Get a random user agent
            random_user_agent = get_desktop_user_agent()
            print(f"Using user agent: {random_user_agent}")
            
            # Configure Chrome options
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument(f"--user-agent={random_user_agent}")
            
            # Initialize the Chrome driver
            print("Initializing Chrome WebDriver...")
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            print("Chrome WebDriver initialized successfully.")
            
            # Add initial delay after browser initialization
            if self.use_delays:
                human_like_delay("general")
            
        except Exception as e:
            print(f"Error initializing Chrome WebDriver: {str(e)}")
            traceback.print_exc()
            raise
    
    def _add_delay(self, action_type="general"):
        """Add human-like delay if delays are enabled"""
        if self.use_delays:
            human_like_delay(action_type)
    
    def _type_with_delays(self, element, text):
        """Type text with human-like delays between characters"""
        if not self.use_delays:
            element.clear()
            element.send_keys(text)
            return
        
        # Clear the field
        element.clear()
        self._add_delay("type")
        
        # Calculate typing delay
        text, total_delay = random_typing_delay(text, verbose=True)
        
        # Type each character with small random delays
        for char in text:
            element.send_keys(char)
            char_delay = random.uniform(0.05, 0.2)  # Small delay between keystrokes
            time.sleep(char_delay)
        
        # Additional small delay after typing
        random_delay(0.2, 0.5, verbose=False)
    
    def _handle_popups(self):
        """Handle any popups or modals that might appear"""
        print("Checking for popups and modals...")
        
        # Quick check if any popups exist at all before detailed checking
        try:
            # Use a very short timeout for initial check
            popup_exists = False
            try:
                # Check for common popup indicators with a very short timeout
                popup_exists = WebDriverWait(self.driver, 0.5).until(
                    EC.presence_of_any_element_located((
                        By.CSS_SELECTOR, 
                        ".modal, .popup, .c-modal-grid, #confirmIt-backdrop, .cookie-banner"
                    ))
                )
            except TimeoutException:
                # No popups detected, exit early
                print("No popups detected, skipping popup handling")
                return
            
            # List of potential popup selectors and their corresponding action buttons
            # Ordered by frequency of appearance for efficiency
            popup_selectors = [
                # Specific to BestBuy (most common)
                {"popup": ".c-modal-grid", "button": ".c-close-icon, .c-button-secondary", "timeout": 0.5},
                # Confirmit modal specific to Best Buy
                {"popup": "#confirmIt-backdrop", "button": "#confirmIt-noBtn", "timeout": 0.5},
                # Cookie consent
                {"popup": ".cookie-banner", "button": ".cookie-accept-btn, .cookie-close-btn, .agree-button", "timeout": 0.5},
                # Generic modals (common)
                {"popup": ".modal-dialog", "button": ".close, .btn-close, .modal-close, .dismiss", "timeout": 0.5},
                # Other less common popups
                {"popup": ".email-signup-modal", "button": ".email-signup-close, .modal-close-btn", "timeout": 0.3},
                {"popup": ".location-modal", "button": ".location-close-btn, .modal-close", "timeout": 0.3},
                {"popup": ".survey-modal", "button": ".survey-close-btn, .modal-close", "timeout": 0.3},
                {"popup": ".popup, .popup-container", "button": ".close, .btn-close, .popup-close", "timeout": 0.3},
                {"popup": "#confirmIt-backdrop", "button": ".confirm-btn, .close-btn, .btn-close, .btn-primary", "timeout": 0.3},
            ]
            
            # Check each potential popup
            popup_found = False
            for selector in popup_selectors:
                try:
                    # Use a short timeout for checking popups
                    timeout = selector.get("timeout", 0.5)
                    popup_elements = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector["popup"]))
                    )
                    
                    popup_found = True
                    print(f"Found popup: {selector['popup']}")
                    
                    # Try to find and click the close/dismiss button
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector["button"])
                    if buttons:
                        # Click the first button found
                        print(f"Attempting to close popup with: {selector['button']}")
                        buttons[0].click()
                        print("Popup closed successfully")
                        time.sleep(0.5)  # Brief pause after closing popup
                        
                        # Once we've handled one popup, break out to recheck the page
                        # This prevents trying to interact with elements that might be gone
                        break
                    else:
                        print(f"No close button found for popup: {selector['popup']}")
                        
                        # Try pressing ESC key to dismiss modal
                        print("Trying to dismiss with ESC key")
                        webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                        time.sleep(0.5)  # Brief pause after ESC
                        break
                except TimeoutException:
                    # This popup doesn't exist, try the next one
                    continue
                except Exception as e:
                    print(f"Error handling popup {selector['popup']}: {e}")
            
            # If no popups were found through the selectors but we detected one initially,
            # use JavaScript to try to remove common modal elements
            if popup_exists and not popup_found:
                print("Using JavaScript to remove potential modal elements")
                self.driver.execute_script("""
                    // Remove common modal backdrops
                    document.querySelectorAll('.modal-backdrop, #confirmIt-backdrop').forEach(e => e.remove());
                    // Remove modal-open class from body
                    document.body.classList.remove('modal-open');
                """)
            
        except Exception as e:
            print(f"Error in popup handling: {e}")
        
        print("Popup checking completed")
        
    def search(self, query):
        """Search for a product on Best Buy website"""
        try:
            print(f"Navigating to {self.base_url}...")
            # Navigate to the Best Buy homepage
            self.driver.get(self.base_url)
            print("Successfully loaded Best Buy homepage.")
            
            # Add delay after navigation
            # self._add_delay("navigate")
            
            # Handle any popups before proceeding
            self._handle_popups()
            
            # Wait for the search input field to be visible
            print("Waiting for search input field...")
            search_input = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.ID, "gh-search-input"))
            )
            print("Search input field found.")
            
            # Add delay before typing
            self._add_delay("type")
            
            # Enter the search query with realistic typing delays
            print(f"Entering search query: {query}")
            self._type_with_delays(search_input, query)
            
            # Add delay before clicking
            self._add_delay("click")
            
            # Try multiple approaches to submit the search
            print("Attempting to submit search...")
            try:
                # First try: Click the search button
                print("Clicking search button...")
                search_button = self.driver.find_element(By.CLASS_NAME, "header-search-button")
                search_button.click()
            except Exception as e:
                print(f"Click failed: {e}")
                
                # Second try: Press Enter key
                print("Trying Enter key...")
                search_input.send_keys(Keys.ENTER)
            
            # Add delay after search submission
            self._add_delay("search")
            
            # Wait for search results to load
            print("Waiting for search results to load...")
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".sku-item, .product-list-item"))
            )
            
            print("Search results loaded successfully.")
            
            # Add delay to simulate reading results
            self._add_delay("read")
            
            # Return the current page URL (search results)
            return self.driver.current_url
            
        except Exception as e:
            print(f"An error occurred during search: {str(e)}")
            traceback.print_exc()
            # Save screenshot for debugging
            try:
                self.driver.save_screenshot("error_screenshot.png")
                print("Screenshot saved as error_screenshot.png")
                print(f"Current URL: {self.driver.current_url}")
                print(f"Page source length: {len(self.driver.page_source)}")
            except:
                pass
            return None
    
    def _extract_product_info(self, item):
        """Extract product information from a product item element"""
        product = {}
        
        try:
            # Store the item ID as SKU (often matches SKU)
            if hasattr(item, 'attrs') and 'data-testid' in item.attrs:
                product['sku'] = item['data-testid']
            
            # Product name
            name_elem = item.select_one(".sku-title a, .product-title, h2.product-title")
            if name_elem:
                product['name'] = name_elem.text.strip()
                
                # Extract URL from anchor element
                anchor = name_elem
                if not name_elem.name == 'a':
                    anchor = name_elem.find_parent('a')
                
                if anchor and anchor.has_attr('href'):
                    if anchor['href'].startswith('http'):
                        product['url'] = anchor['href']
                    else:
                        product['url'] = self.base_url + anchor['href'].lstrip('/')
            
            # Product price
            price_elem = item.select_one(".priceView-customer-price span, .customer-price, #medium-customer-price")
            if price_elem:
                product['price'] = price_elem.text.strip()
            
            # Product rating
            rating_elem = item.select_one(".c-ratings-reviews-v2, .c-ratings-reviews, .c-ratings-reviews-mini")
            if rating_elem:
                # Look for the visually-hidden text that contains the full rating
                hidden_rating = rating_elem.select_one(".visually-hidden")
                if hidden_rating:
                    product['rating'] = hidden_rating.text.strip()
                else:
                    product['rating'] = rating_elem.text.strip()
            
            # PRIMARY METHOD: Extract model number and SKU from product-attributes
            attribute_container = item.select_one(".product-attributes")
            if attribute_container:
                attributes = attribute_container.select(".attribute")
                for attribute in attributes:
                    attribute_text = attribute.text.strip()
                    
                    # Extract model
                    if "Model:" in attribute_text:
                        # First try to get model from value span
                        model_value = attribute.select_one(".value")
                        if model_value:
                            product['model'] = model_value.text.strip()
                        # If no value span, extract from text
                        elif ":" in attribute_text:
                            model_parts = attribute_text.split(":", 1)
                            if len(model_parts) > 1:
                                product['model'] = model_parts[1].strip()
                    
                    # Extract SKU
                    if "SKU:" in attribute_text:
                        # First try to get SKU from value span
                        sku_value = attribute.select_one(".value")
                        if sku_value:
                            product['sku'] = sku_value.text.strip()
                        # If no value span, extract from text
                        elif ":" in attribute_text:
                            sku_parts = attribute_text.split(":", 1)
                            if len(sku_parts) > 1:
                                product['sku'] = sku_parts[1].strip()
            
            # ALTERNATE METHOD 1: Look for any elements with model/sku info
            if 'model' not in product or 'sku' not in product:
                # Look for any elements containing Model: or SKU: text
                all_elements = item.select("div, span, p")
                for elem in all_elements:
                    if not elem.text:
                        continue
                    
                    elem_text = elem.text.strip()
                    # Try to extract model
                    if 'model' not in product and "Model:" in elem_text:
                        try:
                            # Try to extract model number after "Model:"
                            model_parts = elem_text.split("Model:")
                            if len(model_parts) > 1:
                                model_text = model_parts[1].split("SKU:")[0].strip()
                                if model_text:
                                    product['model'] = model_text
                        except Exception:
                            pass
                    
                    # Try to extract SKU
                    if 'sku' not in product and "SKU:" in elem_text:
                        try:
                            # Try to extract SKU after "SKU:"
                            sku_parts = elem_text.split("SKU:")
                            if len(sku_parts) > 1:
                                sku_text = sku_parts[1].strip().split()[0]
                                if sku_text:
                                    product['sku'] = sku_text
                        except Exception:
                            pass
            
            # ALTERNATE METHOD 2: Check for other common patterns
            # Sometimes model/sku are in other formats like data attributes or hidden fields
            if 'model' not in product:
                model_elems = item.select('[data-model], [data-model-number], .model-number')
                for elem in model_elems:
                    if elem.has_attr('data-model'):
                        product['model'] = elem['data-model']
                        break
                    elif elem.has_attr('data-model-number'):
                        product['model'] = elem['data-model-number']
                        break
                    elif elem.text:
                        product['model'] = elem.text.strip()
                        break
            
            # Last resort - use data-testid as SKU if not already found
            if 'sku' not in product and 'data-testid' in product:
                product['sku'] = product['data-testid']
                
            # Debug output if fields are still missing
            if 'model' not in product or 'sku' not in product:
                if 'name' in product:
                    missing = []
                    if 'model' not in product:
                        missing.append('model')
                    if 'sku' not in product:
                        missing.append('sku')
                    print(f"Missing {', '.join(missing)} for product: {product.get('name', 'Unknown')}")
        
        except Exception as e:
            print(f"Error extracting product details: {e}")
        
        return product
    
    def _has_more_products(self):
        """Check if there are more products to load by scrolling"""
        # Check if we're at the bottom of the page
        bottom_check = self.driver.execute_script(
            "return (window.innerHeight + window.scrollY) >= document.body.scrollHeight - 200;"
        )
        
        # Check if there's a "Show More" button
        try:
            show_more_button = self.driver.find_element(By.CSS_SELECTOR, ".show-more-button, .load-more")
            return True
        except NoSuchElementException:
            pass
        
        # If we're at the bottom and no "Show More" button, we're likely at the end
        if bottom_check:
            # Double check by looking for a "End of Results" message
            try:
                end_message = self.driver.find_element(By.CSS_SELECTOR, ".end-of-results, .no-more-results")
                return False
            except NoSuchElementException:
                # If no end message found, we'll assume there might be more (safer approach)
                return True
        
        # If not at the bottom, we can scroll more
        return True
    
    def get_search_results(self, model_no=None, max_scroll_attempts=15):
        """
        Extract product information from the search results page, 
        optionally searching for a specific model number
        
        Args:
            model_no: If provided, search for this specific model number
            max_scroll_attempts: Maximum number of times to scroll down
        
        Returns:
            List of product dictionaries, or a single product if model_no is found
        """
        try:
            # Wait for initial product items to be present
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".sku-item, .product-list-item"))
            )
            
            print("Initial products loaded, beginning extraction...")
            
            # First scroll to bottom to force load all products
            print("Pre-loading all products with progressive scrolling...")
            total_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            scroll_step = viewport_height // 2  # Half viewport per scroll
            
            # Start from top
            self.driver.execute_script("window.scrollTo(0, 0)")
            time.sleep(1)
            
            # Progress to bottom with pauses
            current_position = 0
            for i in range(max_scroll_attempts):
                # Calculate next position with some randomness
                scroll_amount = int(scroll_step * random.uniform(0.8, 1.2))
                current_position += scroll_amount
                
                # Scroll down
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                print(f"Scrolled to position {current_position}/{total_height}")
                
                # Allow content to load with a fixed pause
                time.sleep(1.5)  # Consistent pause for content loading
                
                # Check if we're at the bottom
                if current_position >= total_height:
                    # Get updated height (may have increased with dynamic content)
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height > total_height:
                        # Page grew, update total height and continue
                        print(f"Page height increased: {total_height} -> {new_height}")
                        total_height = new_height
                    else:
                        # We're truly at the bottom
                        print("Reached bottom of page")
                        break
            
            # One final scroll to the very bottom to ensure all content is loaded
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Final wait for any last content
            
            # Now grab ALL products at once after everything has loaded
            print("Extracting all loaded products...")
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find all product items
            product_items = soup.select(".sku-item, .product-list-item")
            print(f"Found {len(product_items)} total product items after scrolling")
            
            # Process all products
            all_results = []
            matching_product = None
            model_found = False
            
            for item in product_items:
                # Extract product information
                product = self._extract_product_info(item)
                
                # Add product to results if it has essential data
                if product and 'name' in product:
                    all_results.append(product)
                    
                    # Check if this matches our model
                    if model_no and 'model' in product and product['model']:
                        if (model_no.lower() == product['model'].lower() or 
                                model_no.lower() in product['model'].lower()):
                            print(f"Model {model_no} found!")
                            model_found = True
                            matching_product = product
            
            # Print results if we didn't find the model
            if model_no and not model_found:
                print(f"Model {model_no} not found in {len(all_results)} products")
                print("Available models:")
                for product in all_results:
                    if 'model' in product:
                        print(f"  - {product.get('model', 'N/A')}: {product.get('name', 'N/A')}")
            
            # Return results based on what was requested
            if model_no:
                if model_found:
                    return matching_product
                else:
                    return None
            else:
                print(f"Found {len(all_results)} total products")
                return all_results
            
        except Exception as e:
            print(f"An error occurred getting search results: {str(e)}")
            traceback.print_exc()
            if model_no:
                return None
            return []
    
    def close(self):
        """Close the Selenium webdriver"""
        if hasattr(self, 'driver') and self.driver:
            print("Closing Chrome WebDriver...")
            try:
                # Add delay before closing
                if self.use_delays:
                    random_delay(0.5, 1.5, verbose=True)
                    
                self.driver.quit()
                print("Chrome WebDriver closed successfully.")
            except Exception as e:
                print(f"Error closing Chrome WebDriver: {str(e)}")
    
    def batch_search(self, search_model_pairs, max_scroll_attempts=15):
        """
        Perform multiple searches for specific models in a batch
        
        Args:
            search_model_pairs: Dictionary where keys are search terms and values are model numbers to find
            max_scroll_attempts: Maximum number of scroll attempts per search
            
        Returns:
            Dictionary where keys are model numbers and values are product details (or None if not found)
        """
        results = {}
        
        try:
            for search_term, model_no in search_model_pairs.items():
                print(f"\n{'='*60}\nSearching for '{search_term}' to find model '{model_no}'")
                print(f"{'='*60}\n")
                
                # Perform the search
                search_url = self.search(search_term)
                
                if search_url:
                    print(f"Search URL: {search_url}")
                    
                    # Try to find the specific model
                    product = self.get_search_results(model_no=model_no, max_scroll_attempts=max_scroll_attempts)
                    
                    if product:
                        print(f"✅ Found model {model_no}!")
                        results[model_no] = product
                    else:
                        print(f"❌ Model {model_no} not found in search results.")
                        results[model_no] = None
                else:
                    print(f"❌ Search failed for term '{search_term}'")
                    results[model_no] = None
                
                # Add a pause between searches
                time.sleep(2)
        
        except Exception as e:
            print(f"Error during batch search: {str(e)}")
            traceback.print_exc()
            
        return results


# Example usage
if __name__ == "__main__":
    try:
        print("Starting Best Buy scraper...")
        scraper = BestBuyScraper(headless=False, use_delays=True)  # Set headless=True for production
        try:
            # Define search terms and model numbers to find
            search_model_pairs = {
                "lg 50 4k smart led tv": "50UT7570PUB",
                "lg 55 oled tv": "OLED55G4SUB",
                "lg 48 oled tv 2024": "OLED48C4PUA",
                "lg nano tv 55": "55NANO75UQA"
            }
            
            # Perform batch search
            results = scraper.batch_search(search_model_pairs)
            
            # Print summary of results
            print("\n\n" + "="*80)
            print("SEARCH RESULTS SUMMARY")
            print("="*80)
            
            for model_no, product in results.items():
                if product:
                    print(f"\n✅ Model: {model_no}")
                    print(f"   Name: {product.get('name', 'N/A')}")
                    print(f"   Price: {product.get('price', 'N/A')}")
                    print(f"   Rating: {product.get('rating', 'N/A')}")
                    print(f"   SKU: {product.get('sku', 'N/A')}")
                    print(f"   URL: {product.get('url', 'N/A')}")
                else:
                    print(f"\n❌ Model: {model_no} - Not found")
            
        finally:
            scraper.close()
    except Exception as e:
        print(f"Unhandled exception: {str(e)}")
        traceback.print_exc()
