/*
 * MN2MC RakNet Proxy
 *
 * Sits between MiniWorld client and Python backend.
 *
 * Two modes:
 *   --mode single  : single RakPeer on --port (default 19132).
 *                    Manual NAT message ignore. Relies on Path A (client must
 *                    receive direct host address - unsolved in 1.56).
 *   --mode dual    : two RakPeers - facilitator (--port) + host (--host-port).
 *                    Facilitator uses NatPunchthroughServer plugin; host peer
 *                    registers with facilitator. Standard Path B (NAT punch).
 *
 * Usage:
 *   mn2mc_proxy --mode dual --port 19132 --host-port 19133 \
 *               --guid 598340631 --lan-ip 192.168.1.7
 *   mn2mc_proxy --mode single --port 19132 \
 *               --guid 598340631 --lan-ip 192.168.1.7
 */

#include "proxy.h"
#include "backend_bridge.h"

#include <cstdio>
#include <cstring>
#include <csignal>
#include <chrono>
#include <thread>

#ifdef _WIN32
#include <windows.h>
#endif

static volatile bool g_running = true;

void signalHandler(int sig) {
    printf("\n[MAIN] Signal %d received, shutting down...\n", sig);
    g_running = false;
}

int main(int argc, char* argv[]) {
    ProxyMode mode = ProxyMode::DualPort;
    uint16_t punch_port = 19132;
    uint16_t host_port = 19133;
    std::string backend_host = "127.0.0.1";
    uint16_t backend_port = 19134;  // moved to avoid host port collision
    uint64_t host_guid = 0;
    std::string lan_ip = "192.168.1.7";

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--mode") == 0 && i + 1 < argc) {
            const char* m = argv[++i];
            if (strcmp(m, "single") == 0) mode = ProxyMode::SinglePort;
            else if (strcmp(m, "dual") == 0) mode = ProxyMode::DualPort;
            else { printf("[MAIN] unknown mode '%s'\n", m); return 1; }
        } else if (strcmp(argv[i], "--port") == 0 && i + 1 < argc) {
            punch_port = (uint16_t)atoi(argv[++i]);
        } else if (strcmp(argv[i], "--host-port") == 0 && i + 1 < argc) {
            host_port = (uint16_t)atoi(argv[++i]);
        } else if (strcmp(argv[i], "--backend") == 0 && i + 1 < argc) {
            char* arg = argv[++i];
            char* colon = strchr(arg, ':');
            if (colon) {
                *colon = 0;
                backend_host = arg;
                backend_port = (uint16_t)atoi(colon + 1);
            }
        } else if (strcmp(argv[i], "--guid") == 0 && i + 1 < argc) {
            host_guid = (uint64_t)atoll(argv[++i]);
        } else if (strcmp(argv[i], "--lan-ip") == 0 && i + 1 < argc) {
            lan_ip = argv[++i];
        }
    }

    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
    printf("===========================================\n");
    printf(" MN2MC RakNet Proxy\n");
    printf("===========================================\n");
    printf(" Mode:         %s\n", mode == ProxyMode::DualPort ? "dual" : "single");
    printf(" Punch port:   %d\n", punch_port);
    if (mode == ProxyMode::DualPort)
        printf(" Host port:    %d\n", host_port);
    printf(" Backend:      %s:%d\n", backend_host.c_str(), backend_port);
    printf(" Host GUID:    %llu\n", (unsigned long long)host_guid);
    printf(" LAN IP:       %s\n", lan_ip.c_str());
    printf("===========================================\n\n");

    signal(SIGINT, signalHandler);
#ifdef _WIN32
    signal(SIGBREAK, signalHandler);
#endif

    MN2MCProxy proxy;
    if (!proxy.start(mode, punch_port, host_port, host_guid, lan_ip)) {
        printf("[MAIN] Failed to start proxy!\n");
        return 1;
    }

    BackendBridge bridge;
    bool bridgeConnected = bridge.start(backend_host, backend_port);
    if (!bridgeConnected) {
        printf("[MAIN] WARNING: Backend not connected. Running in standalone mode.\n");
        printf("[MAIN] Packets will be logged but not forwarded.\n\n");
    }

    proxy.onGamePacket([&](uint32_t guid, const uint8_t* data, uint32_t len) {
        printf("[MAIN] Game packet from %u: %d bytes, first=0x%02X\n", guid, len, data[0]);
        if (bridgeConnected) {
            bridge.sendToBackend(guid, data, len);
        }
    });

    proxy.onClientConnect([&](uint32_t guid) {
        printf("[MAIN] Client %u connected - notifying backend\n", guid);
        if (bridgeConnected) {
            bridge.sendClientConnect(guid);
        } else {
            printf("[MAIN] WARN: backend not connected, client will not get init packets\n");
        }
    });

    proxy.onClientDisconnect([&](uint32_t guid) {
        printf("[MAIN] Client %u disconnected\n", guid);
        if (bridgeConnected) {
            bridge.sendClientDisconnect(guid);
        }
    });

    printf("[MAIN] Running... Press Ctrl+C to stop.\n\n");
    while (g_running) {
        proxy.update();

        BridgePacket pkt;
        while (bridge.pollFromBackend(pkt)) {
            proxy.sendRawToClient(pkt.client_guid, pkt.data.data(), (uint32_t)pkt.data.size());
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }

    printf("[MAIN] Shutting down...\n");
    proxy.stop();
    bridge.stop();
    printf("[MAIN] Done.\n");
    return 0;
}
