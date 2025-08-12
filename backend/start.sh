#!/bin/bash
# Kill any existing processes
pkill -f "python app.py"
pkill -f "python agent_worker.py"
pkill -f "python browser_worker.py"

# Make sure Redis is running first
brew services start redis

# Give Redis a moment to start
sleep 2

# Start all processes
python app.py &
python agent_worker.py &
python browser_worker.py &

echo "All services started! Press Ctrl+C to stop all."
wait