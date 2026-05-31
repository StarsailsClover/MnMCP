#pragma once
#include <cstdint>
#include <string>
#include <thread>
#include <mutex>
#include <queue>
#include <functional>

// TCP bridge to Python backend (mn2mc)
// Sends game packets from client to backend
// Receives game packets from backend to send to client

struct BridgePacket {
    uint32_t client_guid;
    uint16_t msgcode;
    std::vector<uint8_t> data;
};

class BackendBridge {
public:
    BackendBridge();
    ~BackendBridge();

    bool start(const std::string& backend_host, uint16_t backend_port);
    void stop();

    // Send C2S packet to backend
    void sendToBackend(uint32_t client_guid, const uint8_t* data, uint32_t len);

    // Send client connect/disconnect notification (control frames)
    void sendClientConnect(uint32_t client_guid);
    void sendClientDisconnect(uint32_t client_guid);

    // Poll for S2C packets from backend
    bool pollFromBackend(BridgePacket& out);

    bool isConnected() const { return m_socket != INVALID_SOCKET_VAL; }

private:
    static const int INVALID_SOCKET_VAL = -1;
    int m_socket;
    bool m_running;
    std::thread m_recvThread;
    std::mutex m_mutex;
    std::mutex m_sendMutex;
    std::queue<BridgePacket> m_recvQueue;

    void sendFrame(uint32_t client_guid, const uint8_t* data, uint32_t len);
    void recvLoop();
};
