"""
MiniWorld RakNet packet capture analyzer v2.
Properly strips RakNet framing to extract 0x89 game packets.

Usage:
  python capture_and_parse.py miniworld.pcap
"""
import struct
import sys
import os
import json
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from mn2mc.mini.msgcode_registry import get_name, get_direction, get_message_class, _CODE_TO_NAME

from scapy.all import rdpcap, UDP, IP, Raw


def parse_raknet_frame(data: bytes):
    """Extract encapsulated packets from a RakNet 0x84/0x8c data frame.

    RakNet data frame structure:
      1B  frame_id (0x80-0x8f)
      3B  sequence_number (LE 24-bit)
      then one or more encapsulated packets:
        1B  reliability_flags
          bits 7-5: reliability type
          bit 4: has_split
        2B  bit_length (BE) -> byte_length = (bit_length + 7) // 8
        if reliable (reliability >= 2):
          3B  reliable_message_number (LE)
        if sequenced (reliability 1 or 4):
          3B  sequencing_index (LE)
        if ordered (reliability 1,3,4,7):
          3B  ordering_index (LE)
          1B  ordering_channel
        if has_split:
          4B  split_count (BE)
          2B  split_id (BE)
          4B  split_index (BE)
        NB  payload (byte_length bytes)
    """
    if len(data) < 4:
        return []

    frame_id = data[0]
    if not (0x80 <= frame_id <= 0x8f):
        return []

    seq = data[1] | (data[2] << 8) | (data[3] << 16)
    pos = 4
    results = []

    while pos < len(data):
        if pos >= len(data):
            break

        flags = data[pos]
        pos += 1
        reliability = (flags >> 5) & 0x07
        has_split = bool(flags & 0x10)

        if pos + 2 > len(data):
            break
        bit_length = struct.unpack_from(">H", data, pos)[0]
        pos += 2
        byte_length = (bit_length + 7) // 8

        # reliable_message_number
        if reliability in (2, 3, 4, 6, 7):
            pos += 3  # 24-bit LE

        # sequencing_index
        if reliability in (1, 4):
            pos += 3

        # ordering_index + ordering_channel
        if reliability in (1, 3, 4, 7):
            pos += 3 + 1

        split_count = 0
        split_id = 0
        split_index = 0
        if has_split:
            if pos + 10 > len(data):
                break
            split_count = struct.unpack_from(">I", data, pos)[0]
            split_id = struct.unpack_from(">H", data, pos + 4)[0]
            split_index = struct.unpack_from(">I", data, pos + 6)[0]
            pos += 10

        if pos + byte_length > len(data):
            payload = data[pos:]
        else:
            payload = data[pos:pos + byte_length]
        pos += byte_length

        results.append({
            "seq": seq,
            "reliability": reliability,
            "has_split": has_split,
            "split_id": split_id if has_split else None,
            "split_index": split_index if has_split else None,
            "split_count": split_count if has_split else None,
            "payload": payload,
        })

    return results


def parse_game_packet(payload: bytes, direction_hint: str):
    """Parse 0x89 game packet from RakNet payload."""
    if not payload or payload[0] != 0x89:
        return None

    if direction_hint == "C2S" and len(payload) >= 13:
        uin = struct.unpack_from(">I", payload, 1)[0]
        msgcode, length = struct.unpack_from("<HH", payload, 9)
        name = get_name(msgcode)
        if name:
            pkt_data = payload[13:13 + length]
            return {
                "format": "C2S", "uin": uin,
                "msgcode": msgcode, "name": name,
                "direction": get_direction(msgcode),
                "length": length, "data": pkt_data,
            }

    if direction_hint == "S2C" and len(payload) >= 5:
        msgcode, length = struct.unpack_from("<HH", payload, 1)
        name = get_name(msgcode)
        if name:
            pkt_data = payload[5:5 + length]
            return {
                "format": "S2C",
                "msgcode": msgcode, "name": name,
                "direction": get_direction(msgcode),
                "length": length, "data": pkt_data,
            }

    # Try both formats
    if len(payload) >= 13:
        uin = struct.unpack_from(">I", payload, 1)[0]
        msgcode, length = struct.unpack_from("<HH", payload, 9)
        name = get_name(msgcode)
        if name and 13 + length <= len(payload) + 4:
            pkt_data = payload[13:13 + length]
            return {
                "format": "C2S", "uin": uin,
                "msgcode": msgcode, "name": name,
                "direction": get_direction(msgcode),
                "length": length, "data": pkt_data,
            }

    if len(payload) >= 5:
        msgcode, length = struct.unpack_from("<HH", payload, 1)
        name = get_name(msgcode)
        if name and 5 + length <= len(payload) + 4:
            pkt_data = payload[5:5 + length]
            return {
                "format": "S2C",
                "msgcode": msgcode, "name": name,
                "direction": get_direction(msgcode),
                "length": length, "data": pkt_data,
            }

    return None


def decode_proto(msgcode, data):
    cls = get_message_class(msgcode)
    if not cls or not data:
        return None
    try:
        msg = cls()
        msg.ParseFromString(data)
        fields = {}
        for fd in msg.DESCRIPTOR.fields:
            try:
                if msg.HasField(fd.name):
                    val = getattr(msg, fd.name)
                    if isinstance(val, bytes):
                        fields[fd.name] = val[:100].hex()
                    elif isinstance(val, (int, float, bool, str)):
                        fields[fd.name] = val
                    else:
                        fields[fd.name] = str(val)[:300]
            except ValueError:
                val = getattr(msg, fd.name)
                if fd.label == fd.LABEL_REPEATED and len(val) > 0:
                    fields[fd.name] = f"[{len(val)} items]"
        return fields
    except Exception as e:
        return {"_error": str(e)}


def main():
    if len(sys.argv) < 2:
        print("Usage: python capture_and_parse.py <pcap_file>")
        sys.exit(0)

    pcap_path = sys.argv[1]
    print(f"MiniWorld RakNet Analyzer v2")
    print(f"Proto: {len(_CODE_TO_NAME)} codes")
    print(f"Loading {pcap_path}...")

    packets = rdpcap(pcap_path)
    print(f"Total packets: {len(packets)}")

    # Determine client/server by looking at connection handshake
    client_addr = None
    server_addr = None
    for pkt in packets:
        if pkt.haslayer(UDP) and pkt.haslayer(Raw):
            raw = bytes(pkt[Raw].load)
            if raw and raw[0] == 0x05:  # OPEN_CONNECTION_REQUEST_1
                ip = pkt[IP]
                client_addr = (ip.src, pkt[UDP].sport)
                server_addr = (ip.dst, pkt[UDP].dport)
                print(f"Client: {ip.src}:{pkt[UDP].sport}")
                print(f"Server: {ip.dst}:{pkt[UDP].dport}")
                break

    if not client_addr:
        print("No RakNet handshake found!")
        sys.exit(1)

    # Reassemble split packets
    split_buffers = {}
    game_packets = []
    code_counter = Counter()

    for i, pkt in enumerate(packets):
        if not pkt.haslayer(UDP) or not pkt.haslayer(Raw):
            continue
        raw = bytes(pkt[Raw].load)
        if not raw or not (0x80 <= raw[0] <= 0x8f):
            continue

        ip = pkt[IP]
        is_from_client = (ip.src == client_addr[0] and pkt[UDP].sport == client_addr[1])
        dir_hint = "C2S" if is_from_client else "S2C"

        encaps = parse_raknet_frame(raw)
        for enc in encaps:
            payload = enc["payload"]

            if enc["has_split"]:
                key = (dir_hint, enc["split_id"])
                if key not in split_buffers:
                    split_buffers[key] = {}
                split_buffers[key][enc["split_index"]] = payload

                if len(split_buffers[key]) == enc["split_count"]:
                    assembled = b""
                    for idx in range(enc["split_count"]):
                        assembled += split_buffers[key].get(idx, b"")
                    del split_buffers[key]
                    payload = assembled
                else:
                    continue

            gp = parse_game_packet(payload, dir_hint)
            if gp:
                gp["pkt_index"] = i
                gp["timestamp"] = float(pkt.time)

                proto_fields = decode_proto(gp["msgcode"], gp["data"])
                if proto_fields:
                    gp["fields"] = proto_fields

                gp["data"] = gp["data"].hex() if gp["data"] else ""
                game_packets.append(gp)
                code_counter[gp["name"]] += 1

    print(f"\n{'='*70}")
    print(f"Found {len(game_packets)} game packets")
    print(f"{'='*70}")

    print(f"\nMessage frequency (top 50):")
    for name, count in code_counter.most_common(50):
        d = get_direction(next((c for c, n in _CODE_TO_NAME.items() if n == name), 0))
        print(f"  {count:5d}x  [{d:>3s}]  {name}")

    print(f"\n{'='*70}")
    print(f"Packet timeline (first 300):")
    print(f"{'='*70}")
    for p in game_packets[:300]:
        fmt = p.get("format", "?")
        name = p["name"]
        code = p["msgcode"]
        length = p["length"]
        uin = p.get("uin", "")
        uin_str = f" uin={uin}" if uin else ""
        arrow = ">>" if fmt == "C2S" else "<<"

        print(f"  {arrow} {fmt} {code:5d} {name:50s} {length:5d}B{uin_str}")

        fields = p.get("fields")
        if fields and not fields.get("_error"):
            for k, v in list(fields.items())[:10]:
                val_str = str(v)
                if len(val_str) > 100:
                    val_str = val_str[:100] + "..."
                print(f"     {k} = {val_str}")

    out_path = pcap_path.rsplit(".", 1)[0] + "_parsed.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(game_packets, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nSaved: {out_path} ({len(game_packets)} packets)")


if __name__ == "__main__":
    main()
