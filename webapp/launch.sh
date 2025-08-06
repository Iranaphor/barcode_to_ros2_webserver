#!/bin/bash
set -e

# Start Flask app in background
python3 app.py &

# Wait briefly for Flask to start
sleep 2

# Start ngrok in background
ngrok http --url=$NGROK_URL 5000 > /dev/null &

# Wait for ngrok to start and expose the tunnel
sleep 3

# Print the public HTTPS URL
echo "🌍 Your public HTTPS URL is:"
curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*'
echo "📱 Open this on your Android phone to install the PWA"

# Keep the container running
tail -f /dev/null
