import sys
sys.path.insert(0, "D:\\Coding\\BlockConnect\\BlockConnect-MnMCP\\workspace\\mnmcp-v2\\src")

from config import Config, MiniConfig, MCConfig

def test_config():
    config = Config(
        mini=MiniConfig(ip="127.0.0.1", port=8080, uin=2067729592, xxtea_key="test"),
        mc=MCConfig(ip="127.0.0.1", port=25565, username="test")
    )
    assert config.mini.uin == 2067729592
    print("✓ Config test passed")

if __name__ == "__main__":
    test_config()
