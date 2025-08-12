# from langchain_google_genai import ChatGoogleGenerativeAI
# from playwright.sync_api import sync_playwright
# from playwright.async_api import async_playwright
# from langchain.tools import Tool
# from langchain.agents import initialize_agent
# from langgraph.prebuilt import create_react_agent
# from langgraph.checkpoint.memory import MemorySaver
# from dotenv import load_dotenv
# import os
# import random
# import time

# load_dotenv()

# gemini_key = os.getenv("GEMINI_API_KEY")

# # contains tools to navigate browsers
# class BrowserController:
#     async def __init__(self, use_profile=True) -> None:
#         self.playwright = await async_playwright().start()
#         self.browser = await self.playwright.chromium.launch(headless=False)
#         self.page = await self.browser.new_page()

#     # navigates to a given page
#     async def navigate(self, url):
#         if not url.startswith(('http://', 'https://')):
#             url = 'https://' + url
    
#         # Navigate to the page
#         self.page.goto(url)
        
#         # Wait for page to load
#         self.page.wait_for_load_state('domcontentloaded')
        
#         # Automatically try to handle popups
#         self.handle_popups()
        
#         return f"Navigated to {url}. Page title is: {self.page.title()}"

#     # clicks on a certain element on the page
#     async def click(self, text):
#         try:
#             # First attempt
#             self.page.click(f"text={text}", timeout=5000)
#             return f"Clicked on '{text}'"
#         except:
#             # Maybe a popup is blocking it?
#             self.handle_popups()
            
#             try:
#                 # Try again after handling popups
#                 self.page.click(f"text={text}", timeout=5000)
#                 return f"Clicked on '{text}' (after handling popups)"
#             except:
#                 # Try different selectors
#                 selectors = [
#                     f"text={text}",
#                     f"*:has-text('{text}')",
#                     f"button:has-text('{text}')",
#                     f"a:has-text('{text}')",
#                 ]
                
#                 for selector in selectors:
#                     try:
#                         self.page.click(selector, timeout=2000)
#                         return f"Clicked on '{text}' using fallback selector"
#                     except:
#                         continue
                
#                 return f"Could not find '{text}' to click (even after handling popups)"

#     # gets all visible text on a page (query param is there in case langchain tries to pass context into function)
#     async def get_text(self, query: str = "") -> str:
#         text = self.page.inner_text("body")
#         truncated_text = (
#             text[:500] + "..." if len(text) > 500 else text
#         )  # return first 500 chars for now
#         print(truncated_text)
#         return truncated_text

#     # search for something on the current page
#     async def search(self, query: str) -> str:
#         try:
#             # try to find a search box and type
#             search_box = self.page.locator(
#                 "input[type='search'], input[type='text'], input[placeholder*='search' i]"
#             ).first
#             search_box.fill(query)
#             search_box.press("Enter")
#             return f"Searched for '{query}'"
#         except:
#             return f"Could not find search box"

#     # closes the page
#     async def close_page(self):
#         self.page.close()
#         self.browser.close()

#     async def type_text(self, text: str) -> str:
#         """Type text into the currently focused element"""
#         try:
#             self.page.keyboard.type(text)
#             return f"Typed: '{text}'"
#         except Exception as e:
#             return f"Failed to type: {str(e)}"

#     async def press_enter(self, _: str = "") -> str:
#         """Press the Enter key"""
#         self.page.keyboard.press("Enter")
#         return "Pressed Enter"

#     async def go_back(self, _: str = "") -> str:
#         """Go back to previous page"""
#         self.page.go_back()
#         return "Went back to previous page"

#     async def extract_prices(self, _: str = "") -> str:
#         """Extract all prices from the current page"""
#         try:
#             # Common price patterns
#             price_elements = self.page.locator(
#                 "span:has-text('$'), div:has-text('$'), .price, .a-price"
#             ).all()
#             prices = []
#             for elem in price_elements[:10]:  # First 10 prices
#                 text = elem.inner_text()
#                 if "$" in text:
#                     prices.append(text.strip())
#             return f"Found prices: {', '.join(prices)}" if prices else "No prices found"
#         except:
#             return "Could not extract prices"

#     async def screenshot(self, filename: str = "screenshot.png") -> str:
#         """Take a screenshot"""
#         self.page.screenshot(path=filename)
#         return f"Screenshot saved as {filename}"
    
#     async def handle_popups(self, _: str = "") -> str:
#         """Automatically handle common popups and cookie banners"""
#         handled = []
        
#         # Common popup patterns to look for
#         popup_patterns = [
#             # Cookie banners
#             {"text": ["Accept", "Accept all", "Accept cookies", "Accept all cookies", "I agree", "Got it"], "type": "cookie"},
#             {"text": ["Continue", "Continue to site", "Proceed"], "type": "continue"},
#             {"text": ["No thanks", "Not now", "Maybe later", "Skip"], "type": "skip"},
#             {"text": ["X", "×", "Close", "Dismiss"], "type": "close"},
#         ]
        
#         for pattern in popup_patterns:
#             for text in pattern["text"]:
#                 try:
#                     # Look for visible buttons/links with this text
#                     element = self.page.locator(f"button:has-text('{text}'), a:has-text('{text}')").first
#                     if element.is_visible(timeout=1000):
#                         element.click()
#                         handled.append(f"{pattern['type']}: '{text}'")
#                         # Wait a bit for popup to disappear
#                         self.page.wait_for_timeout(500)
#                 except:
#                     continue
        
#         return f"Handled popups: {', '.join(handled)}" if handled else "No popups found"

#     async def check_for_popups(self, _: str = "") -> str:
#         """Check if there are any popups blocking the page"""
#         # Common indicators of popups
#         popup_indicators = [
#             "cookie", "consent", "accept", "privacy", "subscribe", 
#             "newsletter", "notification", "popup", "modal", "overlay"
#         ]
        
#         page_text = self.page.inner_text('body').lower()
#         found_indicators = [ind for ind in popup_indicators if ind in page_text]
        
#         if found_indicators:
#             return f"Possible popups detected related to: {', '.join(found_indicators)}"
#         return "No obvious popups detected"
    
#     async def human_like_navigate(self, url):
#         """Navigate with human-like behavior"""
        
#         # Random delay before navigation (humans don't navigate instantly)
#         time.sleep(random.uniform(0.5, 2.0))
        
#         self.page.goto(url)
        
#         # Random delay after page load
#         time.sleep(random.uniform(1.0, 3.0))
        
#         # Random mouse movement
#         self.page.mouse.move(
#             random.randint(100, 500),
#             random.randint(100, 500)
#         )
        
#         return f"Navigated to {url} (human-like)"

#     async def human_like_click(self, text):
#         """Click with human-like behavior"""
#         import random
#         import time
        
#         try:
#             element = self.page.locator(f"text={text}").first
            
#             # Move mouse to element slowly
#             box = element.bounding_box()
#             self.page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
            
#             # Small delay before click
#             time.sleep(random.uniform(0.1, 0.5))
            
#             element.click()
#             return f"Clicked on '{text}' (human-like)"
#         except:
#             return f"Could not find '{text}'"
        
#     async def check_for_captcha(self, _: str = "") -> str:
#         """Check if there's a CAPTCHA blocking us"""
#         captcha_indicators = [
#             "I'm not a robot",
#             "I am not a robot", 
#             "reCAPTCHA",
#             "Verify you are human",
#             "Select all images",
#             "Security check",
#             "captcha"
#         ]
        
#         page_text = self.page.inner_text('body').lower()
        
#         for indicator in captcha_indicators:
#             if indicator.lower() in page_text:
#                 return "CAPTCHA_DETECTED"
        
#         # Also check for reCAPTCHA iframe
#         try:
#             if self.page.frame_locator("iframe[src*='recaptcha']").count() > 0:
#                 return "CAPTCHA_DETECTED"
#         except:
#             pass
        
#         return "No CAPTCHA detected"

#     async def handle_captcha_detection(self, _: str = "") -> str:
#         """Alert user when CAPTCHA is detected"""
#         if self.check_for_captcha() == "CAPTCHA_DETECTED":
#             print("\n⚠️  CAPTCHA DETECTED - Manual intervention required!")
#             print("Please solve the CAPTCHA manually, then press Enter to continue...")
#             input()
#             return "User solved CAPTCHA manually"
#         return "No CAPTCHA found"

