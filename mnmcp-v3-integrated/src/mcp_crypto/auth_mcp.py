#!/usr/bin/env python3
"""
MnMCP 登录认证模块
基于 MN2MC auth.py，改进为高质量架构

功能:
- 异步 HTTP 登录
- JWT Token 管理
- Session 状态维护
- 自动重连
"""

import json
import hashlib
import time
import asyncio
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .xxtea_mcp import MCPXXTEA, get_xxtea

logger = logging.getLogger(__name__)

# 登录 URL (来自 MN2MC)
LOGIN_URL = "https://wskacchm.mini1.cn:14130/man_machine/login_v3?msg={msg}&sign={sign}"


class MCPAuthenticationError(Exception):
    """认证错误"""
    pass


@dataclass
class MCPAuthState:
    """认证状态"""
    uin: int = 0
    api_id: int = 110
    name: str = "Unknown"
    jwt: str = ""
    full_sign: str = ""
    s2: str = ""
    s2t: str = ""
    
    # 时间戳
    login_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    @property
    def is_expired(self) -> bool:
        """Token 是否过期"""
        if self.expires_at is None:
            return True
        return datetime.now() > self.expires_at
    
    @property
    def is_authenticated(self) -> bool:
        """是否已认证"""
        return self.uin != 0 and not self.is_expired


@dataclass
class MCPAuthConfig:
    """认证配置"""
    uin: str = ""
    passwd: str = ""
    device_id: str = ""
    api_id: int = 110
    version: str = "1.55.0"
    
    def validate(self) -> bool:
        """验证配置"""
        return bool(self.uin and self.passwd)


class MCPAuthManager:
    """
    MnMCP 认证管理器
    
    功能:
    1. XXTEA 加密登录请求
    2. MD5 签名
    3. HTTP GET 登录
    4. JWT Token 解析
    5. Session 自动维护
    
    使用示例:
        auth = MCPAuthManager(config)
        await auth.login()
        
        if auth.is_authenticated:
            print(f"登录成功: {auth.state.name}")
    """
    
    def __init__(self, config: MCPAuthConfig):
        """
        初始化
        
        Args:
            config: 认证配置
        """
        self.config = config
        self.state = MCPAuthState()
        self.xxtea = get_xxtea()
        
        # 登录 URL 中的固定 key (来自 MN2MC)
        self._sign_key = "2ddb7619717147439c83ab022e9d4d38"
        
        logger.info(f"MCPAuthManager 初始化: uin={config.uin}")
    
    async def login(self) -> bool:
        """
        执行登录
        
        Returns:
            是否登录成功
        """
        if not self.config.validate():
            raise MCPAuthenticationError("配置无效: uin 或 passwd 为空")
        
        logger.info(f"开始登录: uin={self.config.uin}")
        
        try:
            # 构建登录消息
            server_time = int(time.time())
            login_data = {
                "source": "client",
                "juhe_auth": "",
                "passwd_auth": json.dumps({"passwd": self.config.passwd}),
                "DeviceID": self.config.device_id,
                "is_url": True,
                "geetest": "blending",
                "target": "login",
                "apiid": self.config.api_id,
                "juhe_strong_auth": "",
                "svrTime": server_time,
                "login_type": "passwd",
                "version": self.config.version,
                "time": server_time,
                "uin": self.config.uin,
            }
            
            # 编码消息
            msg = self._encode_message(login_data)
            logger.debug(f"登录消息编码完成: {msg[:50]}...")
            
            # 计算签名
            sign = self._calculate_sign(msg)
            logger.debug(f"签名: {sign[:16]}...")
            
            # 构建 URL
            url = LOGIN_URL.format(msg=msg, sign=sign)
            
            # 发送 HTTP 请求
            response_data = await self._send_login_request(url)
            
            # 解析响应
            success = self._parse_response(response_data)
            
            if success:
                logger.info(f"✓ 登录成功: {self.state.name} (uin={self.state.uin})")
            else:
                logger.error(f"✗ 登录失败: {response_data}")
            
            return success
            
        except Exception as e:
            logger.exception(f"登录异常: {e}")
            return False
    
    def _encode_message(self, data: dict) -> str:
        """编码登录消息"""
        return self.xxtea.encode_message(data)
    
    def _calculate_sign(self, msg: str) -> str:
        """计算 MD5 签名"""
        sign_str = f"msg={msg}&key={self._sign_key}"
        return hashlib.md5(sign_str.encode()).hexdigest()
    
    async def _send_login_request(self, url: str) -> dict:
        """发送登录 HTTP 请求"""
        # 模拟 HTTP 请求 (实际应该使用 aiohttp)
        # 这里简化处理，实际环境中需要真实请求
        
        logger.debug(f"发送请求: {url[:100]}...")
        
        # 模拟成功响应 (用于测试)
        # 实际应该使用:
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(url) as response:
        #         text = await response.text()
        #         return json.loads(text)
        
        # 模拟响应
        await asyncio.sleep(0.1)  # 模拟网络延迟
        
        return {
            "code": 0,
            "data": {
                "uin": self.config.uin,
                "name": f"Player_{self.config.uin[:6]}",
                "jwt": "mock_jwt_token_12345",
                "full_sign": "mock_full_sign",
                "s2": "mock_s2",
                "s2t": "mock_s2t"
            }
        }
    
    def _parse_response(self, data: dict) -> bool:
        """解析登录响应"""
        if data.get("code") != 0:
            logger.error(f"登录错误: {data}")
            return False
        
        response_data = data.get("data", {})
        
        # 更新状态
        self.state.uin = int(response_data.get("uin", 0))
        self.state.name = response_data.get("name", "Unknown")
        self.state.jwt = response_data.get("jwt", "")
        self.state.full_sign = response_data.get("full_sign", "")
        self.state.s2 = response_data.get("s2", "")
        self.state.s2t = response_data.get("s2t", "")
        self.state.login_at = datetime.now()
        self.state.expires_at = datetime.now() + timedelta(hours=24)
        
        return True
    
    async def logout(self):
        """登出"""
        logger.info(f"登出: {self.state.name}")
        self.state = MCPAuthState()
    
    async def refresh_token(self) -> bool:
        """刷新 Token"""
        if not self.state.is_authenticated:
            logger.warning("未登录，无法刷新")
            return False
        
        logger.info("刷新 Token...")
        # TODO: 实现刷新逻辑
        return await self.login()
    
    @property
    def is_authenticated(self) -> bool:
        """是否已认证"""
        return self.state.is_authenticated
    
    @property
    def uin(self) -> int:
        """获取 UIN"""
        return self.state.uin
    
    @property
    def name(self) -> str:
        """获取用户名"""
        return self.state.name
    
    @property
    def token(self) -> str:
        """获取 JWT Token"""
        return self.state.jwt
    
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        if not self.is_authenticated:
            return {}
        
        return {
            "Authorization": f"Bearer {self.state.jwt}",
            "X-Uin": str(self.state.uin),
            "X-Api-Id": str(self.state.api_id)
        }


if __name__ == "__main__":
    # 测试
    print("=" * 60)
    print(" MCPAuthManager 测试 ".center(60))
    print("=" * 60)
    
    config = MCPAuthConfig(
        uin="123456789",
        passwd="test_password",
        device_id="test_device_123"
    )
    
    auth = MCPAuthManager(config)
    
    # 运行测试
    async def test():
        success = await auth.login()
        
        if success:
            print(f"\n✓ 登录成功!")
            print(f"  UIN: {auth.uin}")
            print(f"  名称: {auth.name}")
            print(f"  Token: {auth.token[:20]}...")
            print(f"  认证头: {auth.get_auth_headers()}")
        else:
            print("\n✗ 登录失败")
    
    asyncio.run(test())
    
    print("\n" + "=" * 60)