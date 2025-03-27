# What I built
I built a python script that generates dynamic search terms powered by an LLM (gemini-2.0-flash). I spent roughly 3 hours on this project and only implemented best buy scraping. The generated search terms and model numbers are then used to search Best Buy, one at a time searching for a product with the exact input model number and returns that data if found. Best Buy requires scrolling in the webpage to load all of the products so I implented a realistic scrolling mechanism to simulate a real human. There are alot of optimizations that can be made (read below).

# How it works/ what it does
* Takes in the products names as input
* Sends the product names to an LLM to generate a good search term for the product and extract the brand and model number from the string
* For each product it loads the Best Buy home page and types the search term in, one character at a time with a different delay between each charecter to reduce bot detection
* Once the search apge is loaded, it scrolls down at random intervals to load all the products as scrolling is required to load all products due to the JS loading of the webpage. 
* The script builds a list of all the products on a webpage and checks if any of the products have the exact same model number as the input
* returns true of so, false other wise.

# How it reduces bot detection
* Each time the script is run we use a different user-agent (see the useAGentRotation.py file).
* Each action uses a randomely timed wait period to wait or commit an action (see the delayUtils.py file). Including scrolling, typing, and searching.

# How it can be improved
Due to me only willing to spend a few hours on this project, alot of improvements can be made:
* reduce delays and timings for each action, to see how fast we can go without being flagged as bots or rate limiting
* Implement a rotating proxy netowork so we can send multiple requests at once, as the target website will view them as different organic users as they will have different ip's, user agents AND different delay/wait times for each action.
* I did not attempt to implement CAPTCHA solving due to again, only spending a few hours on this.
* We are only processing one product on one website at a time. It is likely we can process multiple products with the same ip/user-agent at a time without getting rate-limted or flagged.
* Currently only running one website scraper, but we could run all 12 mentioned websites at the same time on the same ip/user-agent combo with just one instance of chrome, rather than having to spin up 12 seperate chrome sessions to run searches.
* defaults to not headless for example purposes
* modal/popup handling could be tested much more and optimized.
* Containerize with docker and setup to run as a webserver (or run it as a serverless function like on AWS Lambda) with an api endpoint that takes in a search term, finds the data, and save it to our databases
* simplify logging
* Search through multiple pages, the script currently does not attempt to cycle through multiple pages for the same search.



# How to run the application
* 1: create your .env file (you will need a google gemini api key for the LLM calling):
```
DEBUG=True
LOG_LEVEL=INFO
GOOGLE_API_KEY={YOUR_GEMIN_KEY_HERE}
```

* 2: Install the python packages
This project uses poetry as the package manager, make sure you have poetry installed on your system before running
```Poetry install```

* 3: run the project
```poetry run python main.py```


# Results from bestBuy.com
The script finds indentifies that out of the 18 products, there are only 6 of the products on best buys website with the exact model number specified in the searches. Output below: 

{'brands': {'hisense': [{'model_no': '50A68N',
                         'original_name': 'Hisense 50" 4K Smart Google AI Upscaler LED TV - 50A68N',
                         'bestbuy': {'found': False}},
                        {'model_no': '55A68N',
                         'original_name': 'Hisense 55" 4K Smart Google AI Upscaler LED TV - 55A68N',
                         'bestbuy': {'found': False}},
                        {'model_no': '32A4KV',
                         'original_name': 'Hisense 32" HD Smart VIDAA LED TV - 32A4KV',
                         'bestbuy': {'found': False}}],
            'samsung': [{'model_no': 'UN75DU7100FXZC',
                         'original_name': 'Samsung 75” 4K Tizen Smart CUHD TV - UN75DU7100FXZC',
                         'bestbuy': {'found': False}},
                        {'model_no': 'QN65Q80DAFXZC',
                         'original_name': 'Samsung 65” 4K Tizen Smart QLED TV - QN65Q80DAFXZC',
                         'bestbuy': {'found': False}},
                        {'model_no': 'UN43DU7100FXZC',
                         'original_name': 'Samsung 43” 4K Tizen Smart CUHD TV-UN43DU7100FXZC',
                         'bestbuy': {'found': False}},
                        {'model_no': 'QN75Q80DAFXZC',
                         'original_name': 'Samsung 75” 4K Tizen Smart QLED TV - QN75Q80DAFXZC',
                         'bestbuy': {'found': False}},
                        {'model_no': 'QN65QN85DBFXZC',
                         'original_name': 'Samsung 65” Neo QLED 4K Tizen Smart TV QN85D - '
                                          'QN65QN85DBFXZC',
                         'bestbuy': {'found': False}},
                        {'model_no': 'QN65S90DAFXZC',
                         'original_name': 'Samsung 65” OLED 4K Tizen Smart TV S90D - QN65S90DAFXZC',
                         'bestbuy': {'found': False}},
                        {'model_no': 'UN65DU7100FXZC',
                         'original_name': 'Samsung 65” 4K Tizen Smart CUHD TV - UN65DU7100FXZC',
                         'bestbuy': {'found': False}}],
            'lg': [{'model_no': '50UT7570PUB',
                    'original_name': 'LG 50" UHD 4K Smart LED TV - 50UT7570PUB',
                    'bestbuy': {'found': True,
                                'name': 'LG - 50” Class UT75 Series LED 4K UHD Smart webOS TV '
                                        '(2024)',
                                'price': '$299.99',
                                'rating': 'Rating 4.6 out of 5 stars with 169 reviews',
                                'sku': '6578195Rating',
                                'url': 'https://www.bestbuy.com/site/lg-50-class-ut75-series-led-4k-uhd-smart-webos-tv-2024/6578195.p?skuId=6578195'}},
                   {'model_no': '65UT7570PUB',
                    'original_name': 'LG 65" UHD 4K Smart LED TV - 65UT7570PUB',
                    'bestbuy': {'found': True,
                                'name': 'LG - 65” Class UT75 Series LED 4K UHD Smart webOS TV '
                                        '(2024)',
                                'price': '$399.99',
                                'rating': 'Rating 4.5 out of 5 stars with 290 reviews',
                                'sku': '6578178Rating',
                                'url': 'https://www.bestbuy.com/site/lg-65-class-ut75-series-led-4k-uhd-smart-webos-tv-2024/6578178.p?skuId=6578178'}},
                   {'model_no': 'OLED65C4PUA',
                    'original_name': 'LG 65" 4K Smart evo C4 OLED TV - OLED65C4PUA',
                    'bestbuy': {'found': True,
                                'name': 'LG - 65" Class C4 Series OLED evo 4K UHD Smart webOS TV '
                                        '(2024)',
                                'price': '$1,399.99',
                                'rating': 'Rating 4.8 out of 5 stars with 719 reviews',
                                'sku': '6578042Rating',
                                'url': 'https://www.bestbuy.com/site/lg-65-class-c4-series-oled-evo-4k-uhd-smart-webos-tv-2024/6578042.p?skuId=6578042'}},
                   {'model_no': '86UT7590PUA',
                    'original_name': 'LG 86" UHD 4K Smart LED TV - 86UT7590PUA',
                    'bestbuy': {'found': True,
                                'name': 'LG - 86” Class UT75 Series LED 4K UHD Smart webOS TV '
                                        '(2024)',
                                'price': '$749.99',
                                'rating': 'Rating 4.7 out of 5 stars with 180 reviews',
                                'sku': '6578185Rating',
                                'url': 'https://www.bestbuy.com/site/lg-86-class-ut75-series-led-4k-uhd-smart-webos-tv-2024/6578185.p?skuId=6578185'}},
                   {'model_no': '55QNED80TUC',
                    'original_name': 'LG 55" QNED80 4K Smart QLED TV - 55QNED80TUC',
                    'bestbuy': {'found': True,
                                'name': 'LG - 55” Class 80 Series QNED 4K UHD Smart webOS TV '
                                        '(2024)',
                                'price': '$549.99',
                                'rating': 'Rating 4.7 out of 5 stars with 79 reviews',
                                'sku': '6578181Rating',
                                'url': 'https://www.bestbuy.com/site/lg-55-class-80-series-qned-4k-uhd-smart-webos-tv-2024/6578181.p?skuId=6578181'}}],
            'sony': [{'model_no': 'KD75X77L',
                      'original_name': 'SONY 75" X77L 4K HDR LED TV Google TV - KD75X77L',
                      'bestbuy': {'found': True,
                                  'name': 'Sony - 75" Class X77L LED 4K UHD Smart Google TV (2023)',
                                  'price': '$799.99',
                                  'rating': 'Rating 4.7 out of 5 stars with 119 reviews',
                                  'sku': '6544129Rating',
                                  'url': 'https://www.bestbuy.com/site/sony-75-class-x77l-led-4k-uhd-smart-google-tv-2023/6544129.p?skuId=6544129'}}]}}