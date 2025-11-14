# AI Agent Instructions for Nvgl8r

This document provides essential context for AI coding agents working with the Nvgl8r codebase.

## Project Overview

Nvgl8r is a small web-based webcam capture and monitoring application. It supports two primary modes:
- Server-backed mode: capture pages upload photos to a simple Python server which stores a small rolling set of images.
- P2P mode: capture pages send encrypted images directly to connected monitor pages using WebRTC (no server-side storage).

This file describes both the original server-based architecture and the newer P2P additions so agents understand how to modify or extend either mode.

## Architecture Components

### 1. Photo Capture Frontend (server-backed, deprecated)
- Single page web app using vanilla JavaScript
- Uses `getUserMedia` API for webcam access
- Implements canvas-based image capture (640x480 recommended for mobile compatibility)
- AJAX-based image upload to server
- Random interval timing (historically 1-5 minutes; server-backed still supported)
- Wake lock API to prevent device sleep
- Mobile-first responsive design

### 1b. Photo Capture Frontend (P2P)
- Optional serverless capture mode: the capture page can advertise a Room and send encrypted images directly to monitor peers via WebRTC.
- Requires a local `p2pcf.js` helper (not bundled) that handles signalling/peer discovery. Place `p2pcf.js` into the `static/` folder so pages can load it as `/p2pcf.js`.
- Uses `static/p2p-crypto.js` to derive a symmetric AES-GCM key from a user-provided PIN and the Room name (PBKDF2 with SHA-256) and to encrypt image bytes client-side.
- Capture frequency in the P2P flow is 30–60 seconds by default (configurable in `capture.html`). Images are 640x480 JPEGs at reduced quality to keep payloads small.

### 2. Python Server
- Handles both static file serving and photo uploads (server-backed mode)
- Uses built-in Python libraries for HTTP handling
- Serves static HTML/JS files from filesystem
- Manages photo storage with a configurable rolling size
- Tracks most recent photo number in memory
- Simple endpoints for upload and static content

### 2b. P2P Signal/Relay (p2pcf)
- For P2P mode, `p2pcf.js` is responsible for signalling and peer discovery (the project does not bundle a signalling server).
- Ensure the `p2pcf.js` you provide supports STUN/TURN configuration if peers must traverse NATs.

### 3. Photo Monitor Frontend (server-backed)
- Horizontally scrollable display of last 5 photos
- Fetches latest photo number from server and loads N..N-4
- Real-time updates via periodic polling

### 3b. Photo Monitor Frontend (P2P)
- Joins a Room and connects to a capture peer via `p2pcf.js`.
- Derives the AES-GCM key using the user-supplied PIN + Room (same derivation as capture page) using `p2p-crypto.js`.
- Receives encrypted image messages via WebRTC DataChannel, decrypts them, and displays them in the horizontal scroller UI.
- If decryption fails, the monitor should surface an explanatory error (likely due to wrong PIN or mismatched Room).

## Development Workflows

### Authentication (server-backed)
- Auth for server-backed mode is implemented at server level using Basic Auth with a salted password hash.

### Photo Management
- Server-backed: server maintains a rolling set of photos with simple numbered filenames and overwrites the oldest entries.
- P2P: no server storage. Images are held in memory by clients and displayed on monitors as they arrive.

## Cross-Component Communication

### Frontend → Server
- Photo upload: AJAX POST with image data
- Photo retrieval: Fetch API GET requests

### Frontend → Peer (P2P)
- Capture → Monitor: Encrypted binary image payloads are sent over an ordered reliable WebRTC DataChannel.
- Message format (simple): send a small JSON header as a text message describing the image (type:'img', id, iv, mime, size), followed by the ciphertext as a binary message. The header contains the base64-encoded IV required for AES-GCM decryption.

## Project Conventions

### Security
- Server-backed mode: all requests are authenticated with Basic Auth. Sensitive server endpoints should be protected and validated.
- P2P mode: encryption depends entirely on the user-supplied PIN; choose long PINs for better security. AES-GCM-256 is used for image encryption.

### Frontend Design
- Vanilla JavaScript, no frameworks
- Native browser APIs (getUserMedia, canvas, fetch, Web Crypto)
- Mobile-first responsive design

### Implementation Notes
- Server uses only Python standard library (http.server, base64, os.path, mimetypes, etc.)
- `p2p-crypto.js` implements PBKDF2 (HMAC-SHA256) key derivation and AES-GCM encrypt/decrypt helpers for use by capture and monitor pages.
- Keep JPEG dimensions and quality tuned to keep DataChannel payloads small; implement chunking/reassembly only if necessary.

### File Organization
- `static/`
  - `capture.html` - Photo capture page (supports server-backed and P2P host mode)
  - `monitor.html` - Photo viewing page (supports server-backed and P2P client mode)
  - `p2p-crypto.js` - Web Crypto helpers (PBKDF2 + AES-GCM wrappers)
  - `p2pcf.js` - (not bundled) local P2P signalling/connection helper — place in `static/`
- `photos/` - Photo storage directory (server-backed)
- `server.py` - Python server script
  - Accepts password hash via command line
  - Loads static files from filesystem
  - Maintains photo recency in memory (server-backed mode)
