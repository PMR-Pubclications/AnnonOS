#!/usr/bin/env bash
# /opt/annonos/deploy_annonos.sh
# Production deployment and directory initialization script for AnnonOS

set -e

echo "=================================================="
echo "Initializing AnnonOS Production Environment..."
echo "=================================================="

# 1. Create directory hierarchy
sudo mkdir -p /opt/annonos/core/kernel
sudo mkdir -p /opt/annonos/core/chain_of_custody
sudo mkdir -p /opt/annonos/core/resource_manager
sudo mkdir -p /opt/annonos/core/security
sudo mkdir -p /opt/annonos/core/hardware_layer
sudo mkdir -p /opt/annonos/core/ai
sudo mkdir -p /opt/annonos/core/navigation
sudo mkdir -p /opt/annonos/data

# 2. Set secure permissions (Restricted root access for kernel security)
sudo chmod -R 700 /opt/annonos
sudo chmod 755 /opt/annonos/data

echo "Directory tree established successfully."

# 3. Verify Trust-Main repository link
if [ -d "/opt/trust-main" ]; then
    echo "Trust-Main repository detected at /opt/trust-main."
else
    echo "NOTICE: /opt/trust-main not found. Cloning PMR-Publications Trust-Main..."
    sudo git clone https://github.com/PMR-Pubclications/Trust-Main.git /opt/trust-main || echo "Manual git clone required."
fi

# 4. Initialize SQLite Ledger Database
LEDGER_DB="/opt/annonos/data/ledger.db"
if [ ! -f "$LEDGER_DB" ]; then
    echo "Initializing cryptographic Merkle ledger database..."
    python3 -c "import sqlite3; conn = sqlite3.connect('$LEDGER_DB'); cursor = conn.cursor(); cursor.execute('CREATE TABLE IF NOT EXISTS ledger_blocks (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp REAL, payload TEXT, previous_hash TEXT, current_hash TEXT);'); conn.commit(); conn.close();"
    echo "Ledger database initialized."
fi

echo "=================================================="
echo "AnnonOS environment ready. Launch kernel with:"
echo "sudo python3 /opt/annonos/core/kernel/annon_init.py"
echo "=================================================="
