# barcode_to_ros2_webserver
Repository to pipe barcode scans thorough a web server into ROS2.

To start the system:

```sh
# Set environment variables
export NGROK_AUTHTOKEN='enter your auth token here'
export NGROK_URL='enter-your-url-here.ngrok-free.app'
export ROS_DOMAIN_ID='enter your ros2 domain id here'
```

```sh
# Build and run docker image
docker compose build --no-cache
docker compose up
```
