#include "backend_bridge.h"

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#define BB_INVALID_SOCKET INVALID_SOCKET
#define BB_SOCKET_ERROR SOCKET_ERROR
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#define closesocket close
#define BB_INVALID_SOCKET -1
#define BB_SOCKET_ERROR -1
#endif

#include <cstdio>
#include <cstring>

// Frame format:
//   [4B frame_len LE] [4B client_guid LE] [data]
// frame_len = 4 + len(data)
//
// Control frames (from C++ proxy to Python):
//   data = [0x00, 0x01] = client connected
//   data = [0x00, 0x02] = client disconnected
// Real game data always starts with 0x89 (>= 0x80), so 0x00 is unambiguous.

BackendBridge::BackendBridge() : m_socket(INVALID_SOCKET_VAL), m_running(false) {}

BackendBridge::~BackendBridge() {
    stop();
}

bool BackendBridge::start(const std::string& backend_host, uint16_t backend_port) {
#ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif

    m_socket = (int)socket(AF_INET, SOCK_STREAM, 0);
    if (m_socket == BB_INVALID_SOCKET) {
        printf("[BRIDGE] Failed to create socket\n");
        m_socket = INVALID_SOCKET_VAL;
        return false;
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(backend_port);
    inet_pton(AF_INET, backend_host.c_str(), &addr.sin_addr);

    if (connect(m_socket, (sockaddr*)&addr, sizeof(addr)) == BB_SOCKET_ERROR) {
        printf("[BRIDGE] Failed to connect to backend %s:%d\n",
               backend_host.c_str(), backend_port);
        closesocket(m_socket);
        m_socket = INVALID_SOCKET_VAL;
        return false;
    }

    m_running = true;
    m_recvThread = std::thread(&BackendBridge::recvLoop, this);

    printf("[BRIDGE] Connected to backend %s:%d\n", backend_host.c_str(), backend_port);
    return true;
}

void BackendBridge::stop() {
    m_running = false;
    if (m_socket != INVALID_SOCKET_VAL) {
        closesocket(m_socket);
        m_socket = INVALID_SOCKET_VAL;
    }
    if (m_recvThread.joinable()) {
        m_recvThread.join();
    }
}

void BackendBridge::sendFrame(uint32_t client_guid, const uint8_t* data, uint32_t len) {
    if (m_socket == INVALID_SOCKET_VAL) return;
    std::lock_guard<std::mutex> lock(m_sendMutex);

    uint32_t total = 4 + 4 + len;
    uint32_t frame_len = 4 + len;
    auto* buf = new uint8_t[total];
    memcpy(buf, &frame_len, 4);
    memcpy(buf + 4, &client_guid, 4);
    if (len > 0 && data) memcpy(buf + 8, data, len);
    int sent = send(m_socket, (const char*)buf, total, 0);
    if (sent != (int)total) {
        printf("[BRIDGE] sendFrame partial/failed: %d / %u\n", sent, total);
    }
    delete[] buf;
}

void BackendBridge::sendToBackend(uint32_t client_guid, const uint8_t* data, uint32_t len) {
    sendFrame(client_guid, data, len);
}

void BackendBridge::sendClientConnect(uint32_t client_guid) {
    const uint8_t ctrl[2] = { 0x00, 0x01 };
    sendFrame(client_guid, ctrl, 2);
}

void BackendBridge::sendClientDisconnect(uint32_t client_guid) {
    const uint8_t ctrl[2] = { 0x00, 0x02 };
    sendFrame(client_guid, ctrl, 2);
}

bool BackendBridge::pollFromBackend(BridgePacket& out) {
    std::lock_guard<std::mutex> lock(m_mutex);
    if (m_recvQueue.empty()) return false;
    out = std::move(m_recvQueue.front());
    m_recvQueue.pop();
    return true;
}

void BackendBridge::recvLoop() {
    uint8_t header[8];
    while (m_running) {
        int n = recv(m_socket, (char*)header, 8, MSG_WAITALL);
        if (n != 8) break;

        uint32_t frame_len = *(uint32_t*)header;
        uint32_t client_guid = *(uint32_t*)(header + 4);
        uint32_t data_len = frame_len - 4;

        if (data_len > 1024 * 1024) break;

        std::vector<uint8_t> data(data_len);
        if (data_len > 0) {
            n = recv(m_socket, (char*)data.data(), data_len, MSG_WAITALL);
            if (n != (int)data_len) break;
        }

        uint16_t code = 0;
        if (data_len >= 5 && data[0] == 0x89) {
            code = *(uint16_t*)(data.data() + 1);
        }

        BridgePacket pkt;
        pkt.client_guid = client_guid;
        pkt.msgcode = code;
        pkt.data = std::move(data);

        std::lock_guard<std::mutex> lock(m_mutex);
        m_recvQueue.push(std::move(pkt));
    }
    printf("[BRIDGE] Recv loop ended\n");
}
