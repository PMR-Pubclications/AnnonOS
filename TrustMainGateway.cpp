bool TrustMainGateway::initialize() {
    // 1. Initialize OpenSSL Server Context
    SSL_library_init();
    SSL_load_error_strings();
    const SSL_METHOD* method = TLS_server_method();
    m_sslContext = SSL_CTX_new(method);
    
    if (!m_sslContext) {
        std::cerr << "[-] Failed to create SSL context." << std::endl;
        return false;
    }

    // 2. Load Local CA to verify incoming client certificates (mTLS enforcement)
    // This ensures Trust-Main only accepts connections from clients signed by your local CA.
    if (SSL_CTX_load_verify_locations(m_sslContext, "certs/localCA.crt", nullptr) <= 0) {
        std::cerr << "[-] Failed to load localCA.crt for client verification." << std::endl;
        return false;
    }

    // 3. Load Server's Identity Certificate & Private Key
    if (SSL_CTX_use_certificate_file(m_sslContext, "certs/server.crt", SSL_FILETYPE_PEM) <= 0) {
        std::cerr << "[-] Failed to load server.crt." << std::endl;
        return false;
    }
    
    if (SSL_CTX_use_PrivateKey_file(m_sslContext, "certs/server.key", SSL_FILETYPE_PEM) <= 0) {
        std::cerr << "[-] Failed to load server.key." << std::endl;
        return false;
    }

    // 4. Force Mandatory Client Certificate Verification (Strict mTLS)
    // This rejects any connection attempt that doesn't present a valid client cert.
    SSL_CTX_set_verify(m_sslContext, SSL_VERIFY_PEER | SSL_VERIFY_FAIL_IF_NO_PEER_CERT, nullptr);

    // 5. Proceed with standard socket binding and port listening...
    // (Your existing socket bind code goes here)

    std::cout << "[+] TrustMainGateway successfully initialized with mTLS cert bindings." << std::endl;
    return true;
}
