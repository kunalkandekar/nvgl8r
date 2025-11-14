# Nvgl8r aka BratCam
Minimal web app for periodic webcam capture and remote monitoring. The project supports two modes:

- Server-backed mode (original): capture pages upload photos to the bundled Python server which stores a small rolling set of images.
- P2P mode (new): capture pages send encrypted images directly to monitor pages using WebRTC (no server storage). This uses a small local library `p2pcf.js` and a PIN-based symmetric key.

See `./.github/copilot-instructions.md` for implementation details and design notes.

WARNING: This project favors simplicity. It is not production-grade security — only use in trusted environments.

Note: This is not very secure by design to overindex on simplicity, not due to any shortcoming of the AI (or, as the AI autocomplete helpfully suggested, "not because I'm lazy.")

## Quickstart — server-backed mode (existing)

THIS IS HORRIBLY INSECURE DO NOT USE OUTSIDE OF A TRUSTED ENVIRONMENT

1. Clone this repository
2. Run the bundled Python server (serves static files and accepts uploads):

```bash
python3 server.py --port 8888 --password <LONG_RANDOM_STRING>
```

3. On the capture device (mobile), open `http://<your-server-ip>:8888/capture.html` and enter the password when prompted. The capture page will begin taking photos and uploading them to the server.
4. On a monitoring device, open `http://<your-server-ip>:8888/monitor.html` and enter the same password to view the latest images.

## P2P mode (serverless, preferred for direct peer-to-peer)
P2P mode replaces server uploads with a direct WebRTC data channel between the capture page and one or more monitor pages. Images are symmetrically encrypted using a key derived from a user-provided PIN and a room name.

This is entirely implemented using P2PCF, source and license here: https://github.com/gfodor/p2pcf

Technically you still need a server to host the HTML files. CloudFlare would be a good idea given it's free and easy and also used by P2PCF.

Prerequisites
- Place a compatible `p2pcf.js` (the project demo library) into the `static/` directory so it is served as `/p2pcf.js`.

How to use
1. On the capture device, open `http://<your-host>:8888/capture.html`.
2. Enter a human-readable Room name (this is how monitors find the host) and an alphanumeric PIN. Click "Start Capture & Advertise". Allow camera access.
3. On the monitoring device, open `http://<your-host>:8888/monitor.html`, enter the same Room and PIN, and click Connect.
4. When a monitor connects, the capture page will periodically (every 30–60 seconds) capture a 640x480 JPEG, encrypt it using an AES-GCM key derived from PIN+Room, and send it over the WebRTC data channel to connected peers.

Security notes
- The PIN is the only secret used to derive the encryption key. Use sufficiently long alphanumeric PINs to increase safety.
- AES-GCM 256 is used with a random IV per image; the IV is sent in plaintext in the message header.
- P2P mode avoids storing images on the server but still requires signaling/STUN to successfully form peer connections across NATs. If peers cannot connect, try devices on the same LAN or configure STUN/TURN in your `p2pcf.js`.

Behavior differences vs server-backed mode
- No server-side storage or authentication is required for P2P mode — instead, the user supplies a Room and a PIN.
- There is no fallback to server uploads; if peers never connect, images are not delivered.

## Files of interest
- `static/capture.html` — capture UI; now supports P2P host mode with Room+PIN.
- `static/monitor.html` — monitor UI; now supports P2P client mode with Room+PIN.
- `static/p2p-crypto.js` — Web Crypto wrappers used by both pages to derive keys and perform AES-GCM encryption/decryption.
- `static/p2pcf.js` — (not included) the local P2P signaling/WRTC helper. Put it in `static/`.
- `server.py` — simple Python static server and upload handler (still present if you want server-backed mode).

## Troubleshooting
- If `p2pcf.js` is missing or uses a different API than the demo, open your browser console on both pages — the startup scripts include informative messages and small adapter wrappers. If needed, paste your `p2pcf.js` API and the helper can be adapted.
- If decryption fails on the monitor, verify the PIN matches exactly (case-sensitive) and the room is the same.
- If no peer connection forms, try both devices on the same local network to rule out NAT/STUN issues.

## Development
The project is designed to be edited directly in the `static/` files; minimal build tooling is required.
