import struct

class XXTEA:
    """XXTEA encryption for MiniWorld"""
    
    DELTA = 0x9E3779B9
    
    @staticmethod
    def encrypt(data: bytes, key: bytes) -> bytes:
        if len(data) == 0:
            return data
        
        # Pad data
        pad_len = (8 - len(data) % 8) % 8
        data = data + b'\x00' * pad_len
        
        # Convert to uint32 array
        v = struct.unpack(f"<{len(data) // 4}I", data)
        k = struct.unpack("<4I", key.ljust(16, b'\x00')[:16])
        
        n = len(v)
        rounds = 6 + 52 // n
        
        y = v[0]
        z = v[-1]
        sum_val = 0
        
        for _ in range(rounds):
            sum_val = (sum_val + XXTEA.DELTA) & 0xFFFFFFFF
            e = (sum_val >> 2) & 3
            
            for p in range(n - 1):
                z = v[p + 1]
                y = v[p] = (v[p] + ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum_val ^ y) + (k[p & 3 ^ e] ^ z))) & 0xFFFFFFFF
            
            z = v[0]
            y = v[-1] = (v[-1] + ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum_val ^ y) + (k[(n - 1) & 3 ^ e] ^ z))) & 0xFFFFFFFF
        
        return struct.pack(f"<{n}I", *v)
    
    @staticmethod
    def decrypt(data: bytes, key: bytes) -> bytes:
        if len(data) == 0:
            return data
        
        v = struct.unpack(f"<{len(data) // 4}I", data)
        k = struct.unpack("<4I", key.ljust(16, b'\x00')[:16])
        
        n = len(v)
        rounds = 6 + 52 // n
        
        y = v[0]
        z = v[-1]
        sum_val = (rounds * XXTEA.DELTA) & 0xFFFFFFFF
        
        for _ in range(rounds):
            e = (sum_val >> 2) & 3
            
            for p in range(n - 1, 0, -1):
                z = v[p - 1]
                y = v[p] = (v[p] - ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum_val ^ y) + (k[p & 3 ^ e] ^ z))) & 0xFFFFFFFF
            
            z = v[-1]
            y = v[0] = (v[0] - ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum_val ^ y) + (k[e] ^ z))) & 0xFFFFFFFF
            sum_val = (sum_val - XXTEA.DELTA) & 0xFFFFFFFF
        
        result = struct.pack(f"<{n}I", *v)
        return result.rstrip(b'\x00')
