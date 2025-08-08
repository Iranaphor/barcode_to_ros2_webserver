import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from flask import Flask, request, render_template_string
from flask import send_from_directory
import os
import threading

app = Flask(__name__)
rclpy.init()

class WebPublisher(Node):
    def __init__(self):
        super().__init__('web_publisher')
        rdi = os.getenv('ROS_DOMAIN_ID')
        topic_name = os.getenv('BARCODE_ROS2_TOPIC_NAME')
        self.publisher = self.create_publisher(String, topic_name, 10)
        self.get_logger().info(f'Publishing on ROS Domain: {rdi}')
        self.get_logger().info(f'Publishing on topic name: {topic_name}')

    def publish_text(self, text):
        msg = String()
        msg.data = text
        self.get_logger().info(f'Published: "{text}"')
        self.publisher.publish(msg)

node = WebPublisher()

# Run ROS spin in a thread
def ros_spin():
    rclpy.spin(node)

threading.Thread(target=ros_spin, daemon=True).start()

HTML = '''
<!DOCTYPE html>
<html>
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/sw.js').then(() => {
      console.log("Service worker registered");
    }).catch(err => {
      console.warn("Service worker registration failed", err);
    });
  }
</script>
<head>
  <title>ROS2 Input</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <link rel="manifest" href="/static/manifest.json">
  <link rel="icon" href="/static/icon-192.png">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="theme-color" content="#ffffff">

  <script>
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/static/sw.js');
    }
  </script>

  <style>
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
      background: #fff;
      color: #000;
      font-family: monospace;
      font-weight: bold;
      font-size: 24px;
      overflow: hidden;
    }
    #container {
      display: flex;
      flex-direction: column;
      height: 100%;
    }
    #log {
      flex: 1;
      padding: 10px;
      overflow-y: auto;
      white-space: pre-wrap;
      box-sizing: border-box;
    }
    #display {
      background: #eee;
      border-top: 2px solid #000;
      padding: 10px;
      height: 40px;
      outline: none;
      box-sizing: border-box;
    }
    #fullscreenPrompt {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(255,255,255,0.9);
      color: #000;
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: 24px;
      text-align: center;
      padding: 40px;
      box-sizing: border-box;
      z-index: 10;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <div id="fullscreenPrompt" onclick="enterFullscreen()">Tap anywhere to enter fullscreen</div>
  <div id="container">
    <div id="log"></div>
    <div id="display" tabindex="0"></div>
  </div>

  <script>
      let buffer = "";
      const display = document.getElementById("display");
      const log = document.getElementById("log");

      // Wake Lock API
      let wakelock = null;

      function getOrCreateUUID() {
        let uuid = localStorage.getItem('uuid');
        if (!uuid) {
          uuid = crypto.randomUUID();
          localStorage.setItem('uuid', uuid);
        }
        return uuid;
      }

      const uuid = getOrCreateUUID();

      async function enableWakeLock() {
        try {
          wakelock = await navigator.wakeLock.request('screen');
          console.log('Wake Lock enabled');
        } catch (err) {
          console.error('Wake Lock error:', err);
        }
      }

      function forceFocus() {
        if (document.activeElement !== display) {
          display.focus();
        }
      }

      // Enter fullscreen and enable wakelock
      function enterFullscreen() {
        const elem = document.documentElement;
        if (elem.requestFullscreen) {
          elem.requestFullscreen();
        } else if (elem.webkitRequestFullscreen) {
          elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) {
          elem.msRequestFullscreen();
        }
        document.getElementById("fullscreenPrompt").style.display = "none";
        enableWakeLock();  // enable wakelock here
        forceFocus();
      }

      // Events that trigger focus / wakelock
      window.onload = forceFocus;
      display.addEventListener("blur", () => setTimeout(forceFocus, 10));
      document.addEventListener("visibilitychange", () => {
        if (!document.hidden) {
          setTimeout(forceFocus, 10);
          enableWakeLock();  // re-request wakelock if resumed
        }
      });

      document.addEventListener("click", e => {
        if (document.getElementById("fullscreenPrompt").style.display !== "none") return;
        e.preventDefault();
        forceFocus();
        enableWakeLock();
      });

      document.addEventListener("touchstart", e => {
        if (document.getElementById("fullscreenPrompt").style.display !== "none") return;
        e.preventDefault();
        forceFocus();
        enableWakeLock();
      });

      //Input logic
      document.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
          event.preventDefault();
          const text = buffer.trim();
          if (text.length > 0) {
            fetch("/submit", {
              method: "POST",
              headers: { "Content-Type": "application/x-www-form-urlencoded" },
              body: "text=" + encodeURIComponent(text) + "&uuid=" + encodeURIComponent(uuid)
            }).then(() => {
              const line = document.createElement("div");
              line.textContent = text;
              log.appendChild(line);
              log.scrollTop = log.scrollHeight;
              buffer = "";
              display.textContent = "";
            });
          }
        } else if (event.key === "Backspace") {
          buffer = buffer.slice(0, -1);
          display.textContent = buffer;
        } else if (event.key.length === 1) {
          buffer += event.key;
          display.textContent = buffer;
        }
      });
    </script>
  </body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/submit', methods=['POST'])
def submit():
    text = request.form['text']
    uuid = request.form.get('uuid', 'unknown')
    node.publish_text(f'{uuid}~{text}')
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
