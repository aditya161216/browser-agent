# import threading
# import queue
# from agent_browser import BrowserController

# class ThreadSafeBrowserWrapper:
#     def __init__(self):
#         self.command_queue = queue.Queue()
#         self.result_queue = queue.Queue()
        
#         # Start the browser thread
#         self.browser_thread = threading.Thread(target=self._browser_worker)
#         self.browser_thread.daemon = True
#         self.browser_thread.start()
    
#     def _browser_worker(self):
#         """This runs in its own thread and owns all browser/agent operations"""
#         # Import and initialize everything in THIS thread
#         from langchain_google_genai import ChatGoogleGenerativeAI
#         from langchain.agents import initialize_agent
#         from langchain.tools import Tool
#         from langgraph.prebuilt import create_react_agent
#         from langgraph.checkpoint.memory import InMemorySaver
#         from langchain_core.messages import HumanMessage
#         import os
        
#         # Create browser controller in this thread
#         browser = BrowserController()
        
#         # Create tools in this thread
#         tools = [
#             Tool(name="navigate", func=browser.navigate, description="Navigate to a website"),
#             Tool(name="click", func=browser.click, description="Click on something by its text"),
#             Tool(name="read_page", func=browser.get_text, description="Read the text content"),
#             Tool(name="search", func=browser.search, description="Search on current page"),
#             Tool(name="type_text", func=browser.type_text, description="Type text"),
#             Tool(name="press_enter", func=browser.press_enter, description="Press Enter key"),
#             Tool(name="extract_prices", func=browser.extract_prices, description="Extract prices"),
#             Tool(name="go_back", func=browser.go_back, description="Go back"),
#             Tool(name="screenshot", func=browser.screenshot, description="Take screenshot"),
#             Tool(name="handle_popups", func=browser.handle_popups, description="Handle popups"),
#             Tool(name="check_for_popups", func=browser.check_for_popups, description="Check popups"),
#             Tool(name="human_like_navigate", func=browser.human_like_navigate, description="Navigate human-like"),
#             Tool(name="human_like_click", func=browser.human_like_click, description="Click human-like"),
#             Tool(name="check_captcha", func=browser.check_for_captcha, description="Check CAPTCHA"),
#             Tool(name="handle_captcha", func=browser.handle_captcha_detection, description="Handle CAPTCHA"),
#         ]
        
#         # Create LLM and agent in this thread
#         llm = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash", 
#             google_api_key=os.getenv("GEMINI_API_KEY"), 
#             temperature=0
#         )
        
#         # agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

#         # gives agent memory
#         checkpointer = InMemorySaver()

#         agent = create_react_agent(
#             model=llm,
#             tools=tools,
#             checkpointer=checkpointer
#         )

#         config = {"configurable": {"thread_id": "1"}}

        
#         # Process commands
#         while True:
#             try:
#                 # Get command from queue
#                 command = self.command_queue.get(timeout=1)

                
#                 # Execute the command using the agent
#                 # result = agent.run(command)

#                 inputs = {"messages": [HumanMessage(content=command)]}

#                 result = agent.invoke(inputs, config)

#                 print("THIS IS THE RESULT: ", result)

#                 final_response = "Command executed"
#                 if result and 'messages' in result:
#                     for msg in reversed(result['messages']):
#                         # Look for the last AI message that has content
#                         if hasattr(msg, 'content') and msg.content and not isinstance(msg, HumanMessage):
#                             final_response = msg.content
#                             break

#                 print("FINAL RESPONSE: ", final_response)
                
#                 # Put result back
#                 self.result_queue.put({'success': True, 'result': final_response})
                
#             except queue.Empty:
#                 continue
#             except Exception as e:
#                 self.result_queue.put({'success': False, 'error': str(e)})
    
#     def execute_task(self, task_description):
#         """Thread-safe method to execute tasks"""
#         # Put command in queue
#         self.command_queue.put(task_description)
        
#         # Wait for result
#         try:
#             result = self.result_queue.get(timeout=60)  # 60 second timeout
#             if result['success']:
#                 return result['result']
#             else:
#                 raise Exception(result['error'])
#         except queue.Empty:
#             raise Exception("Command timed out")

# # Create global instance
# thread_safe_browser = ThreadSafeBrowserWrapper()


