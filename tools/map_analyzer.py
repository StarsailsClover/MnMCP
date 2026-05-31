# -*- coding: utf-8 -*-
"""
MiniWorld Map Full Analyzer
Parses ALL map data from local saves and network captures.
Reports everything parseable and flags unknowns.
"""
import struct
import zlib
import json
import os
import sys
import hashlib
from pathlib import Path
from collections import defaultdict

REPORT = []
UNKNOWNS = []

def log(msg):
    print(msg)
    REPORT.append(msg)

def unknown(category, detail):
    msg = f"[UNKNOWN] {category}: {detail}"
    print(msg)
    UNKNOWNS.append(msg)
    REPORT.append(msg)

# ============================================================
# FlatBuffers minimal parser
# ============================================================
def parse_flatbuf_header(data):
    if len(data) < 8:
        return None
    root_offset = struct.unpack_from('<I', data, 0)[0]
    return {"root_offset": root_offset, "size": len(data)}

def parse_fb_table(data, offset):
    """Parse a FlatBuffers table at given offset"""
    if offset + 4 > len(data):
        return {}
    vtable_offset = struct.unpack_from('<i', data, offset)[0]
    vtable_pos = offset - vtable_offset
    if vtable_pos < 0 or vtable_pos + 4 > len(data):
        return {"_error": "vtable out of bounds"}
    vtable_size = struct.unpack_from('<H', data, vtable_pos)[0]
    table_size = struct.unpack_from('<H', data, vtable_pos + 2)[0]
    num_fields = (vtable_size - 4) // 2
    fields = {}
    for i in range(num_fields):
        field_offset = struct.unpack_from('<H', data, vtable_pos + 4 + i * 2)[0]
        if field_offset:
            abs_offset = offset + field_offset
            if abs_offset + 4 <= len(data):
                raw = struct.unpack_from('<I', data, abs_offset)[0]
                fields[i] = {"offset": abs_offset, "raw_uint32": raw}
    return {"vtable_size": vtable_size, "table_size": table_size, "num_fields": num_fields, "fields": fields}

# ============================================================
# Region file (.r) parser
# ============================================================
def parse_region_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    result = {
        "path": str(filepath),
        "size": len(data),
        "sections": [],
        "data_blocks": [],
    }

    # Parse header as varints
    pos = 0
    header_varints = []
    for _ in range(5):
        val = 0
        shift = 0
        while pos < len(data) and pos < 20:
            b = data[pos]
            val |= (b & 0x7F) << shift
            pos += 1
            shift += 7
            if (b & 0x80) == 0:
                break
        header_varints.append(val)
    result["header_varints"] = header_varints
    result["header_bytes"] = pos

    # Parse 128-byte section table
    section_start = pos
    section_count = 0
    sections = []
    while section_start + 128 <= len(data):
        record = data[section_start:section_start + 128]
        is_empty = all(b == 0 for b in record)
        if is_empty:
            sections.append({"index": section_count, "empty": True, "offset": section_start})
        else:
            first2 = record[0:2].hex()
            last16 = record[112:128]
            sections.append({
                "index": section_count,
                "empty": False,
                "offset": section_start,
                "first2": first2,
                "first16_hex": record[:16].hex(),
                "last16_hex": last16.hex(),
            })
        section_count += 1
        section_start += 128
        # Stop if we've gone past reasonable section table
        if section_count > 1000:
            break

    # Detect where section table ends (transition to actual data)
    # The section table is followed by chunk data
    # Heuristic: sections stop when we find a block that doesn't follow the pattern
    result["section_count"] = section_count
    result["sections_summary"] = {
        "total": section_count,
        "non_empty": sum(1 for s in sections if not s["empty"]),
        "empty": sum(1 for s in sections if s["empty"]),
    }

    # Analyze first-byte patterns
    first_byte_counts = defaultdict(int)
    for s in sections:
        if not s["empty"]:
            fb = s["first2"][:2]
            first_byte_counts[fb] += 1
    result["section_first_byte_dist"] = dict(first_byte_counts)

    # Try to decompress data after section table
    data_start = pos + section_count * 128
    result["data_region_start"] = data_start
    result["data_region_size"] = len(data) - data_start

    # Try various decompression on data region
    if data_start < len(data):
        chunk = data[data_start:data_start + min(65536, len(data) - data_start)]
        # Try zlib
        try:
            decompressed = zlib.decompress(chunk)
            result["data_compression"] = "zlib"
            result["data_decompressed_size"] = len(decompressed)
        except:
            pass

        # Try zstd
        try:
            import zstandard as zstd
            dctx = zstd.ZstdDecompressor()
            decompressed = dctx.decompress(chunk, max_output_size=1024*1024)
            result["data_compression"] = "zstd"
            result["data_decompressed_size"] = len(decompressed)
        except ImportError:
            result["zstd_note"] = "zstandard not installed"
        except:
            pass

        if "data_compression" not in result:
            # Try raw deflate (no header)
            try:
                decompressed = zlib.decompress(chunk, -15)
                result["data_compression"] = "raw_deflate"
                result["data_decompressed_size"] = len(decompressed)
            except:
                pass

        if "data_compression" not in result:
            unknown("region_compression", f"Cannot decompress data region at offset {data_start}, first 32B: {chunk[:32].hex()}")

    return result

# ============================================================
# Actor file (.a) parser
# ============================================================
def parse_actor_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()

    result = {
        "path": str(filepath),
        "size": len(data),
        "first32_hex": data[:32].hex() if data else "",
    }

    # Check if FlatBuffers
    if len(data) >= 8:
        root_off = struct.unpack_from('<I', data, 0)[0]
        if 4 <= root_off < len(data):
            result["format_guess"] = "flatbuffers"
            result["root_offset"] = root_off
            table = parse_fb_table(data, root_off)
            result["root_table"] = table
        else:
            result["format_guess"] = "unknown"
            unknown("actor_format", f"{filepath}: root_offset={root_off}, not valid FB")

    return result

# ============================================================
# World descriptor files
# ============================================================
def parse_fb_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    result = {
        "path": str(filepath),
        "size": len(data),
        "first32_hex": data[:32].hex() if len(data) >= 32 else data.hex(),
    }
    if len(data) >= 8:
        result["fb_header"] = parse_flatbuf_header(data)
        root_off = struct.unpack_from('<I', data, 0)[0]
        if 4 <= root_off < len(data):
            result["root_table"] = parse_fb_table(data, root_off)
    return result

def parse_raw_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    result = {
        "path": str(filepath),
        "size": len(data),
        "hex": data.hex() if len(data) <= 64 else data[:64].hex() + "...",
    }
    if len(data) == 4:
        result["as_uint32"] = struct.unpack_from('<I', data, 0)[0]
    elif len(data) == 8:
        result["as_uint64"] = struct.unpack_from('<Q', data, 0)[0]
    return result

# ============================================================
# Network PACKDATA analyzer
# ============================================================
def analyze_pcap_packdata(pcap_path, host_ip, phone_ip):
    try:
        from scapy.all import rdpcap, UDP, IP, Raw
    except ImportError:
        unknown("pcap", "scapy not installed")
        return None

    packets = rdpcap(pcap_path)
    results = {
        "total_udp": 0,
        "packdata_packets": [],
        "reassembled": {},
        "other_game_packets": [],
    }

    split_buffers = {}

    for pkt in packets:
        if not pkt.haslayer(UDP) or not pkt.haslayer(Raw):
            continue
        raw = bytes(pkt[Raw].load)
        if not raw or not (0x80 <= raw[0] <= 0x8f):
            continue
        ip = pkt[IP]
        if not ((ip.src == host_ip and ip.dst == phone_ip) or
                (ip.src == phone_ip and ip.dst == host_ip)):
            continue
        results["total_udp"] += 1

        # Parse RakNet frame
        pos = 4
        while pos < len(raw):
            if pos >= len(raw):
                break
            flags = raw[pos]; pos += 1
            rel = (flags >> 5) & 7
            has_split = bool(flags & 0x10)
            if pos + 2 > len(raw): break
            bit_len = struct.unpack_from('>H', raw, pos)[0]; pos += 2
            byte_len = (bit_len + 7) // 8
            if rel in (2, 3, 4, 6, 7): pos += 3
            if rel in (1, 4): pos += 3
            if rel in (1, 3, 4, 7): pos += 4

            split_count = 0
            split_id = 0
            split_index = 0
            if has_split:
                if pos + 10 > len(raw): break
                split_count = struct.unpack_from('>I', raw, pos)[0]
                split_id = struct.unpack_from('>H', raw, pos + 4)[0]
                split_index = struct.unpack_from('>I', raw, pos + 6)[0]
                pos += 10

            if pos + byte_len > len(raw):
                payload = raw[pos:]
            else:
                payload = raw[pos:pos + byte_len]
            pos += byte_len

            if not payload or payload[0] != 0x89:
                continue

            direction = "H2C" if ip.src == host_ip else "C2H"

            if has_split:
                key = (direction, split_id)
                if key not in split_buffers:
                    split_buffers[key] = {"count": split_count, "parts": {}}
                split_buffers[key]["parts"][split_index] = payload
                if len(split_buffers[key]["parts"]) == split_count:
                    assembled = b""
                    for idx in range(split_count):
                        assembled += split_buffers[key]["parts"].get(idx, b"")
                    del split_buffers[key]
                    # Parse assembled packet
                    if len(assembled) >= 5:
                        mc = struct.unpack_from('<H', assembled, 1)[0]
                        ln = struct.unpack_from('<H', assembled, 3)[0]
                        pkt_data = assembled[5:5 + ln]
                        results["reassembled"][f"{direction}_{mc}_{len(results['reassembled'])}"] = {
                            "direction": direction,
                            "msgcode": mc,
                            "length": ln,
                            "actual_data_len": len(pkt_data),
                            "first64_hex": pkt_data[:64].hex() if pkt_data else "",
                            "data": pkt_data,
                        }
                continue

            # Non-split packet
            if direction == "H2C" and len(payload) >= 5:
                mc = struct.unpack_from('<H', payload, 1)[0]
                ln = struct.unpack_from('<H', payload, 3)[0]
                pkt_data = payload[5:5 + ln]
                if mc == 43299:
                    results["packdata_packets"].append({
                        "direction": direction,
                        "msgcode": mc,
                        "length_field": ln,
                        "actual_len": len(pkt_data),
                        "first32_hex": pkt_data[:32].hex() if pkt_data else "",
                    })
            elif direction == "C2H" and len(payload) >= 13:
                uin = struct.unpack_from('>I', payload, 1)[0]
                mc = struct.unpack_from('<H', payload, 9)[0]
                ln = struct.unpack_from('<H', payload, 11)[0]
                pkt_data = payload[13:13 + ln]
                results["other_game_packets"].append({
                    "direction": direction,
                    "msgcode": mc,
                    "uin": uin,
                    "length": ln,
                    "first32_hex": pkt_data[:32].hex() if pkt_data else "",
                })

    return results

# ============================================================
# Main
# ============================================================
def main():
    log("=" * 70)
    log("MiniWorld Map Full Analysis")
    log("=" * 70)

    # 1. Local save analysis
    save_root = Path(r"C:\Users\PC\AppData\Roaming\miniworddata110\data")
    world_dirs = sorted([d for d in save_root.glob("w*") if (d / "m0").exists()])

    log(f"\n[1] Local saves: {len(world_dirs)} worlds found")

    for wd in world_dirs[:2]:  # Analyze first 2 worlds
        log(f"\n{'='*50}")
        log(f"World: {wd.name}")
        log(f"{'='*50}")

        # wdesc.fb
        wdesc = wd / "wdesc.fb"
        if wdesc.exists():
            r = parse_fb_file(wdesc)
            log(f"  wdesc.fb: {r['size']}B, root_offset={r.get('fb_header', {}).get('root_offset', '?')}")
            table = r.get("root_table", {})
            if table:
                log(f"    fields: {table.get('num_fields', '?')}, vtable_size={table.get('vtable_size', '?')}")

        # wglobal.fb
        wglobal = wd / "wglobal.fb"
        if wglobal.exists():
            r = parse_fb_file(wglobal)
            log(f"  wglobal.fb: {r['size']}B")

        # wterrtype.fb
        wtt = wd / "wterrtype.fb"
        if wtt.exists():
            r = parse_raw_file(wtt)
            log(f"  wterrtype.fb: {r.get('as_uint32', '?')} (terrain type)")

        # wsize.fb
        ws = wd / "wsize.fb"
        if ws.exists():
            r = parse_raw_file(ws)
            log(f"  wsize.fb: 0x{r.get('as_uint32', 0):08X}")

        # Dimensions
        for dim in range(3):
            dim_dir = wd / f"m{dim}"
            if not dim_dir.exists():
                continue
            region_files = sorted(dim_dir.glob("x*z*.r"))
            actor_files = sorted(dim_dir.glob("a*_*.a"))
            log(f"  m{dim}/: {len(region_files)} regions, {len(actor_files)} actor files")

            # Parse first region file
            if region_files:
                rf = region_files[0]
                r = parse_region_file(rf)
                log(f"    {rf.name}: {r['size']}B")
                log(f"      header({r['header_bytes']}B): varints={r['header_varints']}")
                log(f"      sections: {r['sections_summary']}")
                log(f"      first-byte dist: {r.get('section_first_byte_dist', {})}")
                log(f"      data region: offset={r.get('data_region_start')}, size={r.get('data_region_size')}")
                if "data_compression" in r:
                    log(f"      compression: {r['data_compression']}, decompressed={r.get('data_decompressed_size')}")
                elif "zstd_note" in r:
                    log(f"      compression: unknown (zstd not installed)")

            # Parse first actor file
            if actor_files:
                af = actor_files[0]
                r = parse_actor_file(af)
                log(f"    {af.name}: {r['size']}B, format={r.get('format_guess', '?')}")
                if "root_table" in r:
                    table = r["root_table"]
                    log(f"      root table: {table.get('num_fields', '?')} fields")

    # 2. Network PACKDATA analysis
    pcap_path = Path(r"E:\TEMP_SHARE\MN2MC\miniworld_local.pcap")
    if pcap_path.exists():
        log(f"\n{'='*50}")
        log(f"[2] Network PACKDATA Analysis")
        log(f"{'='*50}")

        results = analyze_pcap_packdata(str(pcap_path), "192.168.1.7", "192.168.1.15")
        if results:
            log(f"  Total UDP packets: {results['total_udp']}")
            log(f"  Non-split PACKDATA (43299): {len(results['packdata_packets'])}")
            log(f"  Reassembled packets: {len(results['reassembled'])}")
            log(f"  Other C2H game packets: {len(results['other_game_packets'])}")

            # Analyze reassembled PACKDATA
            packdata_43299 = {k: v for k, v in results["reassembled"].items() if v["msgcode"] == 43299}
            log(f"\n  Reassembled PACKDATA (43299): {len(packdata_43299)}")

            for key, pkt in list(packdata_43299.items())[:5]:
                data = pkt["data"]
                log(f"\n    {key}: {pkt['actual_data_len']}B")
                log(f"      first 64B: {data[:64].hex()}")

                # Try parsing the 4-byte header + content
                if len(data) >= 4:
                    hdr = struct.unpack_from('<I', data, 0)[0]
                    log(f"      header uint32: {hdr}")
                    content = data[4:]
                    log(f"      content size: {len(content)}B")

                    # Try protobuf
                    try:
                        import blackboxprotobuf
                        msg, typedef = blackboxprotobuf.decode_message(content)
                        log(f"      protobuf: YES")
                        for k2, v2 in list(msg.items())[:10]:
                            val_str = str(v2)
                            if len(val_str) > 80:
                                val_str = val_str[:80] + "..."
                            log(f"        field {k2}: {val_str}")
                    except Exception as e:
                        log(f"      protobuf: NO ({e})")

                    # Try zlib/zstd on content
                    try:
                        dec = zlib.decompress(content)
                        log(f"      zlib: YES, {len(dec)}B")
                    except:
                        pass
                    try:
                        dec = zlib.decompress(content, -15)
                        log(f"      raw_deflate: YES, {len(dec)}B")
                    except:
                        pass

            # Show C2H packets (1013 etc)
            log(f"\n  C2H game packets:")
            for pkt in results["other_game_packets"][:10]:
                log(f"    code={pkt['msgcode']} uin={pkt['uin']} len={pkt['length']} hex={pkt['first32_hex'][:40]}")

    # 3. Summary
    log(f"\n{'='*70}")
    log(f"SUMMARY")
    log(f"{'='*70}")
    log(f"Total unknowns: {len(UNKNOWNS)}")
    for u in UNKNOWNS:
        log(f"  {u}")

    # Save report
    report_path = Path(r"E:\TEMP_SHARE\MN2MC\docs\map_analysis_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(REPORT))
    log(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    main()
