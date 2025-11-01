# AI Agent Instructions for Nvgl8r

This document provides essential context for AI coding agents working with the Nvgl8r codebase.

## Project Overview

Nvgl8r is a web-based surveillance application that:
- Captures photos from a webcam at random intervals (1-5 minutes)
- Uploads photos to a zero-dependency Python server
- Provides a mobile-friendly monitoring interface to view recent photos
- Designed for simplicity and minimal resource usage

## Architecture Components

### 1. Photo Capture Frontend
- Single page web app using vanilla JavaScript
- Uses `getUserMedia` API for webcam access
- Implements canvas-based image capture (640x480 recommended for mobile compatibility)
- AJAX-based image upload to server
- Random interval timing between 1-5 minutes
- Wake lock API to prevent device sleep
- Mobile-first responsive design

### 2. Python Server
- Handles both static file serving and photo uploads
- Uses built-in Python libraries for HTTP handling
- Serves static HTML/JS files from filesystem
- Manages photo storage with 10-photo limit
- Accepts auth credentials via command line args
- Implements basic auth with salted password hashing

### 3. Photo Monitor Frontend
- Horizontally scrollable display of last 5 photos
- Uses Fetch API for photo retrieval
- Real-time photo updates
- Touch-friendly swipe navigation

## Development Workflows

### Authentication
- Auth is implemented at server level using basic auth
- Credentials are hardcoded in server script
- All endpoints (web pages and API) require authentication

### Photo Management
- Server maintains max 10 photos on filesystem
- Simple numbered naming (photo1.jpg through photo10.jpg)
- Photo recency tracking in server memory
- Oldest photos overwritten based on memory state
- Last 5 photos served to monitor page

## Cross-Component Communication

### Frontend → Server
- Photo upload: AJAX POST with image data
- Photo retrieval: Fetch API GET requests
- All requests must include basic auth headers

### Data Flow
1. Webcam capture → Canvas conversion
2. Canvas data → AJAX upload
3. Server storage → File system
4. File system → Monitor page display

## Project Conventions

### Security
- All endpoints require authentication
- Password stored as salted hash in server code
- Basic auth headers required for all requests
- Alternative simple security options:
  - Time-based tokens (server memory only)
  - IP-based allowlisting for trusted networks
  - Shared secret in URL path (for simpler clients)

### Frontend Design
- Vanilla JavaScript, no frameworks
- Native browser APIs (getUserMedia, canvas, fetch)
- Mobile-first responsive design
- Simple horizontal scroll for photo viewing

### Implementation Notes
- Server uses only Python standard library
  - http.server for web serving
  - base64 for auth encoding
  - io for image handling
- Memory-only state management
  - Photo recency tracking in memory
  - Current auth tokens/sessions
  - No database needed
- Project structure
  - Static HTML/JS in separate files
  - Python server script
  - Command-line configuration
- Basic mobile optimizations
  - Compressed JPEG format
  - Client-side image resizing

### File Organization
- `static/`
  - `capture.html` - Photo capture page
  - `monitor.html` - Photo viewing page
  - `common.js` - Shared JavaScript utilities
- `photos/` - Photo storage directory
- `server.py` - Python server script
  - Accepts password hash via command line
  - Loads static files from filesystem
  - Maintains photo recency in memory