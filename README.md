# LTE Rack OLED Display

Raspberry Pi Zero-basierte Status-Anzeige zur Überwachung des Teltonika RUT241 LTE-Routers per SNMP auf einem 2.23" Waveshare OLED-Display.

## ✨ Features

- ✅ **Vollständig implementiert und einsatzbereit**
- 📡 Echtzeit-SNMP-Überwachung des RUT241 LTE-Router-Status
- 📊 Anzeige von Signalstärke (RSSI, RSRP, RSRQ, SINR), Netzwerktyp, Operator und Verbindungsstatus
- 🖥️ Optimiert für Raspberry Pi Zero (minimaler Ressourcenverbrauch)
- 🔒 Sicherheitsorientiertes Dependency-Management
- 🧪 Test-Tools für SNMP ohne Display-Hardware
- ⚙️ Automatisches Installations-Script
- 🔄 Systemd-Service für Autostart
- 📝 Umfassende Dokumentation

## 🚀 Schnellstart (Automatische Installation)

### Einfachste Methode

```bash
# Repository klonen
git clone <your-repo-url>
cd LTE_Rack_OLED

# Automatisches Installations-Script ausführen
chmod +x install.sh
./install.sh

# Konfiguration anpassen
nano config.env

# SNMP-Verbindung testen (ohne Display)
source venv/bin/activate
python3 test_snmp.py

# Hauptanwendung starten
python3 src/main.py
```

Das war's! Das Script installiert automatisch alle Abhängigkeiten, erstellt das Virtual Environment und kann optional einen Systemd-Service einrichten.

## 📋 Manuelle Installation

### Voraussetzungen

```bash
# System aktualisieren
sudo apt-get update && sudo apt-get upgrade -y

# System-Abhängigkeiten installieren
sudo apt-get install -y python3 python3-pip python3-venv i2c-tools

# I2C-Schnittstelle aktivieren
sudo raspi-config
# Navigieren zu: Interface Options -> I2C -> Enable
```

### Installation

```bash
# Repository klonen
git clone <your-repo-url>
cd LTE_Rack_OLED

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip install --upgrade pip
pip install -r requirements.txt

# Anwendung konfigurieren
cp config.env.example config.env
nano config.env  # Mit Ihren Einstellungen bearbeiten
```

### Alternative: Performance-optimierte Installation

For better performance on Pi Zero (lower memory, faster execution):

```bash
# Install system dependency for easysnmp
sudo apt-get install -y libsnmp-dev

# Install performance-optimized dependencies
pip install -r requirements-performance.txt
```

## Dependency Management

### Security First

All dependencies are:
- ✅ Currently maintained and updated
- ✅ Free from known security vulnerabilities
- ✅ Minimal and purpose-specific
- ✅ Tested on Raspberry Pi Zero

### Dependency Choices

**SNMP Library**: `pysnmp-lextudio` (maintained fork)
- Original `pysnmp` is abandoned
- Security updates and Python 3.11+ support
- Alternative: `easysnmp` for performance (see requirements-performance.txt)

**Display Driver**: `luma.oled`
- Well-maintained, active community
- Supports Waveshare displays
- Efficient for embedded systems

**Image Processing**: `Pillow`
- Latest version with security patches
- Required for OLED rendering

### Regular Updates

```bash
# Check for outdated packages
pip list --outdated

# Security audit
pip install pip-audit
pip-audit

# Update dependencies (carefully)
pip install --upgrade pip-audit
pip-audit
```

## 📦 Projekt-Struktur

```
LTE_Rack_OLED/
├── src/
│   ├── __init__.py              # Modul-Initialisierung
│   ├── snmp_client.py           # SNMP Client für RUT241
│   ├── display_handler.py       # OLED Display Handler
│   └── main.py                  # Hauptanwendung (ausführbar)
├── requirements.txt              # Produktions-Abhängigkeiten (Standard)
├── requirements-performance.txt  # Performance-optimiert (Alternative)
├── requirements-dev.txt          # Entwicklungs-Tools
├── config.env.example            # Konfigurations-Vorlage
├── test_snmp.py                 # SNMP Test-Tool (ohne Display)
├── install.sh                   # Automatisches Installations-Script
├── .python-version              # Python 3.11.7
├── .gitignore                   # Git ignore Regeln
├── DEPENDENCY_ANALYSIS.md       # Detaillierte Abhängigkeits-Analyse
├── USAGE.md                     # Umfassende Verwendungsanleitung
└── README.md                    # Diese Datei
```

## 🎯 Verwendung

### 1. SNMP-Verbindung testen (ohne Display)

Ideal zum Debuggen oder wenn kein Display angeschlossen ist:

```bash
source venv/bin/activate
python3 test_snmp.py

# Oder mit spezifischen Parametern:
python3 test_snmp.py 192.168.1.1 public
```

Das Test-Script bietet ein interaktives Menü mit verschiedenen Test-Optionen.

### 2. Hauptanwendung starten

Mit OLED-Display:

```bash
source venv/bin/activate
python3 src/main.py
```

### 3. Als Systemd-Service (Autostart)

Wenn während der Installation aktiviert:

```bash
# Service starten
sudo systemctl start lte-rack-oled

# Service-Status prüfen
sudo systemctl status lte-rack-oled

# Logs ansehen
sudo journalctl -u lte-rack-oled -f
```

### 4. In eigenem Code verwenden

```python
from src.snmp_client import RUT241SNMPClient

# SNMP Client erstellen
client = RUT241SNMPClient(host='192.168.1.1', community='public')

# Status abrufen
status = client.get_all_status()
print(f"Signalstärke: {status['signal_strength']} dBm")
print(f"Operator: {status['operator']}")
print(f"Netzwerk: {status['network_type']}")
```

## Configuration

Edit `config.env` with your settings:

```bash
# Basic SNMP v2c (simple)
SNMP_HOST=192.168.1.1
SNMP_COMMUNITY=public
SNMP_VERSION=2c

# Secure SNMP v3 (recommended for production)
SNMP_VERSION=3
SNMP_USER=your_username
SNMP_AUTH_PASSWORD=your_auth_password
SNMP_PRIV_PASSWORD=your_priv_password
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Code formatting
black .

# Linting
flake8 src/

# Security audit
pip-audit
```

## Troubleshooting

### I2C Not Working
```bash
# Check I2C devices
sudo i2cdetect -y 1

# If not found, ensure I2C is enabled
sudo raspi-config
```

### SNMP Connection Issues
```bash
# Test SNMP connection manually
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.1.1.0
```

### Memory Issues on Pi Zero
- Use `requirements-performance.txt` instead
- Reduce display update interval
- Disable unnecessary system services

## Security Recommendations

1. **Use SNMP v3** with authentication and encryption
2. **Never commit** `config.env` to version control
3. **Run regular audits** with `pip-audit`
4. **Keep dependencies updated** (monthly checks)
5. **Use virtual environment** for isolation
6. **Restrict file permissions** on config files

```bash
chmod 600 config.env
```

## Performance Optimization

For best performance on Raspberry Pi Zero:

1. Use `requirements-performance.txt` (easysnmp is faster)
2. Optimize Python execution: `python3 -OO your_script.py`
3. Set appropriate update intervals (5-10 seconds recommended)
4. Consider using systemd service with resource limits

## 📚 Dokumentation

Umfassende Dokumentation für alle Aspekte des Projekts:

- **[README.md](README.md)** (diese Datei) - Übersicht und Schnellstart
- **[USAGE.md](USAGE.md)** - Detaillierte Verwendungsanleitung
  - Alle Verwendungsmöglichkeiten
  - Modul-Dokumentation
  - OID-Referenz für RUT241
  - Troubleshooting-Guide
  - Tipps & Tricks
- **[DEPENDENCY_ANALYSIS.md](DEPENDENCY_ANALYSIS.md)** - Abhängigkeits-Analyse
  - Vollständige Sicherheitsanalyse
  - Bloat-Vermeidung
  - Update-Strategien
  - Performance-Optimierung

## 🔧 Module

### snmp_client.py
SNMP Client für Teltonika RUT241 mit Unterstützung für alle wichtigen OIDs:
- Signalstärke (RSSI, RSRP, RSRQ, SINR)
- Netzwerktyp, Operator, Verbindungsstatus
- System-Informationen
- Formatierte Ausgabe

### display_handler.py
OLED Display Handler für Waveshare 2.23" Display:
- Grafische Signalbalken
- Mehrere Informationen gleichzeitig
- Fehlerbehandlung
- Console-Fallback ohne Hardware

### main.py
Hauptanwendung mit kontinuierlichem Monitoring:
- Konfigurierbares Update-Intervall
- Verbindungstest beim Start
- Automatische Fehlerbehandlung
- Systemd-Service-kompatibel

### test_snmp.py
Interaktives Test-Tool ohne Display-Hardware:
- Menü-gesteuerte Tests
- Alle OIDs testen
- Eigene OIDs ausprobieren
- Ideal zum Debuggen

## License

[Your License Here]

## Contributing

1. Follow dependency management guidelines in DEPENDENCY_ANALYSIS.md
2. Run security audit before submitting PRs
3. Keep dependencies minimal
4. Test on actual Raspberry Pi Zero hardware

## Support

For issues related to:
- **Dependencies**: See DEPENDENCY_ANALYSIS.md
- **Hardware**: Check Waveshare documentation
- **SNMP**: Refer to RUT241 documentation
- **General issues**: Open GitHub issue

---

**Letzte Aktualisierung**: 2026-01-11
**Ziel-Platform**: Raspberry Pi Zero W/WH
**Python-Version**: 3.11.7
**Status**: ✅ Vollständig implementiert und einsatzbereit
