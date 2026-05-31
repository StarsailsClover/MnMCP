"""
Minimal RakNet server for testing MiniWorld client connectivity.
Listens on 0.0.0.0:19132, accepts connections, parses all incoming packets.
No auth, no MC bridge, no Node.js — pure packet capture.
"""
import asyncio
import struct
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import aiorak
from loguru import logger
from mn2mc.mini.msgcode_registry import get_name, get_direction, get_message_class, decode_packet

logger.remove()
logger.add(sys.stderr, level="DEBUG", format="<green>{time:HH:mm:ss}</green> | <level>{level:7s}</level> | {message}")
logger.add("logs/raknet_test_{time}.log", level="DEBUG", rotation="10 MB")

PACKET_LOG = []


def parse_client_packet(raw: bytes):
    if len(raw) < 13 or raw[0:1] != b'\x89':
        return None, None, None, raw
    uin = struct.unpack(">I", raw[1:5])[0]
    msgcode, length = struct.unpack("<HH", raw[9:13])
    data = raw[13:13+length]
    return uin, msgcode, length, data


def parse_server_packet(raw: bytes):
    if len(raw) < 5 or raw[0:1] != b'\x89':
        return None, None, raw
    msgcode, length = struct.unpack("<HH", raw[1:5])
    data = raw[5:5+length]
    return msgcode, length, data


async def handler(conn: aiorak.Connection):
    remote = conn.remote_address
    guid = conn.remote_guid
    logger.info(f"=== NEW CONNECTION === guid={guid} addr={remote}")

    import mn2mc.mini.proto as proto
    import json

    room_extra = {
        "room_extra": {
            "audioconfigurl": '{"editorSceneSwitch":1,"worldtype":4}',
            "autoTag": "综合",
            "editorSceneSwitch": 0,
            "modUuids": [],
            "modurl": "",
            "translate": "",
            "translate_sourcelang": 0,
            "uilibsurl": "",
            "version": "1.55.0",
            "vipExp": 0,
            "vipLevel": 0,
            "vipType": 0,
        }
    }
    extra_msg = proto.hc.PB_RoomExtraInfoHC()
    extra_msg.room_extra = json.dumps(room_extra["room_extra"]).encode()
    extra_bytes = extra_msg.SerializeToString()

    server_pkt = b'\x89' + struct.pack("<HH", 5205, len(extra_bytes)) + extra_bytes
    conn.send(server_pkt, aiorak.Reliability.RELIABLE_ORDERED)
    logger.info(f"Sent PB_SYNC_ROOM_EXTRA_HC to {guid}")

    pkt_count = 0
    try:
        async for raw in conn:
            pkt_count += 1
            uin, msgcode, length, data = parse_client_packet(raw)
            if msgcode is None:
                logger.warning(f"[{pkt_count}] Non-0x89 packet ({len(raw)}B): {raw[:32].hex()}")
                continue

            name = get_name(msgcode) or f"UNKNOWN_{msgcode}"
            direction = get_direction(msgcode)
            cls = get_message_class(msgcode)

            logger.info(f"[{pkt_count}] uin={uin} code={msgcode} name={name} dir={direction} len={length}")

            if cls and data:
                try:
                    msg = cls()
                    msg.ParseFromString(data)
                    fields = {}
                    for fd in msg.DESCRIPTOR.fields:
                        if msg.HasField(fd.name):
                            val = getattr(msg, fd.name)
                            if isinstance(val, bytes):
                                fields[fd.name] = val[:64].hex() + ("..." if len(val) > 64 else "")
                            else:
                                fields[fd.name] = str(val)[:200]
                    if fields:
                        for k, v in fields.items():
                            logger.debug(f"  {k} = {v}")
                    else:
                        logger.debug(f"  (empty message)")
                except Exception as e:
                    logger.warning(f"  Proto parse failed: {e}")
                    logger.debug(f"  Raw data: {data[:64].hex()}")
            elif data:
                logger.debug(f"  No proto class, raw: {data[:64].hex()}")

            PACKET_LOG.append({
                "seq": pkt_count,
                "uin": uin,
                "code": msgcode,
                "name": name,
                "direction": direction,
                "length": length,
                "data_hex": data.hex() if data else "",
            })

    except aiorak.ConnectionClosedError:
        logger.info(f"Connection closed: guid={guid}")
    except Exception as e:
        logger.exception(f"Error in handler: {e}")

    logger.info(f"=== DISCONNECTED === guid={guid} total_packets={pkt_count}")


async def main():
    host = "0.0.0.0"
    port = 19132

    logger.info(f"Starting RakNet test server on {host}:{port}")
    logger.info(f"GUID=666 (non-host bridge mode)")
    logger.info(f"Proto registry: 659/660 codes mapped")
    logger.info(f"Waiting for MiniWorld client connection...")
    logger.info(f"")
    logger.info(f"Point your MiniWorld client to this machine's LAN IP on port {port}")

    server = await aiorak.create_server((host, port), handler, guid=666)

    try:
        await server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await server.close()

    if PACKET_LOG:
        import json
        with open("logs/captured_packets.json", "w") as f:
            json.dump(PACKET_LOG, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(PACKET_LOG)} packets to logs/captured_packets.json")


if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    asyncio.run(main())
