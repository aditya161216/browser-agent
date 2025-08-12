# 🤖 Browser Agent - Natural Language Browser Automation

An intelligent browser automation system that allows users to control their web browser using natural language commands through a Chrome extension. Built with a microservices architecture using Python, LangChain, and Redis.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-🦜-green.svg)
![Redis](https://img.shields.io/badge/Redis-7.0+-red.svg)
![Playwright](https://img.shields.io/badge/Playwright-1.40+-purple.svg)

## 🌟 Features

- **Natural Language Control**: Control your browser with commands like "Go to Amazon and search for laptops"
- **Chrome Extension Interface**: User-friendly popup for entering commands
- **AI-Powered Decision Making**: Uses Google's Gemini model to interpret commands and execute browser actions
- **Distributed Architecture**: Scalable microservices design with Redis message queuing
- **Smart Browser Automation**: Handles popups, CAPTCHAs detection, human-like interactions
- **Session Management**: Maintains conversation context across multiple commands

## 🏗️ Architecture

The system uses a distributed microservices architecture to ensure scalability and separation of concerns.

### Components:

1. **Chrome Extension**: User interface for natural language input
2. **Flask API Server**: RESTful API that receives commands and returns results
3. **Redis Message Queue**: Enables asynchronous communication between services
4. **Agent Worker**: LangGraph agent that interprets commands and decides actions
5. **Browser Worker**: Executes browser automation using Playwright
