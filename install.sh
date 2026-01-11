#!/bin/bash
#
# Installations-Script für LTE Rack OLED Monitor
# Für Raspberry Pi Zero mit Raspberry Pi OS
#

set -e

echo "=============================================="
echo "LTE Rack OLED Monitor - Installation"
echo "=============================================="
echo ""

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funktionen
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Prüfe ob als root ausgeführt
if [ "$EUID" -eq 0 ]; then
    print_error "Bitte NICHT als root ausführen!"
    print_info "Verwenden Sie: ./install.sh"
    exit 1
fi

# System-Updates
print_info "System-Pakete aktualisieren..."
sudo apt-get update

# Python und Entwicklungstools installieren
print_info "Installiere Python und Entwicklungstools..."
sudo apt-get install -y python3 python3-pip python3-venv python3-dev

# I2C Tools installieren (für OLED Display)
print_info "Installiere I2C Tools..."
sudo apt-get install -y i2c-tools

# Optional: SNMP Tools für Debugging
read -p "SNMP Debugging-Tools installieren? (j/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    print_info "Installiere SNMP Tools..."
    sudo apt-get install -y snmp snmp-mibs-downloader
fi

# I2C aktivieren
print_info "Prüfe I2C-Konfiguration..."
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    print_warn "I2C ist nicht aktiviert!"
    echo ""
    echo "Bitte aktivieren Sie I2C:"
    echo "  1. Führen Sie aus: sudo raspi-config"
    echo "  2. Wählen Sie: Interface Options -> I2C -> Enable"
    echo "  3. Starten Sie neu"
    echo ""
    read -p "I2C später manuell aktivieren? (j/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Jj]$ ]]; then
        exit 1
    fi
fi

# Virtual Environment erstellen
print_info "Erstelle Virtual Environment..."
python3 -m venv venv

# Virtual Environment aktivieren und Pakete installieren
print_info "Installiere Python-Pakete..."
source venv/bin/activate

# pip upgraden
pip install --upgrade pip

# Abhängigkeiten installieren
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_info "Standard-Abhängigkeiten installiert"
else
    print_error "requirements.txt nicht gefunden!"
    exit 1
fi

# Optional: Performance-optimierte Version
echo ""
read -p "Performance-optimierte Version installieren (easysnmp)? (j/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    print_info "Installiere libsnmp-dev..."
    sudo apt-get install -y libsnmp-dev

    print_info "Installiere easysnmp..."
    pip install easysnmp==0.2.6
fi

# Konfigurationsdatei erstellen
if [ ! -f "config.env" ]; then
    print_info "Erstelle config.env aus Vorlage..."
    cp config.env.example config.env
    print_warn "Bitte bearbeiten Sie config.env mit Ihren Einstellungen!"
    echo ""
    echo "Wichtige Einstellungen:"
    echo "  SNMP_HOST=<IP des RUT241>"
    echo "  SNMP_COMMUNITY=<Community String>"
    echo ""
else
    print_info "config.env existiert bereits"
fi

# Hauptscript ausführbar machen
chmod +x src/main.py
chmod +x test_snmp.py

# Systemd Service (optional)
echo ""
read -p "Systemd Service installieren (Autostart)? (j/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    print_info "Erstelle Systemd Service..."

    SERVICE_FILE="/etc/systemd/system/lte-rack-oled.service"
    INSTALL_DIR=$(pwd)
    USER=$(whoami)

    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=LTE Rack OLED Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/src/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable lte-rack-oled.service

    print_info "Service installiert!"
    echo ""
    echo "Service-Befehle:"
    echo "  sudo systemctl start lte-rack-oled    # Starten"
    echo "  sudo systemctl stop lte-rack-oled     # Stoppen"
    echo "  sudo systemctl status lte-rack-oled   # Status"
    echo "  sudo journalctl -u lte-rack-oled -f   # Logs ansehen"
    echo ""
fi

# Zusammenfassung
echo ""
print_info "=============================================="
print_info "Installation abgeschlossen!"
print_info "=============================================="
echo ""
echo "Nächste Schritte:"
echo ""
echo "1. Konfiguration bearbeiten:"
echo "   nano config.env"
echo ""
echo "2. SNMP-Verbindung testen:"
echo "   source venv/bin/activate"
echo "   python3 test_snmp.py"
echo ""
echo "3. Hauptanwendung starten:"
echo "   source venv/bin/activate"
echo "   python3 src/main.py"
echo ""
echo "Dokumentation:"
echo "   - README.md: Schnellstart"
echo "   - DEPENDENCY_ANALYSIS.md: Detaillierte Informationen"
echo ""

deactivate 2>/dev/null || true

print_info "Installation erfolgreich abgeschlossen!"
