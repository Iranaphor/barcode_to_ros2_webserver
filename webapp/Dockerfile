FROM ros:humble

# Install pip and tools
RUN apt update && apt install -y python3-pip curl unzip tree

# Install Python packages
WORKDIR /webapp
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy app and static files
COPY app.py .
COPY static/ static/

# Install ngrok
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
    apt update && apt install -y ngrok

# Launch script will run both Flask and ngrok
COPY launch.sh .

# Display current file heirarchy
RUN echo "====== Docker context file tree ======" && tree /webapp

# Setup NGrok auth
ARG NGROK_AUTHTOKEN
RUN ngrok config add-authtoken $NGROK_AUTHTOKEN

EXPOSE 5000
CMD ["bash", "launch.sh"]
