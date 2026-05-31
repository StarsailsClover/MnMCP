#!/usr/bin/env python3
"""Test crypto modules."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing crypto modules...")

# Test AES-GCM
from mn2mc.crypto.aes_gcm import aes_gcm_encrypt, aes_gcm_decrypt
key = b'0123456789abcdef'
nonce = b'0123456789ab'
plaintext = b'Hello WPKG!'

ciphertext, tag = aes_gcm_encrypt(key, nonce, plaintext)
decrypted = aes_gcm_decrypt(key, nonce, ciphertext, tag)

assert decrypted == plaintext, "AES-GCM decryption failed!"
print("✓ AES-GCM OK")

# Test HKDF
from mn2mc.crypto.hkdf import derive_wpkg_keys, derive_session_material
shared_secret = b'x' * 32  # 32 bytes
material = derive_session_material(shared_secret)
assert len(material) == 48, "HKDF output wrong length!"
print("✓ HKDF OK")

aes_key, nonce_base = derive_wpkg_keys(shared_secret)
assert len(aes_key) == 16, "AES key wrong length!"
assert len(nonce_base) == 12, "Nonce base wrong length!"
print("✓ WPKG key derivation OK")

# Test ECDH
from mn2mc.crypto.ecdh import generate_keypair, compute_shared_secret
priv1, pub1 = generate_keypair()
priv2, pub2 = generate_keypair()

shared1 = compute_shared_secret(priv1, pub2)
shared2 = compute_shared_secret(priv2, pub1)

assert shared1 == shared2, "ECDH shared secrets don't match!"
assert len(shared1) == 32, "ECDH shared secret wrong length!"
print("✓ ECDH OK")

# Test WPKG
from mn2mc.protocol.wpkg import WPKGHeader, WPKGCodec

# Test header encoding/decoding
header = WPKGHeader(
    cmd_id=1,
    seq_no=100,
    body_len=50
)
header_bytes = header.to_bytes()
assert len(header_bytes) == 16, "Header wrong length!"

decoded = WPKGHeader.from_bytes(header_bytes)
assert decoded.cmd_id == 1, "Header cmd_id mismatch!"
assert decoded.seq_no == 100, "Header seq_no mismatch!"
print("✓ WPKG Header OK")

# Test full encode/decode
from mn2mc.crypto.aes_gcm import generate_nonce

session_key = b'0123456789abcdef'
payload = b'{"cmd": "test", "data": "hello"}'

encoded = WPKGCodec.encode(1, 1, payload, session_key)
assert len(encoded) > 16 + 12 + 16, "Encoded packet too short!"

decoded_header, decoded_payload = WPKGCodec.decode(encoded, session_key)
assert decoded_payload == payload, "WPKG decode mismatch!"
print("✓ WPKG Codec OK")

print("\n" + "="*40)
print("All crypto tests PASSED!")
print("="*40)
