#include "proxy.h"

#include "slikenet/peerinterface.h"
#define protected public
#include "slikenet/peer.h"
#undef protected
#include "slikenet/MessageIdentifiers.h"
#include "slikenet/BitStream.h"
#include "slikenet/NatPunchthroughServer.h"
#include "slikenet/NatPunchthroughClient.h"
#include "slikenet/GetTime.h"

// for host peer's NAT punch client
static SLNet::NatPunchthroughClient* g_hostNatClient = nullptr;

#include <cstdio>
#include <cstring>

MN2MCProxy::MN2MCProxy()
    : m_mode(ProxyMode::SinglePort),
      m_punchPeer(nullptr), m_hostPeer(nullptr), m_natPlugin(nullptr),
      m_hostGuid(0), m_facilitatorGuid(0xDEADBEEFCAFEBABEULL),
      m_punchPort(0), m_hostPort(0) {}

MN2MCProxy::~MN2MCProxy() {
    stop();
}

bool MN2MCProxy::start(ProxyMode mode,
                       uint16_t punch_port,
                       uint16_t host_port,
                       uint64_t host_guid,
                       const std::string& lan_ip)
{
    m_mode = mode;
    m_punchPort = punch_port;
    m_hostPort = host_port;
    m_hostGuid = host_guid;
    m_lanIp = lan_ip;

    const char* bindAddr = lan_ip.empty() ? nullptr : lan_ip.c_str();

    // ============================================================
    // Punch peer (facilitator) - always created
    // ============================================================
    m_punchPeer = SLNet::RakPeerInterface::GetInstance();
    if (!m_punchPeer) {
        printf("[PROXY] Failed to create punch RakPeer\n");
        return false;
    }

    if (mode == ProxyMode::DualPort) {
        // Attach NatPunchthroughServer plugin to facilitator
        m_natPlugin = new SLNet::NatPunchthroughServer();
        m_punchPeer->AttachPlugin(m_natPlugin);
        printf("[PROXY] NatPunchthroughServer plugin attached\n");
    }

    SLNet::SocketDescriptor punchSd(punch_port, bindAddr);
    punchSd.socketFamily = AF_INET;
    auto rc = m_punchPeer->Startup(64, &punchSd, 1);
    if (rc != SLNet::RAKNET_STARTED) {
        printf("[PROXY] Punch peer startup failed: %d\n", rc);
        return false;
    }
    m_punchPeer->SetMaximumIncomingConnections(64);

    if (mode == ProxyMode::SinglePort) {
        // Single-port: use host GUID for the punch peer
        SLNet::RakNetGUID guid;
        guid.g = host_guid;
        ((SLNet::RakPeer*)m_punchPeer)->myGuid = guid;
        printf("[PROXY] SinglePort mode: punch=%s:%d GUID=%llu\n",
               bindAddr ? bindAddr : "0.0.0.0", punch_port,
               (unsigned long long)host_guid);
        printf("[PROXY] Waiting for connections...\n");
        return true;
    }

    // ============================================================
    // DualPort mode: also create host peer
    // ============================================================
    // Facilitator gets a unique GUID, not host's
    SLNet::RakNetGUID facGuid;
    facGuid.g = m_facilitatorGuid;
    ((SLNet::RakPeer*)m_punchPeer)->myGuid = facGuid;

    m_hostPeer = SLNet::RakPeerInterface::GetInstance();
    if (!m_hostPeer) {
        printf("[PROXY] Failed to create host RakPeer\n");
        return false;
    }

    SLNet::SocketDescriptor hostSd(host_port, bindAddr);
    hostSd.socketFamily = AF_INET;
    rc = m_hostPeer->Startup(64, &hostSd, 1);
    if (rc != SLNet::RAKNET_STARTED) {
        printf("[PROXY] Host peer startup failed: %d\n", rc);
        return false;
    }
    m_hostPeer->SetMaximumIncomingConnections(64);

    // Host peer uses the host's actual UID as GUID (so clients recognize us)
    SLNet::RakNetGUID hGuid;
    hGuid.g = host_guid;
    ((SLNet::RakPeer*)m_hostPeer)->myGuid = hGuid;

    // Attach NatPunchthroughClient to host peer so it can participate
    // in NAT punch coordination from the facilitator
    g_hostNatClient = new SLNet::NatPunchthroughClient();
    m_hostPeer->AttachPlugin(g_hostNatClient);
    printf("[PROXY] NatPunchthroughClient attached to host peer\n");

    // Host peer connects to facilitator to register for NAT punch
    const char* facHost = bindAddr ? bindAddr : "127.0.0.1";
    auto cc = m_hostPeer->Connect(facHost, punch_port, nullptr, 0);
    if (cc != SLNet::CONNECTION_ATTEMPT_STARTED) {
        printf("[PROXY] WARN: host->facilitator connect failed: %d\n", (int)cc);
    } else {
        printf("[PROXY] host peer connecting to facilitator %s:%d\n", facHost, punch_port);
    }

    printf("[PROXY] DualPort mode:\n");
    printf("[PROXY]   facilitator: %s:%d (GUID=%llu)\n",
           bindAddr ? bindAddr : "0.0.0.0", punch_port,
           (unsigned long long)m_facilitatorGuid);
    printf("[PROXY]   host:        %s:%d (GUID=%llu)\n",
           bindAddr ? bindAddr : "0.0.0.0", host_port,
           (unsigned long long)host_guid);
    printf("[PROXY] Waiting for connections...\n");
    return true;
}

void MN2MCProxy::update() {
    if (m_punchPeer) {
        SLNet::Packet* p;
        for (p = m_punchPeer->Receive(); p; m_punchPeer->DeallocatePacket(p), p = m_punchPeer->Receive()) {
            if (m_mode == ProxyMode::DualPort) handlePunchPacket(p);
            else                                handleSinglePortPacket(p);
        }
    }
    if (m_hostPeer) {
        SLNet::Packet* p;
        for (p = m_hostPeer->Receive(); p; m_hostPeer->DeallocatePacket(p), p = m_hostPeer->Receive()) {
            handleHostPacket(p);
        }
    }
}

// Single-port: client connects to one peer; we serve everything here.
// NAT messages: respond manually (won't work fully without secondary peer).
void MN2MCProxy::handleSinglePortPacket(SLNet::Packet* packet) {
    unsigned char msgId = packet->data[0];
    uint32_t guid = (uint32_t)(packet->guid.g & 0xFFFFFFFF);

    switch (msgId) {
    case ID_NEW_INCOMING_CONNECTION:
        printf("[PUNCH] Client connected: %s (guid=%u)\n",
               packet->systemAddress.ToString(true), guid);
        if (m_onConnect) m_onConnect(guid);
        break;

    case ID_DISCONNECTION_NOTIFICATION:
    case ID_CONNECTION_LOST:
        printf("[PUNCH] Client disconnected: %s\n",
               packet->systemAddress.ToString(true));
        if (m_onDisconnect) m_onDisconnect(guid);
        break;

    case 0x7C:
        printf("[PUNCH] 0x7C from %s (ignoring - single port mode)\n",
               packet->systemAddress.ToString(true));
        break;

    case 0x3A:
        printf("[PUNCH] 0x3A from %s (ignoring - single port mode)\n",
               packet->systemAddress.ToString(true));
        break;

    default:
        if (msgId == 0x89 && packet->length >= 13) {
            uint16_t code = *(uint16_t*)(packet->data + 9);
            uint16_t len = *(uint16_t*)(packet->data + 11);
            printf("[PUNCH] Game packet from %u: code=%d len=%d\n", guid, code, len);
            if (m_onGamePacket) m_onGamePacket(guid, packet->data, packet->length);
        } else {
            printf("[PUNCH] msg 0x%02X (%d bytes) from %s\n",
                   msgId, packet->length, packet->systemAddress.ToString(true));
        }
        break;
    }
}

// DualPort facilitator: handle NAT-only traffic. Game traffic goes through host peer.
void MN2MCProxy::handlePunchPacket(SLNet::Packet* packet) {
    unsigned char msgId = packet->data[0];
    SLNet::RakNetGUID g = packet->guid;

    switch (msgId) {
    case ID_NEW_INCOMING_CONNECTION:
        printf("[FACIL] Peer connected: %s (guid=%llu)\n",
               packet->systemAddress.ToString(true), (unsigned long long)g.g);
        break;

    case ID_CONNECTION_REQUEST_ACCEPTED:
        printf("[FACIL] Outgoing connect accepted: %s (guid=%llu)\n",
               packet->systemAddress.ToString(true), (unsigned long long)g.g);
        break;

    case ID_DISCONNECTION_NOTIFICATION:
    case ID_CONNECTION_LOST:
        printf("[FACIL] Peer disconnected: %s\n",
               packet->systemAddress.ToString(true));
        break;

    case 0x7C:
    case 0x3A:
        // NatPunchthroughServer plugin handles these
        printf("[FACIL] NAT 0x%02x from %s (plugin handles)\n",
               msgId, packet->systemAddress.ToString(true));
        break;

    case ID_NAT_PUNCHTHROUGH_SUCCEEDED:
        printf("[FACIL] NAT punchthrough succeeded for %s\n",
               packet->systemAddress.ToString(true));
        break;

    case ID_NAT_PUNCHTHROUGH_FAILED:
        printf("[FACIL] NAT punchthrough failed for %s\n",
               packet->systemAddress.ToString(true));
        break;

    default:
        printf("[FACIL] msg 0x%02X (%d bytes) from %s\n",
               msgId, packet->length, packet->systemAddress.ToString(true));
        break;
    }
}

// DualPort host: game server logic
void MN2MCProxy::handleHostPacket(SLNet::Packet* packet) {
    unsigned char msgId = packet->data[0];
    uint32_t guid = (uint32_t)(packet->guid.g & 0xFFFFFFFF);

    switch (msgId) {
    case ID_NEW_INCOMING_CONNECTION:
        printf("[HOST] Client connected: %s (guid=%u)\n",
               packet->systemAddress.ToString(true), guid);
        if (m_onConnect) m_onConnect(guid);
        break;

    case ID_CONNECTION_REQUEST_ACCEPTED:
        printf("[HOST] Outgoing connect accepted: %s (guid=%llu)\n",
               packet->systemAddress.ToString(true), (unsigned long long)packet->guid.g);
        break;

    case ID_DISCONNECTION_NOTIFICATION:
    case ID_CONNECTION_LOST:
        printf("[HOST] Client disconnected: %s\n",
               packet->systemAddress.ToString(true));
        if (m_onDisconnect) m_onDisconnect(guid);
        break;

    case ID_NAT_PUNCHTHROUGH_SUCCEEDED:
        printf("[HOST] NAT punchthrough succeeded with %s\n",
               packet->systemAddress.ToString(true));
        break;

    case ID_NAT_PUNCHTHROUGH_FAILED:
        printf("[HOST] NAT punchthrough failed with %s\n",
               packet->systemAddress.ToString(true));
        break;

    default:
        if (msgId == 0x89 && packet->length >= 13) {
            uint16_t code = *(uint16_t*)(packet->data + 9);
            uint16_t len = *(uint16_t*)(packet->data + 11);
            printf("[HOST] Game packet from %u: code=%d len=%d\n", guid, code, len);
            if (m_onGamePacket) m_onGamePacket(guid, packet->data, packet->length);
        } else {
            printf("[HOST] msg 0x%02X (%d bytes) from %s\n",
                   msgId, packet->length, packet->systemAddress.ToString(true));
        }
        break;
    }
}

void MN2MCProxy::sendToClient(uint32_t client_guid, uint16_t msgcode, const uint8_t* data, uint32_t len) {
    uint32_t total = 1 + 2 + 2 + len;
    auto* buf = new uint8_t[total];
    buf[0] = 0x89;
    memcpy(buf + 1, &msgcode, 2);
    uint16_t pktLen = (uint16_t)len;
    memcpy(buf + 3, &pktLen, 2);
    if (len > 0) memcpy(buf + 5, data, len);

    sendRawToClient(client_guid, buf, total);
    delete[] buf;
}

void MN2MCProxy::sendRawToClient(uint32_t client_guid, const uint8_t* data, uint32_t len) {
    // Send via host peer in DualPort, punch peer in SinglePort
    SLNet::RakPeerInterface* peer = (m_mode == ProxyMode::DualPort) ? m_hostPeer : m_punchPeer;
    if (!peer) return;

    // Find the specific client by matching low 32 bits of GUID
    unsigned short numSystems;
    peer->GetConnectionList(nullptr, &numSystems);
    if (numSystems == 0) return;

    SLNet::SystemAddress* addrs = new SLNet::SystemAddress[numSystems];
    peer->GetConnectionList(addrs, &numSystems);

    bool sent = false;
    for (int i = 0; i < numSystems; i++) {
        SLNet::RakNetGUID g = peer->GetGuidFromSystemAddress(addrs[i]);
        uint32_t g32 = (uint32_t)(g.g & 0xFFFFFFFF);
        // skip our own facilitator connection (host-to-facil in DualPort)
        if (m_mode == ProxyMode::DualPort && g.g == m_facilitatorGuid) continue;
        // match the target client
        if (client_guid != 0 && g32 != client_guid) continue;
        peer->Send((const char*)data, len, HIGH_PRIORITY,
                   RELIABLE_ORDERED, 0, addrs[i], false);
        sent = true;
    }
    if (!sent) {
        printf("[PROXY] WARN: sendRawToClient: no peer matching guid=%u\n", client_guid);
    }

    delete[] addrs;
}

void MN2MCProxy::stop() {
    if (m_punchPeer) {
        m_punchPeer->Shutdown(500);
        SLNet::RakPeerInterface::DestroyInstance(m_punchPeer);
        m_punchPeer = nullptr;
    }
    if (m_hostPeer) {
        m_hostPeer->Shutdown(500);
        SLNet::RakPeerInterface::DestroyInstance(m_hostPeer);
        m_hostPeer = nullptr;
    }
    if (m_natPlugin) {
        delete m_natPlugin;
        m_natPlugin = nullptr;
    }
    if (g_hostNatClient) {
        delete g_hostNatClient;
        g_hostNatClient = nullptr;
    }
}
