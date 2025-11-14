// Minimal Web Crypto helpers for PIN-derived AES-GCM encryption
// Exports: deriveKeyFromPIN(pin, room) -> CryptoKey
// encryptBuffer(buffer, key) -> { ivBase64, ciphertext }
// decryptBuffer(ivBase64, ciphertext, key) -> ArrayBuffer
// utils: blobToArrayBuffer

const P2PCrypto = (function() {
    const enc = new TextEncoder();

    async function sha256(data) {
        return await crypto.subtle.digest('SHA-256', data);
    }

    function arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        const chunkSize = 0x8000;
        let binary = '';
        for (let i = 0; i < bytes.length; i += chunkSize) {
            binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunkSize));
        }
        return btoa(binary);
    }

    function base64ToArrayBuffer(base64) {
        const binary = atob(base64);
        const len = binary.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes.buffer;
    }

    async function deriveKeyFromPIN(pin, room) {
        // room used as salt context (SHA-256(room))
        const salt = await sha256(enc.encode(String(room || 'nvgl8r')));
        const baseKey = await crypto.subtle.importKey(
            'raw',
            enc.encode(String(pin)),
            { name: 'PBKDF2' },
            false,
            ['deriveKey']
        );

        // iterations chosen for reasonable mobile perf; adjust if needed
        const iterations = 100000;

        const key = await crypto.subtle.deriveKey(
            {
                name: 'PBKDF2',
                salt: salt,
                iterations: iterations,
                hash: 'SHA-256'
            },
            baseKey,
            { name: 'AES-GCM', length: 256 },
            false,
            ['encrypt', 'decrypt']
        );
        return key;
    }

    async function encryptBuffer(buffer, key) {
        const iv = crypto.getRandomValues(new Uint8Array(12));
        const ct = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, buffer);
        return {
            ivBase64: arrayBufferToBase64(iv.buffer),
            ciphertext: ct // ArrayBuffer
        };
    }

    async function decryptBuffer(ivBase64, ciphertext, key) {
        const iv = base64ToArrayBuffer(ivBase64);
        const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: new Uint8Array(iv) }, key, ciphertext);
        return plain; // ArrayBuffer
    }

    async function blobToArrayBuffer(blob) {
        return await new Response(blob).arrayBuffer();
    }

    return {
        deriveKeyFromPIN,
        encryptBuffer,
        decryptBuffer,
        blobToArrayBuffer,
        arrayBufferToBase64,
        base64ToArrayBuffer
        // _internals: { arrayBufferToBase64, base64ToArrayBuffer }
    };
})();

// Export to global
window.P2PCrypto = P2PCrypto;
