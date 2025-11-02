#!/usr/bin/env python3

import argparse
import base64
import datetime
import hashlib
import http.server
import json
import mimetypes
import os
import sys
import time
import urllib.request
from urllib.parse import parse_qs, urlparse

class PhotoServer(http.server.SimpleHTTPRequestHandler):
    # Class variables for photo management
    MAX_PHOTOS = 5
    PHOTOS_DIR = os.path.abspath('photos')
    STATIC_DIR = os.path.abspath('static')
    photos = []  # List of photo filenames from newest (0) to oldest (9)
    relay_target = None  # Tuple of (host, port) for relay server

    def __init__(self, *args, password_hash=None, **kwargs):
        self.password_hash = password_hash
        super().__init__(*args, **kwargs)

    @classmethod
    def cleanup_photos(cls):
        """Remove all photos from the photos directory"""
        if os.path.exists(cls.PHOTOS_DIR):
            for filename in os.listdir(cls.PHOTOS_DIR):
                if filename.endswith('.jpg'):
                    try:
                        os.remove(os.path.join(cls.PHOTOS_DIR, filename))
                    except Exception as e:
                        print(f"Error removing photo {filename}: {e}", file=sys.stderr)
                        pass
        cls.photos = []  # Reset photo list

    @classmethod
    def rotate_photos(cls, new_filename):
        """
        Adds a new photo to the front of the list and removes oldest if needed.
        """
        # If we've reached max photos, remove the oldest
        if len(cls.photos) >= cls.MAX_PHOTOS:
            try:
                oldest = cls.photos.pop()
                delete_path = os.path.join(cls.PHOTOS_DIR, oldest)
                print(f"Deleting oldest photo: {delete_path}")
                os.remove(delete_path)
            except Exception as e:
                print(f"Error removing oldest photo {oldest}: {e}", file=sys.stderr)
                pass  # Ignore cleanup errors

        # Add new photo at the start (position 0)
        cls.photos.insert(0, new_filename)

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Nvgl8r"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if not self.authenticate():
            return

        # Parse the URL
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Serve static files and photos
        if path.startswith('/photos/'):
            try:
                # Extract photo position from path (e.g., /photos/0.jpg -> 0)
                pos = int(os.path.splitext(os.path.basename(path))[0])
                if 0 <= pos < len(self.photos):
                    file_path = os.path.join(self.__class__.PHOTOS_DIR, self.photos[pos])
                else:
                    self.send_error(404, "Photo not found")
                    return
            except (ValueError, IndexError):
                self.send_error(400, "Invalid photo number")
                return
        else:
            # Default to serving from static directory
            if path == '/monitor.html':
                file_path = os.path.join(self.__class__.STATIC_DIR, 'monitor.html')
            elif path == '/capture.html':
                file_path = os.path.join(self.__class__.STATIC_DIR, 'capture.html')
            else:
                file_path = os.path.join(self.__class__.STATIC_DIR, path.lstrip('/'))

        # Validate the path
        if not self.is_valid_path(file_path):
            self.send_error(403, "Forbidden")
            return

        try:
            with open(file_path, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', self.guess_type(file_path))
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404, "File not found")
        except Exception as e:
            self.send_error(500, "Internal server error")

    def do_POST(self):
        if not self.authenticate():
            return

        if self.path == '/upload':
            content_length = int(self.headers['Content-Length'])
            photo_data = self.rfile.read(content_length)

            # Use simple numbered filename based on current time
            filename = f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.jpg"
            photo_path = os.path.join(self.__class__.PHOTOS_DIR, filename)
            print('Writing to ', photo_path)

            try:
                if self.__class__.relay_target:
                    # Relay the photo to another server
                    host, port = self.__class__.relay_target
                    url = f'http://{host}:{port}/upload'
                    request = urllib.request.Request(
                        url,
                        data=photo_data,
                        headers={
                            'Content-Type': 'image/jpeg',
                            'Authorization': self.headers.get('Authorization', '')
                        }
                    )
                    with urllib.request.urlopen(request) as response:
                        if response.status != 200:
                            raise Exception(f"Relay failed with status {response.status}")
                else:
                    # Save the photo locally
                    with open(photo_path, 'wb') as f:
                        f.write(photo_data)
                    # Rotate photos (adds new photo and removes oldest if needed)
                    self.__class__.rotate_photos(filename)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
            except Exception as e:
                # Cleanup on error
                if not self.__class__.relay_target:
                    try:
                        os.remove(photo_path)
                    except:
                        pass
                self.send_error(500, f"Failed to handle photo: {str(e)}")
        else:
            self.send_error(404, "Endpoint not found")

    def authenticate(self):
        auth_header = self.headers.get('Authorization')
        if not auth_header:
            self.do_AUTHHEAD()
            return False

        try:
            auth_decoded = base64.b64decode(auth_header.split()[1]).decode()
            username, password = auth_decoded.split(':')
            if self.verify_password(password):
                return True
        except Exception:
            pass

        self.do_AUTHHEAD()
        return False

    def verify_password(self, password):
        if not self.password_hash:
            return False
        salt = self.password_hash[:32]  # First 32 chars are salt
        return self.password_hash == salt + hashlib.sha256((salt + password).encode()).hexdigest()

    def is_valid_path(self, path):
        """Validate file path to prevent directory traversal"""
        base_path = os.path.abspath(os.path.dirname(path))
        requested_path = os.path.abspath(path)
        return (requested_path.startswith(self.__class__.STATIC_DIR) or
                requested_path.startswith(self.__class__.PHOTOS_DIR)) and \
               os.path.splitext(path)[1].lower() in ['.html', '.js', '.jpg']

    def guess_type(self, path):
        """Guess the type of a file based on its extension"""
        return mimetypes.guess_type(path)[0] or 'application/octet-stream'

def generate_password_hash(password):
    """Generate a salted password hash"""
    salt = os.urandom(16).hex()
    return salt + hashlib.sha256((salt + password).encode()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description='Start the photo server')
    parser.add_argument('--port', type=int, default=8888, help='Port to listen on')
    parser.add_argument('--password', required=True, help='Password for authentication')
    parser.add_argument('--relay', help='Relay photos to another server (format: host:port)')
    args = parser.parse_args()

    # Generate password hash
    password_hash = generate_password_hash(args.password)

    # Set up relay target if specified
    if args.relay:
        try:
            host, port = args.relay.split(':')
            PhotoServer.relay_target = (host, int(port))
            print(f"Will relay photos to {host}:{port}")
        except Exception as e:
            print(f"Invalid relay target {args.relay}: {str(e)}", file=sys.stderr)
            sys.exit(1)

    # Ensure required directories exist
    os.makedirs('static', exist_ok=True)
    if not PhotoServer.relay_target:
        os.makedirs('photos', exist_ok=True)
        # Clean up any existing photos
        PhotoServer.cleanup_photos()

    # Create handler with password hash
    handler = lambda *args, **kwargs: PhotoServer(*args, password_hash=password_hash, **kwargs)

    # Start server
    server = http.server.HTTPServer(('', args.port), handler)
    print(f'Server started on port {args.port}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down...')
        if not PhotoServer.relay_target:
            PhotoServer.cleanup_photos()  # Clean up photos on shutdown
        server.server_close()

if __name__ == '__main__':
    main()
