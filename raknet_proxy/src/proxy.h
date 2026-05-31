#pragma once
#include <cstdint>
#include <string>
#include <functional>
#include <memory>

namespace SLNet {
    class RakPeerInterface;
    struct Packet;
    struct SystemAddress;
    class NatPunchthroughServer;
}

using GamePacketCallback = std::function<void(uint32_t client_guid, const uint8_t* data, uint32_t len)>;
using ConnectCallback = std::function<void(uint32_t client_guid)>;

enum class ProxyMode {
    SinglePort,  // 单端口模式：只开 punch port，依赖 Path A (直连Host需要 sub_767FEE8 触发)
    DualPort,    // 双端口模式：punch port (NatPunchthroughServer) + host port (game server)，走 Path B
};

class MN2MCProxy {
public:
    MN2MCProxy();
    ~MN2MCProxy();

    // 启动
    // mode = SinglePort: 仅 punch_port 监听
    // mode = DualPort: punch_port (facilitator) + host_port (game)
    bool start(ProxyMode mode,
               uint16_t punch_port,
               uint16_t host_port,
               uint64_t host_guid,
               const std::string& lan_ip);

    void update();

    void sendToClient(uint32_t client_guid, uint16_t msgcode, const uint8_t* data, uint32_t len);
    void sendRawToClient(uint32_t client_guid, const uint8_t* data, uint32_t len);

    void onGamePacket(GamePacketCallback cb) { m_onGamePacket = cb; }
    void onClientConnect(ConnectCallback cb) { m_onConnect = cb; }
    void onClientDisconnect(ConnectCallback cb) { m_onDisconnect = cb; }

    void stop();

private:
    void handlePunchPacket(SLNet::Packet* packet);
    void handleHostPacket(SLNet::Packet* packet);
    void handleSinglePortPacket(SLNet::Packet* packet);

    ProxyMode m_mode;
    SLNet::RakPeerInterface* m_punchPeer;
    SLNet::RakPeerInterface* m_hostPeer;
    SLNet::NatPunchthroughServer* m_natPlugin;

    uint64_t m_hostGuid;
    uint64_t m_facilitatorGuid;
    uint16_t m_punchPort;
    uint16_t m_hostPort;
    std::string m_lanIp;

    GamePacketCallback m_onGamePacket;
    ConnectCallback m_onConnect;
    ConnectCallback m_onDisconnect;
};
