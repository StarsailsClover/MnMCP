# Troubleshooting - No mitmproxy Output

## Issue

- Proxifier shows connections
- mitmproxy shows no output
- Possible causes:
  1. Certificate not trusted by application
  2. Application bypassing proxy
  3. mitmproxy not intercepting correctly

## Solution: Check Proxifier Log

Please check what Proxifier shows:
- What IPs/ports is minigameapp.exe connecting to?
- Are connections going through proxy?
- Any errors?

## Alternative: Use mitmweb (GUI version)

mitmweb provides a web interface to see traffic more clearly.

Let me start mitmweb instead...
