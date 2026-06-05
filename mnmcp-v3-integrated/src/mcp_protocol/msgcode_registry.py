"""
MnMCP v3 - 消息注册表
移植自 MN2MC，融合 MnMCP v3 高质量架构
"""

from typing import Dict, Optional, Type, Any, Callable
from dataclasses import dataclass
from enum import IntEnum
import logging

logger = logging.getLogger(__name__)


class PacketDirection(IntEnum):
    """数据包方向"""
    CLIENT_TO_SERVER = 0  # CH - Client to Host (MiniWorld)
    SERVER_TO_CLIENT = 1  # HC - Host to Client (MiniWorld)
    UNKNOWN = 2


@dataclass
class MessageInfo:
    """消息信息"""
    code: int
    name: str
    direction: PacketDirection
    message_class: Optional[Type] = None
    description: str = ""


class MessageRegistry:
    """
    MiniWorld 消息注册表
    
    功能:
    1. 消息码到名称的映射
    2. 消息方向管理 (CH/HC)
    3. 消息类注册
    4. 快速查询
    
    移植自 MN2MC，改进:
    - 类型注解完整
    - 错误处理完善
    - 支持动态注册
    """
    
    # 消息码定义 (移植自 MN2MC protobuf_parser.py)
    MSG_CODE_TO_NAME: Dict[int, str] = {
        # 心跳
        11: "PB_HeartBeatCH",
        12: "PB_HeartBeatHC",
        
        # 区块同步
        101: "PB_SyncChunkDataCH",
        102: "PB_SyncChunkDataHC",
        103: "PB_BlockUpdateCH",
        104: "PB_BlockUpdateHC",
        105: "PB_SyncSectionLightDataHC",
        106: "PB_OverrideLightDataHC",
        
        # 角色/玩家
        1001: "PB_RoleEnterWorldCH",
        1002: "PB_RoleEnterWorldHC",
        1003: "PB_RoleLeaveWorldCH",
        1004: "PB_RoleLeaveWorldHC",
        1006: "PB_ActorEnterAOIHC",
        1008: "PB_ActorLeaveAOIHC",
        1010: "PB_GameLeaderSwitchHC",
        1011: "PB_GeneralEnterAOIHC",
        
        # 移动
        2001: "PB_RoleMoveCH",
        2002: "PB_TrainMoveCH",
        2004: "PB_ActorMoveHC",
        2005: "PB_TrainMoveHC",
        2006: "PB_ActorMoveV2HC",
        2007: "PB_ActorTeleportCH",
        2008: "PB_ActorTeleportHC",
        2009: "PB_ActorMotionHC",
        2010: "PB_MechaMotionHC",
        2011: "PB_GunInfoCH",
        2012: "PB_SetInfoCH",
        2013: "PB_SyncGridUserDataCH",
        2014: "PB_SyncGridUserDataHC",
        2015: "PB_SyncTriggerBlockHC",
        2016: "PB_FullrotActorMoveHC",
        2017: "PB_ActorMotionV2HC",
        2018: "PB_ActorMoveV3HC",
        2019: "PB_ActorModelChangeHC",
        
        # 其他
        2997: "PB_ServerCheckBoardHC",
        2998: "PB_ServerSetPriorityHC",
        2999: "PB_ServerSpeedCheckCH",
        3000: "PB_ServerSpeedCheckHC",
        
        # 输入/交互
        4001: "PB_InputActionCH",
        4002: "PB_ActorInputActionHC",
        4003: "PB_DriveInputCH",
        4004: "PB_DriveInputHC",
        4005: "PB_RoleInputHistoryCH",
        4006: "PB_RoleInputHistoryHC",
        4007: "PB_ClientCheckBoardCH",
        4008: "PB_ClientCheckBoardHC",
        4009: "PB_TutorialInputActionCH",
        4010: "PB_TutorialInputActionHC",
        
        # 容器/物品
        5001: "PB_OpenInventoryCH",
        5002: "PB_OpenInventoryHC",
        5003: "PB_CloseInventoryCH",
        5004: "PB_CloseInventoryHC",
        5005: "PB_SyncInventoryCH",
        5006: "PB_SyncInventoryHC",
        5007: "PB_MoveInventoryItemCH",
        5008: "PB_MoveInventoryItemHC",
        5009: "PB_DropItemCH",
        5010: "PB_DropItemHC",
        5011: "PB_ConsumeItemCH",
        5012: "PB_PickupItemCH",
        5013: "PB_PickupItemHC",
        5014: "PB_InventoryItemDetailCH",
        5015: "PB_InventoryItemDetailHC",
        5016: "PB_CraftingCH",
        5017: "PB_CraftingHC",
        5018: "PB_SwapInventoryCH",
        5019: "PB_SwapInventoryHC",
        5020: "PB_UiAdjustItemCH",
        5021: "PB_UiAdjustItemHC",
        
        # 方块交互
        6001: "PB_PlaceBlockCH",
        6002: "PB_PlaceBlockHC",
        6003: "PB_DestroyBlockCH",
        6004: "PB_DestroyBlockHC",
        6005: "PB_BlockInteractCH",
        6006: "PB_BlockInteractHC",
        6007: "PB_BlockPunchCH",
        6008: "PB_BlockPunchHC",
        
        # 聊天
        9001: "PB_ChatContentCH",
        9002: "PB_ChatContentHC",
        9003: "PB_ChatInfoCH",
        9004: "PB_ChatInfoHC",
        9005: "PB_ChatBlockListCH",
        9006: "PB_ChatBlockListHC",
        9007: "PB_ChatLikeCH",
        9008: "PB_ChatLikeHC",
    }
    
    # 方向映射 (CH = Client->Host, HC = Host->Client)
    MSG_DIRECTION: Dict[int, PacketDirection] = {}
    
    # 消息类映射
    _message_classes: Dict[int, Type] = {}
    
    def __init__(self):
        """初始化注册表"""
        self._build_direction_map()
    
    def _build_direction_map(self) -> None:
        """构建方向映射"""
        for code, name in self.MSG_CODE_TO_NAME.items():
            if name.endswith("CH"):
                self.MSG_DIRECTION[code] = PacketDirection.CLIENT_TO_SERVER
            elif name.endswith("HC"):
                self.MSG_DIRECTION[code] = PacketDirection.SERVER_TO_CLIENT
            else:
                self.MSG_DIRECTION[code] = PacketDirection.UNKNOWN
    
    def get_name(self, code: int) -> Optional[str]:
        """
        获取消息名称
        
        Args:
            code: 消息码
            
        Returns:
            消息名称，未找到返回 None
        """
        return self.MSG_CODE_TO_NAME.get(code)
    
    def get_code(self, name: str) -> Optional[int]:
        """
        通过名称获取消息码
        
        Args:
            name: 消息名称
            
        Returns:
            消息码，未找到返回 None
        """
        for code, msg_name in self.MSG_CODE_TO_NAME.items():
            if msg_name == name:
                return code
        return None
    
    def get_direction(self, code: int) -> PacketDirection:
        """
        获取消息方向
        
        Args:
            code: 消息码
            
        Returns:
            消息方向
        """
        return self.MSG_DIRECTION.get(code, PacketDirection.UNKNOWN)
    
    def register_class(self, code: int, message_class: Type) -> None:
        """
        注册消息类
        
        Args:
            code: 消息码
            message_class: 消息类
        """
        self._message_classes[code] = message_class
        logger.debug(f"Registered message class: {code} -> {message_class.__name__}")
    
    def get_message_class(self, code: int) -> Optional[Type]:
        """
        获取消息类
        
        Args:
            code: 消息码
            
        Returns:
            消息类，未注册返回 None
        """
        return self._message_classes.get(code)
    
    def is_client_to_server(self, code: int) -> bool:
        """是否是客户端到服务端的消息"""
        return self.get_direction(code) == PacketDirection.CLIENT_TO_SERVER
    
    def is_server_to_client(self, code: int) -> bool:
        """是否是服务端到客户端的消息"""
        return self.get_direction(code) == PacketDirection.SERVER_TO_CLIENT
    
    def get_all_codes(self) -> list:
        """获取所有消息码"""
        return list(self.MSG_CODE_TO_NAME.keys())
    
    def get_stats(self) -> Dict[str, int]:
        """
        获取统计信息
        
        Returns:
            统计字典
        """
        total = len(self.MSG_CODE_TO_NAME)
        ch_count = sum(1 for d in self.MSG_DIRECTION.values() if d == PacketDirection.CLIENT_TO_SERVER)
        hc_count = sum(1 for d in self.MSG_DIRECTION.values() if d == PacketDirection.SERVER_TO_CLIENT)
        registered = len(self._message_classes)
        
        return {
            'total_messages': total,
            'client_to_server': ch_count,
            'server_to_client': hc_count,
            'classes_registered': registered,
        }


# 全局注册表实例
_registry = MessageRegistry()


def get_message_name(code: int) -> Optional[str]:
    """获取消息名称 (便捷函数)"""
    return _registry.get_name(code)


def get_message_direction(code: int) -> PacketDirection:
    """获取消息方向 (便捷函数)"""
    return _registry.get_direction(code)


def get_message_class(code: int) -> Optional[Type]:
    """获取消息类 (便捷函数)"""
    return _registry.get_message_class(code)


def register_message_class(code: int, message_class: Type) -> None:
    """注册消息类 (便捷函数)"""
    _registry.register_class(code, message_class)


# 测试
if __name__ == "__main__":
    registry = MessageRegistry()
    
    print("=" * 60)
    print("MnMCP v3 - 消息注册表测试")
    print("=" * 60)
    
    # 测试查询
    test_codes = [11, 1001, 2001, 6001, 9001]
    
    print("\n消息查询测试:")
    for code in test_codes:
        name = registry.get_name(code)
        direction = registry.get_direction(code)
        dir_str = "CH" if direction == PacketDirection.CLIENT_TO_SERVER else "HC" if direction == PacketDirection.SERVER_TO_CLIENT else "?"
        print(f"  {code:4d} -> {name:30s} ({dir_str})")
    
    # 统计
    stats = registry.get_stats()
    print(f"\n统计信息:")
    print(f"  总消息数: {stats['total_messages']}")
    print(f"  Client->Server: {stats['client_to_server']}")
    print(f"  Server->Client: {stats['server_to_client']}")
    print(f"  已注册类: {stats['classes_registered']}")
    
    print("\n✓ 消息注册表测试通过")
