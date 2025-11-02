# Nvgl8r aka BratCam
Basic web application that uses the webcamera to take pictures at semi-regular intervals and upload them to a server. The application is designed to be used as an invigilator to ensure your brats are studying and not goofing off.

Almost fully agentically vibe-coded.

See the copilot-instructions for design and implementation details.

THIS IS HORRIBLY INSECURE DO NOT USE OUTSIDE OF A TRUSTED ENVIRONMENT

# Instructions
1. Clone this repository
2. Run the server on a publicly accessible server: python3 server.py --port 8888 --password <LONG_RANDOM_STRING>
3. Position the mobile device intended to be the BratCam to capture the brats' study area
4. Open the capture.html page in a browser on the mobile device and enter the password above when prompted (username is admin but doesn't really matter.)
5. The application will start capturing and uploading photos
6. Open the monitor page at http://<your-server-ip>:8888/monitor.html
7. Log in using the same username/password
