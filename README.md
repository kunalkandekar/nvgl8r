# Nvgl8r
Basic web application that uses the webcamera to take pictures at semi-regular intervals and upload them to a server. The application is designed to be used in a variety of settings, including security, surveillance, and monitoring.

# Components
This has only three components:
- A photo capture web page, which is a simple HTML page that uses JavaScript to access the web camera and take pictures.
- A web page to view the pictures, which is a simple HTML page that displays the last 5 pictures in a grid.
- A server that serves the HTML pages and receives the pictures, which is a simple Python script that saves the pictures to a directory on the server.

# Design
## Photo Capture Page
The photo capture page is a simple HTML page that uses JavaScript to access the web camera and take pictures. The page uses the `getUserMedia` API to access the web camera and the `canvas` element to capture the images. Pictures are taken at semi-regular intervals, with the interval being a random number between 1 minute and 5 minutes. The images are then sent to the server using an AJAX request.

## Server
The server is a simple Python script that serves the static HTML pages as well as an endpoint that receives the pictures and saves them to a directory on the server. The server uses inbuilt libraries to handle the HTTP requests and save the files. The server also cleans up old pictures when the count exceeds 10.

## Photo Monitor Page
The web page to view pictures is a simple HTML page that displays the last 5 pictures in a grid. The page uses the `fetch` API to retrieve the pictures from the server and display them in the grid.

# Authentication
The application uses extremely basic authentication to protect both web pages and the endpoint. The authentication is done using a simple username and password, which is hardcoded in the server script. The user is prompted to enter the username and password when they access the web pages or the endpoint. The password is stored in the server script as a salted hash.
