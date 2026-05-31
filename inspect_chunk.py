"""Inspect a real cached chunk file to understand FlatBuffers chunk format."""
import sys
import lzma
import struct

if len(sys.argv) < 2:
    sys.argv.append(r"C:\Users\PC\AppData\Roaming\miniworddata110\data\cachetrunk\1015\w72954558563850_0_27_0_575139e71a9672f294b4b5edcbf0a14c")

path = sys.argv[1]
with open(path, "rb") as f:
    raw = f.read()

print(f"File: {path}")
print(f"Total size: {len(raw)} bytes")
print(f"First 16 bytes: {raw[:16].hex()}")

# LZMA raw format: [5B props][8B uncomp_size LE][compressed]
# But miniworld's "src + 5" suggests no size prefix, just props.
# That's "LZMA streamed without size" — needs lzma1 format with FORMAT_ALONE.
props = raw[:5]
print(f"Props bytes: {props.hex()}")
print(f"  preset byte: 0x{props[0]:02x}")
print(f"  dict size LE: 0x{int.from_bytes(props[1:5], 'little'):x} ({int.from_bytes(props[1:5], 'little')})")

# Try lzma decompression
# Method 1: LZMA1 alone format (with 8B size field of -1)
header_alone = props + b'\xff' * 8  # unknown size
try:
    decompressor = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
    decompressed = decompressor.decompress(header_alone + raw[5:])
    print(f"\n[LZMA-alone] Decompressed: {len(decompressed)} bytes")
    print(f"First 64 bytes: {decompressed[:64].hex()}")
    print(f"ASCII view: {bytes((c if 32 <= c < 127 else ord('.') for c in decompressed[:64])).decode()}")

    # Try parsing as FlatBuffers
    if len(decompressed) >= 8:
        root_offset = int.from_bytes(decompressed[:4], 'little')
        print(f"\nFlatBuffers analysis:")
        print(f"  root_offset (data[0:4] LE): {root_offset}")
        if root_offset < len(decompressed):
            vtable_offset_neg = int.from_bytes(decompressed[root_offset:root_offset+4], 'little', signed=True)
            print(f"  *(root_offset)/vtable_offset signed: {vtable_offset_neg}")
            vtable_addr = root_offset - vtable_offset_neg
            print(f"  vtable_addr = root_offset - vtable_offset = {vtable_addr}")
            if 0 <= vtable_addr < len(decompressed) - 4:
                vtable_size = int.from_bytes(decompressed[vtable_addr:vtable_addr+2], 'little')
                inline_size = int.from_bytes(decompressed[vtable_addr+2:vtable_addr+4], 'little')
                print(f"  vtable_size: {vtable_size}, inline_size: {inline_size}")
                print(f"  vtable[0..]: ", end="")
                for i in range(2, min(vtable_size // 2, 20)):
                    val = int.from_bytes(decompressed[vtable_addr + i*2:vtable_addr + i*2 + 2], 'little')
                    print(f"vtable[{i-2}]={val} ", end="")
                print()

    out_path = path + ".decompressed"
    with open(out_path, "wb") as f:
        f.write(decompressed)
    print(f"\nSaved decompressed to: {out_path}")
except Exception as e:
    print(f"[LZMA-alone] failed: {e}")

    # Method 2: try with miniworld-style stream (no size, requires custom filter)
    try:
        filters = [
            {"id": lzma.FILTER_LZMA1, "preset": 6}
        ]
        decompressor = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=filters)
        decompressed = decompressor.decompress(raw[5:])
        print(f"\n[LZMA-raw] Decompressed: {len(decompressed)} bytes")
        print(f"First 64 bytes: {decompressed[:64].hex()}")
    except Exception as e2:
        print(f"[LZMA-raw] failed: {e2}")
