from langchain_google_genai import ChatGoogleGenerativeAI
from playwright.sync_api import sync_playwright
from langchain.tools import Tool
from langchain.agents import initialize_agent
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os
import random
import time

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")

# contains tools to navigate browsers
class BrowserController:
    def __init__(self, use_profile=True) -> None:
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()

    # navigates to a given page
    def navigate(self, url):
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
    
        # Navigate to the page
        self.page.goto(url)
        
        # Wait for page to load
        self.page.wait_for_load_state('domcontentloaded')
        
        # Automatically try to handle popups
        self.handle_popups()
        
        return f"Navigated to {url}. Page title is: {self.page.title()}"

    # clicks on a certain element on the page
    def click(self, text):
        try:
            # First attempt
            self.page.click(f"text={text}", timeout=5000)
            return f"Clicked on '{text}'"
        except:
            # Maybe a popup is blocking it?
            self.handle_popups()
            
            try:
                # Try again after handling popups
                self.page.click(f"text={text}", timeout=5000)
                return f"Clicked on '{text}' (after handling popups)"
            except:
                # Try different selectors
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
                
                return f"Could not find '{text}' to click (even after handling popups)"

    # gets all visible text on a page (query param is there in case langchain tries to pass context into function)
    def get_text(self, query: str = "") -> str:
        text = self.page.inner_text("body")
        truncated_text = (
            text[:500] + "..." if len(text) > 500 else text
        )  # return first 500 chars for now
        print(truncated_text)
        return truncated_text

    # search for something on the current page
    def search(self, query: str) -> str:
        try:
            # try to find a search box and type
            search_box = self.page.locator(
                "input[type='search'], input[type='text'], input[placeholder*='search' i]"
            ).first
            search_box.fill(query)
            search_box.press("Enter")
            return f"Searched for '{query}'"
        except:
            return f"Could not find search box"

    # closes the page
    def close_page(self):
        self.page.close()
        self.browser.close()

    def type_text(self, text: str) -> str:
        """Type text into the currently focused element"""
        try:
            self.page.keyboard.type(text)
            return f"Typed: '{text}'"
        except Exception as e:
            return f"Failed to type: {str(e)}"

    def press_enter(self, _: str = "") -> str:
        """Press the Enter key"""
        self.page.keyboard.press("Enter")
        return "Pressed Enter"

    def go_back(self, _: str = "") -> str:
        """Go back to previous page"""
        self.page.go_back()
        return "Went back to previous page"

    def extract_prices(self, _: str = "") -> str:
        """Extract all prices from the current page"""
        try:
            # Common price patterns
            price_elements = self.page.locator(
                "span:has-text('$'), div:has-text('$'), .price, .a-price"
            ).all()
            prices = []
            for elem in price_elements[:10]:  # First 10 prices
                text = elem.inner_text()
                if "$" in text:
                    prices.append(text.strip())
            return f"Found prices: {', '.join(prices)}" if prices else "No prices found"
        except:
            return "Could not extract prices"

    def screenshot(self, filename: str = "screenshot.png") -> str:
        """Take a screenshot"""
        self.page.screenshot(path=filename)
        return f"Screenshot saved as {filename}"
    
    def handle_popups(self, _: str = "") -> str:
        """Automatically handle common popups and cookie banners"""
        handled = []
        
        # Common popup patterns to look for
        popup_patterns = [
            # Cookie banners
            {"text": ["Accept", "Accept all", "Accept cookies", "Accept all cookies", "I agree", "Got it"], "type": "cookie"},
            {"text": ["Continue", "Continue to site", "Proceed"], "type": "continue"},
            {"text": ["No thanks", "Not now", "Maybe later", "Skip"], "type": "skip"},
            {"text": ["X", "×", "Close", "Dismiss"], "type": "close"},
        ]
        
        for pattern in popup_patterns:
            for text in pattern["text"]:
                try:
                    # Look for visible buttons/links with this text
                    element = self.page.locator(f"button:has-text('{text}'), a:has-text('{text}')").first
                    if element.is_visible(timeout=1000):
                        element.click()
                        handled.append(f"{pattern['type']}: '{text}'")
                        # Wait a bit for popup to disappear
                        self.page.wait_for_timeout(500)
                except:
                    continue
        
        return f"Handled popups: {', '.join(handled)}" if handled else "No popups found"

    def check_for_popups(self, _: str = "") -> str:
        """Check if there are any popups blocking the page"""
        # Common indicators of popups
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
        """Navigate with human-like behavior"""
        
        # Random delay before navigation (humans don't navigate instantly)
        time.sleep(random.uniform(0.5, 2.0))
        
        self.page.goto(url)
        
        # Random delay after page load
        time.sleep(random.uniform(1.0, 3.0))
        
        # Random mouse movement
        self.page.mouse.move(
            random.randint(100, 500),
            random.randint(100, 500)
        )
        
        return f"Navigated to {url} (human-like)"

    def human_like_click(self, text):
        """Click with human-like behavior"""
        import random
        import time
        
        try:
            element = self.page.locator(f"text={text}").first
            
            # Move mouse to element slowly
            box = element.bounding_box()
            self.page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
            
            # Small delay before click
            time.sleep(random.uniform(0.1, 0.5))
            
            element.click()
            return f"Clicked on '{text}' (human-like)"
        except:
            return f"Could not find '{text}'"
        
    def check_for_captcha(self, _: str = "") -> str:
        """Check if there's a CAPTCHA blocking us"""
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
        
        # Also check for reCAPTCHA iframe
        try:
            if self.page.frame_locator("iframe[src*='recaptcha']").count() > 0:
                return "CAPTCHA_DETECTED"
        except:
            pass
        
        return "No CAPTCHA detected"

    def handle_captcha_detection(self, _: str = "") -> str:
        """Alert user when CAPTCHA is detected"""
        if self.check_for_captcha() == "CAPTCHA_DETECTED":
            print("\n⚠️  CAPTCHA DETECTED - Manual intervention required!")
            print("Please solve the CAPTCHA manually, then press Enter to continue...")
            input()
            return "User solved CAPTCHA manually"
        return "No CAPTCHA found"


browser = BrowserController()

# the tools we provide our agent with
tools = [
    Tool(
        name="navigate",
        func=browser.navigate,
        description="Navigate to a website. Input should be a URL like google.com",
    ),
    Tool(
        name="click",
        func=browser.click,
        description="Click on something by its text. Input should be the exact text to click.",
    ),
    Tool(
        name="read_page",
        func=browser.get_text,
        description="Read the text content of the current page",
    ),
    Tool(
        name="search",
        func=browser.search,
        description="Search for something on the current page",
    ),
    Tool(
        name="type_text",
        func=browser.type_text,
        description="Type text into focused element",
    ),
    Tool(name="press_enter", func=browser.press_enter, description="Press Enter key"),
    Tool(
        name="extract_prices",
        func=browser.extract_prices,
        description="Extract prices from page",
    ),
    Tool(name="go_back", func=browser.go_back, description="Go back to previous page"),
    Tool(name="screenshot", func=browser.screenshot, description="Take a screenshot"),
    Tool(
        name="handle_popups",
        func=browser.handle_popups,
        description="Handle cookie banners and popups blocking the page"
    ),
    Tool(
        name="check_for_popups",
        func=browser.check_for_popups,
        description="Check if there are popups on the page"
    ),
    Tool(
    name="human_like_navigate",
    func=browser.human_like_navigate,
    description="Navigate to a URL with human-like delays and mouse movements to avoid detection"
    ),
    Tool(
        name="human_like_click",
        func=browser.human_like_click,
        description="Click on an element with human-like mouse movement and delays"
    ),
    Tool(
        name="check_captcha",
        func=browser.check_for_captcha,
        description="Check if there's a CAPTCHA on the page"
    ),
    Tool(
        name="handle_captcha",
        func=browser.handle_captcha_detection,
        description="Alert user to manually solve CAPTCHA if one is detected"
    ),
]

# initialize llm
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", google_api_key=gemini_key, temperature=0
)

# our current agent
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)


# executes tasks using the agent
def execute_complex_task(task_description):
    """
    Convert natural language to agent commands
    Examples:
    - "Find the cheapest laptop on Amazon"
    - "Check the weather in San Francisco"
    - "What's the top story on CNN?"
    """
    return agent.run(task_description)
