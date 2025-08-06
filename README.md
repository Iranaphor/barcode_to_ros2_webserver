# Barcode to ROS2 WebServer
Repository to pipe barcode scans thorough a web server into ROS2.

To start the system:

```sh
# Set environment variables
export NGROK_AUTHTOKEN='enter your auth token here'
export NGROK_URL='enter-your-url-here.ngrok-free.app'
export ROS_DOMAIN_ID='enter your ros2 domain id here'
export BARCODE_ROS2_TOPIC_NAME='/your/ros2_topic/name/here'
```

```sh
# Build and run docker image
docker compose build --no-cache
docker compose up
```


# Run
On your phones web browser go to:
`https://$NGROK_URL/`

1. Plug a usb barcode scanner into your phone's usb port
2. Scan a QR code or barcode
3. You will see a line as below on the container's terminal

```
webapp-1  | [INFO] [1754489702.613275782] [web_publisher]: Published: "my_qr_code_text"
```

This should be accessible on your ROS2 humble terminal by echoing the topic it publishes to.

Note while this is designed for a barcode such as (THIS)[https://amzn.eu/d/edl1cSl], the webserver will also work with keyboard input, only sending what is typed once the carridge return is pressed.
