from dataclasses import dataclass
from typing import Optional

@dataclass
class RoomInfo:
    room_id: str
    room_name: str
    host_name: str
    host_uin: str
    current_players: int
    max_players: int
    map_name: str
    game_mode: str
    version: str = "1.55.0"
    ping: int = 10
    is_public: bool = True
    password: Optional[str] = None
