import redis
import json
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
import os

load_dotenv()

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0
)

# these are proxy browser tools; essentially a fancy way of saying they push commands to the browser redis queue
# that will then be accessed by the browser process
def navigate_proxy(url: str) -> str:
    """Navigate to a URL"""
    browser_task_id = str(uuid.uuid4())
    
    # send to browser queue
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'navigate',
        'params': {'url': url}
    }))
    
    # wait for browser result
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Navigation timed out"

def click_proxy(text: str) -> str:
    """Click on element by text"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'click',
        'params': {'text': text}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Click timed out"

def read_page_proxy() -> str:
    """Read page content"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'read_page',
        'params': {}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Read page timed out"

def search_proxy(query: str) -> str:
    """Search on current page"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'search',
        'params': {'query': query}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Search timed out"

def extract_prices_proxy() -> str:
    """Extract prices from page"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'extract_prices',
        'params': {}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Extract prices timed out"


def type_text_proxy(text: str) -> str:
    """Type text into focused element"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'type_text',
        'params': {'text': text}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Type text timed out"

def press_enter_proxy() -> str:
    """Press Enter key"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'press_enter',
        'params': {}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Press enter timed out"

def go_back_proxy() -> str:
    """Go back to previous page"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'go_back',
        'params': {}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Go back timed out"

def screenshot_proxy(filename: str = "screenshot.png") -> str:
    """Take a screenshot"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'screenshot',
        'params': {'filename': filename}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Screenshot timed out"

def handle_popups_proxy() -> str:
    """Handle popups"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'handle_popups',
        'params': {}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Handle popups timed out"

def check_for_popups_proxy() -> str:
    """Check for popups"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'check_for_popups',
        'params': {}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Check popups timed out"

def human_like_navigate_proxy(url: str) -> str:
    """Navigate with human-like behavior"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'human_like_navigate',
        'params': {'url': url}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Human-like navigate timed out"

def human_like_click_proxy(text: str) -> str:
    """Click with human-like behavior"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'human_like_click',
        'params': {'text': text}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Human-like click timed out"

def check_captcha_proxy() -> str:
    """Check for CAPTCHA"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'check_captcha',
        'params': {}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Check CAPTCHA timed out"

def handle_captcha_proxy() -> str:
    """Handle CAPTCHA detection"""
    browser_task_id = str(uuid.uuid4())
    
    redis_client.lpush('browser_tasks', json.dumps({
        'id': browser_task_id,
        'action': 'handle_captcha',
        'params': {}
    }))
    
    result = redis_client.blpop(f'browser_result:{browser_task_id}', timeout=30)
    if result:
        return json.loads(result[1])['result']
    return "Handle CAPTCHA timed out"

# tools list using all proxy functions
tools = [
    Tool(
        name="navigate",
        func=navigate_proxy,
        description="Navigate to a website. Input should be a URL like amazon.com"
    ),
    Tool(
        name="click",
        func=click_proxy,
        description="Click on something by its text. Input should be the exact text to click."
    ),
    Tool(
        name="read_page",
        func=read_page_proxy,
        description="Read the current page content"
    ),
    Tool(
        name="search",
        func=search_proxy,
        description="Search for something on the current page. Input should be the search query."
    ),
    Tool(
        name="type_text",
        func=type_text_proxy,
        description="Type text into the currently focused element. Input should be the text to type."
    ),
    Tool(
        name="press_enter",
        func=press_enter_proxy,
        description="Press the Enter key"
    ),
    Tool(
        name="go_back",
        func=go_back_proxy,
        description="Go back to the previous page"
    ),
    Tool(
        name="extract_prices",
        func=extract_prices_proxy,
        description="Extract all prices from the current page"
    ),
    Tool(
        name="screenshot",
        func=screenshot_proxy,
        description="Take a screenshot of the current page. Optional: provide filename."
    ),
    Tool(
        name="handle_popups",
        func=handle_popups_proxy,
        description="Automatically handle cookie banners and popups blocking the page"
    ),
    Tool(
        name="check_for_popups",
        func=check_for_popups_proxy,
        description="Check if there are popups on the page"
    ),
    Tool(
        name="human_like_navigate",
        func=human_like_navigate_proxy,
        description="Navigate to a URL with human-like delays and mouse movements to avoid detection"
    ),
    Tool(
        name="human_like_click",
        func=human_like_click_proxy,
        description="Click on an element with human-like mouse movement and delays"
    ),
    Tool(
        name="check_captcha",
        func=check_captcha_proxy,
        description="Check if there's a CAPTCHA on the page"
    ),
    Tool(
        name="handle_captcha",
        func=handle_captcha_proxy,
        description="Alert user to manually solve CAPTCHA if one is detected"
    ),
]

# memory saver for conversation persistence
memory = MemorySaver()

# create langgraph agent
agent = create_react_agent(
    llm,
    tools,
    checkpointer=memory,
    # state_modifier="You are a helpful browser automation assistant. Break down complex tasks into steps and execute them one by one."
)

def main():
    print("Agent Worker Started - Waiting for tasks...")
    
    while True:
        try:
            # waits for a task in agent_tasks queue from either flask process or browser process
            task_data = redis_client.brpop('agent_tasks', timeout=1)
            
            if task_data:
                task = json.loads(task_data[1])
                task_id = task['id']
                command = task['command']
                
                print(f"Processing task {task_id}: {command}")
                
                # this allows for llm's memory retention
                config = {"configurable": {"thread_id": task_id}}
                
                # result = agent.invoke(
                #     {"messages": [HumanMessage(content=command)]},
                #     config
                # )

                result = agent.invoke(
                    {"messages": [
                        SystemMessage(content="You are a browser automation assistant. When given a command, you MUST use the appropriate browser tools to complete it. For example, 'open amazon' means you should use the navigate tool to go to amazon.com. Always execute the requested action using the available tools."),
                        HumanMessage(content=command)
                    ]},
                    config
                )

                # DEBUG
                print(f"Full agent result: {json.dumps(str(result), indent=2)}")
                
                # extract response
                final_response = "Task completed"
                if result and 'messages' in result:
                    for msg in reversed(result['messages']):
                        if hasattr(msg, 'content') and msg.content and not isinstance(msg, HumanMessage):
                            final_response = msg.content
                            break
                
                print(f"Task {task_id} complete: {final_response}")
                
                # send final result back to flask process
                redis_client.lpush(f'final_result:{task_id}', json.dumps({
                    'result': final_response
                }))
                
        except Exception as e:
            print(f"Error in agent worker: {e}")
            if 'task_id' in locals():
                redis_client.lpush(f'final_result:{task_id}', json.dumps({
                    'result': f'Error: {str(e)}'
                }))

if __name__ == "__main__":
    main()