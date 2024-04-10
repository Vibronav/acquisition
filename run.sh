#!/bin/bash

# Start Flask application
python3 vnav_acquisition/webserver.py &

# Navigate to your MUI/React application directory
cd front_app

# Install dependencies (if needed)
# npm install

# Start React application
npm start
