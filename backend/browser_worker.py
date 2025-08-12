import redis
import json
from playwright.sync_api import sync_playwright
import random
import time
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

class BrowserController:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()

    def navigate(self, url):
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        self.page.goto(url)
        self.page.wait_for_load_state('domcontentloaded')
        
        # automatically try to handle popups
        self.handle_popups()
        
        return f"Navigated to {url}. Page title is: {self.page.title()}"

    def click(self, text):
        try:
            self.page.click(f"text={text}", timeout=5000)
            return f"Clicked on '{text}'"
        except:
            self.handle_popups()
            
            try:
                self.page.click(f"text={text}", timeout=5000)
                return f"Clicked on '{text}' (after handling popups)"
            except:
                selectors = [
                    f"text={text}",
                    f"*:has-text('{text}')",
                    f"button:has-text('{text}')",
                    f"a:has-text('{text}')",
                ]
                
                for selector in selectors:
                    try:
                        self.page.click(selector, timeout=2000)
                        return f"Clicked on '{text}' using fallback selector"
                    except:
                        continue
                
                return f"Could not find '{text}' to click"

    def get_text(self, query=""):
        text = self.page.inner_text("body")
        truncated_text = text[:500] + "..." if len(text) > 500 else text
        return truncated_text

    def search(self, query):
        try:
            search_box = self.page.locator(
                "input[type='search'], input[type='text'], input[placeholder*='search' i]"
            ).first
            search_box.fill(query)
            search_box.press("Enter")
            return f"Searched for '{query}'"
        except:
            return "Could not find search box"

    def type_text(self, text):
        try:
            self.page.keyboard.type(text)
            return f"Typed: '{text}'"
        except Exception as e:
            return f"Failed to type: {str(e)}"

    def press_enter(self):
        self.page.keyboard.press("Enter")
        return "Pressed Enter"

    def go_back(self):
        self.page.go_back()
        return "Went back to previous page"

    def extract_prices(self):
        try:
            price_elements = self.page.locator(
                "span:has-text('$'), div:has-text('$'), .price, .a-price"
            ).all()
            prices = []
            for elem in price_elements[:10]:
                text = elem.inner_text()
                if "$" in text:
                    prices.append(text.strip())
            return f"Found prices: {', '.join(prices)}" if prices else "No prices found"
        except:
            return "Could not extract prices"

    def screenshot(self, filename="screenshot.png"):
        self.page.screenshot(path=filename)
        return f"Screenshot saved as {filename}"
    
    def handle_popups(self):
        handled = []
        
        popup_patterns = [
            {"text": ["Accept", "Accept all", "Accept cookies", "Accept all cookies", "I agree", "Got it"], "type": "cookie"},
            {"text": ["Continue", "Continue to site", "Proceed"], "type": "continue"},
            {"text": ["No thanks", "Not now", "Maybe later", "Skip"], "type": "skip"},
            {"text": ["X", "×", "Close", "Dismiss"], "type": "close"},
        ]
        
        for pattern in popup_patterns:
            for text in pattern["text"]:
                try:
                    element = self.page.locator(f"button:has-text('{text}'), a:has-text('{text}')").first
                    if element.is_visible(timeout=1000):
                        element.click()
                        handled.append(f"{pattern['type']}: '{text}'")
                        self.page.wait_for_timeout(500)
                except:
                    continue
        
        return f"Handled popups: {', '.join(handled)}" if handled else "No popups found"

    def check_for_popups(self):
        popup_indicators = [
            "cookie", "consent", "accept", "privacy", "subscribe", 
            "newsletter", "notification", "popup", "modal", "overlay"
        ]
        
        page_text = self.page.inner_text('body').lower()
        found_indicators = [ind for ind in popup_indicators if ind in page_text]
        
        if found_indicators:
            return f"Possible popups detected related to: {', '.join(found_indicators)}"
        return "No obvious popups detected"
    
    def human_like_navigate(self, url):
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        time.sleep(random.uniform(0.5, 2.0))
        
        self.page.goto(url)
        
        time.sleep(random.uniform(1.0, 3.0))
        
        self.page.mouse.move(
            random.randint(100, 500),
            random.randint(100, 500)
        )
        
        return f"Navigated to {url} (human-like)"

    def human_like_click(self, text):
        try:
            element = self.page.locator(f"text={text}").first
            
            box = element.bounding_box()
            self.page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
            
            time.sleep(random.uniform(0.1, 0.5))
            
            element.click()
            return f"Clicked on '{text}' (human-like)"
        except:
            return f"Could not find '{text}'"
        
    def check_for_captcha(self):
        captcha_indicators = [
            "I'm not a robot",
            "I am not a robot", 
            "reCAPTCHA",
            "Verify you are human",
            "Select all images",
            "Security check",
            "captcha"
        ]
        
        page_text = self.page.inner_text('body').lower()
        
        for indicator in captcha_indicators:
            if indicator.lower() in page_text:
                return "CAPTCHA_DETECTED"
        
        try:
            if self.page.frame_locator("iframe[src*='recaptcha']").count() > 0:
                return "CAPTCHA_DETECTED"
        except:
            pass
        
        return "No CAPTCHA detected"

    def handle_captcha_detection(self):
        if self.check_for_captcha() == "CAPTCHA_DETECTED":
            print("\n⚠️  CAPTCHA DETECTED - Manual intervention required!")
            print("Please solve the CAPTCHA manually, then press Enter to continue...")
            input()
            return "User solved CAPTCHA manually"
        return "No CAPTCHA found"

    def close_page(self):
        self.page.close()
        self.browser.close()


def main():
    print("Browser Worker Started - Initializing browser...")
    browser = BrowserController()
    print("Browser ready - Waiting for tasks...")
    
    while True:
        try:
            # wait for task to appear in browser_tasks queue (tasks will be given by agent worker)
            task_data = redis_client.brpop('browser_tasks', timeout=1)
            
            if task_data:
                # Parse task
                task = json.loads(task_data[1])
                task_id = task['id']
                action = task['action']
                params = task.get('params', {})
                
                print(f"Executing {action} (task {task_id})")
                
                # execute appropriate browser action
                result = None
                
                if action == 'navigate':
                    result = browser.navigate(params.get('url'))
                
                elif action == 'click':
                    result = browser.click(params.get('text'))
                
                elif action == 'read_page':
                    result = browser.get_text()
                
                elif action == 'search':
                    result = browser.search(params.get('query'))
                
                elif action == 'type_text':
                    result = browser.type_text(params.get('text'))
                
                elif action == 'press_enter':
                    result = browser.press_enter()
                
                elif action == 'go_back':
                    result = browser.go_back()
                
                elif action == 'extract_prices':
                    result = browser.extract_prices()
                
                elif action == 'screenshot':
                    result = browser.screenshot(params.get('filename', 'screenshot.png'))
                
                elif action == 'handle_popups':
                    result = browser.handle_popups()
                
                elif action == 'check_for_popups':
                    result = browser.check_for_popups()
                
                elif action == 'human_like_navigate':
                    result = browser.human_like_navigate(params.get('url'))
                
                elif action == 'human_like_click':
                    result = browser.human_like_click(params.get('text'))
                
                elif action == 'check_captcha':
                    result = browser.check_for_captcha()
                
                elif action == 'handle_captcha':
                    result = browser.handle_captcha_detection()
                
                else:
                    result = f"Unknown action: {action}"
                
                print(f"Task {task_id} result: {result}")
                
                # send result back to agent worker
                redis_client.lpush(f'browser_result:{task_id}', json.dumps({
                    'result': result
                }))
                
        except Exception as e:
            print(f"Error in browser worker: {e}")
            if 'task_id' in locals():
                redis_client.lpush(f'browser_result:{task_id}', json.dumps({
                    'result': f'Error: {str(e)}'
                }))

if __name__ == "__main__":
    main()