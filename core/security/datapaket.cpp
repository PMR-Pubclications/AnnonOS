#pragma pack(push, 1)
struct SecurePayloadHeader {
    uint32_t magicBytes;       // e.g., 0xAF05 (AnonOS Secure Gate)
    uint8_t  sourceType;       // 0x01: Android NDK, 0x02: Windows MF, 0x03: macOS AVF
    uint8_t  authStatus;       // 0x00: Pre-Auth (3 FPS Throttled), 0x01: Post-Auth (Full Stream)
    uint64_t timestamp;        // Epoch milliseconds
    uint32_t payloadSize;      // Size of the raw frame/audio buffer following header
};
#pragma pack(pop)
