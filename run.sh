#!/bin/bash

# Check if Flask server is already running
if ! lsof -ti:5000; then
    # Clear port 5000
    kill $(lsof -t -i:5000)
    
    # Start Flask application
    python3 vnav_acquisition/webserver.py &
fi

# Navigate to your MUI/React application directory
cd front_app

# Install dependencies (if needed)
#pnpm install

# Start React application
pnpm start --open --port 5173
