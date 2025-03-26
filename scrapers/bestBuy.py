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
        
        try:
            # List of potential popup selectors and their corresponding action buttons
            popup_selectors = [
                # Modal backdrop (generic)
                {"popup": "#confirmIt-backdrop", "button": ".confirm-btn, .close-btn, .btn-close, .btn-primary"},
                # Cookie consent
                {"popup": ".cookie-banner", "button": ".cookie-accept-btn, .cookie-close-btn, .agree-button"},
                # Newsletter signup
                {"popup": ".email-signup-modal", "button": ".email-signup-close, .modal-close-btn"},
                # Location prompt
                {"popup": ".location-modal", "button": ".location-close-btn, .modal-close"},
                # Survey invite
                {"popup": ".survey-modal", "button": ".survey-close-btn, .modal-close"},
                # Generic modals
                {"popup": ".modal-dialog", "button": ".close, .btn-close, .modal-close, .dismiss"},
                # Generic popups
                {"popup": ".popup, .popup-container", "button": ".close, .btn-close, .popup-close"},
                # Specific to BestBuy
                {"popup": ".c-modal-grid", "button": ".c-close-icon, .c-button-secondary"},
                # Confirmit modal specific to Best Buy
                {"popup": "#confirmIt-backdrop", "button": "#confirmIt-noBtn"}
            ]
            
            # Check each potential popup
            for selector in popup_selectors:
                try:
                    # Use a short timeout for checking popups
                    popup_elements = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector["popup"]))
                    )
                    
                    print(f"Found popup: {selector['popup']}")
                    
                    # Try to find and click the close/dismiss button
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector["button"])
                    if buttons:
                        # Click the first button found
                        print(f"Attempting to close popup with: {selector['button']}")
                        buttons[0].click()
                        print("Popup closed successfully")
                        time.sleep(1)  # Brief pause after closing popup
                    else:
                        print(f"No close button found for popup: {selector['popup']}")
                        
                        # Try pressing ESC key to dismiss modal
                        print("Trying to dismiss with ESC key")
                        webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                        time.sleep(1)  # Brief pause after ESC
                except TimeoutException:
                    # This popup doesn't exist, try the next one
                    continue
                except Exception as e:
                    print(f"Error handling popup {selector['popup']}: {e}")
            
            # Additional specific handling for the confirmIt modal backdrop
            try:
                backdrop = self.driver.find_element(By.ID, "confirmIt-backdrop")
                if backdrop:
                    print("Found confirmIt backdrop, attempting to dismiss")
                    # Try clicking the backdrop itself
                    backdrop.click()
                    time.sleep(0.5)
                    
                    # Try to find and click No button
                    try:
                        no_button = self.driver.find_element(By.ID, "confirmIt-noBtn")
                        no_button.click()
                        print("Clicked 'No' button on confirmIt modal")
                    except NoSuchElementException:
                        pass
                    
                    # Use JavaScript to remove the backdrop
                    self.driver.execute_script("arguments[0].remove();", backdrop)
                    print("Removed confirmIt backdrop with JavaScript")
                    
                    # Also remove the modal-open class from body to allow scrolling
                    self.driver.execute_script("document.body.classList.remove('modal-open');")
                    print("Removed modal-open class from body")
            except NoSuchElementException:
                pass
            except Exception as e:
                print(f"Error handling confirmIt backdrop: {e}")
        
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
            self._add_delay("navigate")
            
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
            # Product name
            name_elem = item.select_one(".sku-title a, .product-title")
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
            price_elem = item.select_one(".priceView-customer-price span, .customer-price")
            if price_elem:
                product['price'] = price_elem.text.strip()
            
            # Product rating
            rating_elem = item.select_one(".c-ratings-reviews-v2, .c-ratings-reviews")
            if rating_elem:
                product['rating'] = rating_elem.text.strip()
            
            # Extract model number and SKU
            attributes = item.select(".product-attributes .attribute")
            if attributes:
                for attribute in attributes:
                    attribute_text = attribute.text.strip()
                    if "Model:" in attribute_text:
                        model_value = attribute.select_one(".value")
                        if model_value:
                            product['model'] = model_value.text.strip()
                    elif "SKU:" in attribute_text:
                        sku_value = attribute.select_one(".value")
                        if sku_value:
                            product['sku'] = sku_value.text.strip()
            
            # Try alternative method for model/SKU if needed
            if 'model' not in product or 'sku' not in product:
                # Check if there's a data-testid attribute (SKU)
                if hasattr(item, 'attrs') and 'data-testid' in item.attrs:
                    product['sku'] = item['data-testid']
                
                # Look for model in different formats
                model_containers = item.select('.attribute, .product-data')
                for container in model_containers:
                    if container.text and 'Model:' in container.text:
                        model_text = container.text.strip()
                        model_parts = model_text.split('Model:')
                        if len(model_parts) > 1:
                            model_value = model_parts[1].split('SKU:')[0].strip()
                            if model_value:
                                product['model'] = model_value
        
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
            # Wait for product items to be present
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".sku-item, .product-list-item"))
            )
            
            # Add delay before processing
            self._add_delay("general")
            
            # Initialize results list and tracking variables
            all_results = []
            scroll_count = 0
            model_found = False
            matching_product = None
            processed_items = set()  # Track processed items to avoid duplicates
            
            # Process results with scrolling if needed
            while scroll_count < max_scroll_attempts:
                # Get the page HTML and parse with BeautifulSoup
                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find all product items
                product_items = soup.select(".sku-item, .product-list-item")
                print(f"Found {len(product_items)} product items on page (scroll {scroll_count})")
                
                new_items_found = False
                
                # Process each product item
                for item in product_items:
                    # Get a unique identifier for this item (data-testid or some other attribute)
                    item_id = None
                    if hasattr(item, 'attrs'):
                        if 'data-testid' in item.attrs:
                            item_id = item['data-testid']
                        elif 'data-sku-id' in item.attrs:
                            item_id = item['data-sku-id']
                        elif 'data-product-id' in item.attrs:
                            item_id = item['data-product-id']
                        elif 'id' in item.attrs:
                            item_id = item['id']
                    
                    if not item_id:
                        # If no ID found, use the item content as hash
                        item_id = hash(str(item))
                    
                    # Skip if we've already processed this item
                    if item_id in processed_items:
                        continue
                    
                    # Mark as processed
                    processed_items.add(item_id)
                    new_items_found = True
                    
                    # Extract product information
                    product = self._extract_product_info(item)
                    
                    # If we're looking for a specific model
                    if model_no and 'model' in product and product['model']:
                        # Check for exact or partial model match (case insensitive)
                        if (model_no.lower() == product['model'].lower() or 
                                model_no.lower() in product['model'].lower()):
                            print(f"Model number {model_no} found!")
                            model_found = True
                            matching_product = product
                            break
                    
                    # Add to results list
                    all_results.append(product)
                
                # If we found the model or reached max scrolls, break the loop
                if model_found or scroll_count >= max_scroll_attempts:
                    break
                
                # If no new items were found and we've reached the end, break
                if not new_items_found and not self._has_more_products():
                    print("No more products to load")
                    break
                
                # Scroll down to load more items
                print(f"Scrolling down to load more results (attempt {scroll_count + 1}/{max_scroll_attempts})...")
                scroll_down_pause(self.driver, verbose=self.use_delays)
                
                # Increment scroll counter
                scroll_count += 1
            
            # Return results based on what was requested
            if model_no:
                if model_found:
                    print(f"Returning product matching model {model_no}")
                    return matching_product
                else:
                    print(f"Model {model_no} not found in search results")
                    return None
            else:
                print(f"Returning all {len(all_results)} products found")
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

# Example usage
if __name__ == "__main__":
    try:
        print("Starting Best Buy scraper...")
        scraper = BestBuyScraper(headless=False, use_delays=True)  # Set headless=True for production
        try:
            search_term = "lg 50 4k smart led tv"
            print(f"Searching for '{search_term}'...")
            search_url = scraper.search(search_term)
            
            if search_url:
                print(f"Search URL: {search_url}")
                
                # Example 1: Get a few results first to find model numbers
                results = scraper.get_search_results(max_scroll_attempts=3)
                print(f"Found {len(results)} products in initial scan")
                
                # Get first model number found to use for testing
                example_model = '50UT7570PUB'
                for product in results:
                    if 'model' in product and product['model']:
                        example_model = product['model']
                        break
                
                if example_model:
                    print(f"\nSearching for model: {example_model}")
                    # Example 2: Search for a specific model number
                    model_result = scraper.get_search_results(model_no=example_model)
                    if model_result:
                        print(f"Found model {example_model}:")
                        print(f"Name: {model_result.get('name', 'N/A')}")
                        print(f"Price: {model_result.get('price', 'N/A')}")
                        print(f"Rating: {model_result.get('rating', 'N/A')}")
                        print(f"Model: {model_result.get('model', 'N/A')}")
                        print(f"SKU: {model_result.get('sku', 'N/A')}")
                        print(f"URL: {model_result.get('url', 'N/A')}")
                else:
                    print("No model numbers found in initial results")
                    
                    # Print the first 5 results
                    for i, product in enumerate(results[:5], 1):
                        print(f"\nProduct {i}:")
                        print(f"Name: {product.get('name', 'N/A')}")
                        print(f"Price: {product.get('price', 'N/A')}")
                        print(f"Rating: {product.get('rating', 'N/A')}")
                        print(f"Model: {product.get('model', 'N/A')}")
                        print(f"SKU: {product.get('sku', 'N/A')}")
                        print(f"URL: {product.get('url', 'N/A')}")
        finally:
            scraper.close()
    except Exception as e:
        print(f"Unhandled exception: {str(e)}")
        traceback.print_exc()
