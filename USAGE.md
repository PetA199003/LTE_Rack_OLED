# Verwendungsanleitung - LTE Rack OLED Monitor

## Schnellstart

### 1. Installation

```bash
# Repository klonen
git clone <repository-url>
cd LTE_Rack_OLED

# Installations-Script ausführen
chmod +x install.sh
./install.sh
```

### 2. Konfiguration

Bearbeiten Sie `config.env`:

```bash
nano config.env
```

Wichtige Einstellungen:
```bash
SNMP_HOST=192.168.1.1        # IP-Adresse Ihres RUT241
SNMP_COMMUNITY=public        # SNMP Community String
DISPLAY_UPDATE_INTERVAL=5    # Update-Intervall in Sekunden
```

### 3. SNMP testen (ohne Display)

```bash
source venv/bin/activate
python3 test_snmp.py
```

Das Test-Script bietet ein interaktives Menü zum Testen verschiedener SNMP-Funktionen.

### 4. Hauptanwendung starten

```bash
source venv/bin/activate
python3 src/main.py
```

## Verwendungsmöglichkeiten

### A) Manuelle Verwendung

**SNMP-Test ohne Display:**
```bash
# Interaktives Menü
python3 test_snmp.py

# Mit spezifischer IP
python3 test_snmp.py 192.168.1.1

# Mit IP und Community
python3 test_snmp.py 192.168.1.1 MeinCommunity
```

**Hauptanwendung:**
```bash
# Mit Konfiguration aus config.env
python3 src/main.py

# Mit Umgebungsvariablen
SNMP_HOST=192.168.1.10 SNMP_COMMUNITY=private python3 src/main.py
```

### B) Als Systemd Service (Autostart)

Wenn während der Installation aktiviert:

```bash
# Service starten
sudo systemctl start lte-rack-oled

# Service stoppen
sudo systemctl stop lte-rack-oled

# Service-Status prüfen
sudo systemctl status lte-rack-oled

# Logs ansehen
sudo journalctl -u lte-rack-oled -f

# Autostart deaktivieren
sudo systemctl disable lte-rack-oled

# Autostart aktivieren
sudo systemctl enable lte-rack-oled
```

### C) Nur SNMP-Modul verwenden (in eigenem Code)

```python
#!/usr/bin/env python3
from src.snmp_client import RUT241SNMPClient

# Client erstellen
client = RUT241SNMPClient(
    host='192.168.1.1',
    community='public'
)

# Einzelne Werte abrufen
signal = client.get_signal_strength()
operator = client.get_operator()
network = client.get_network_type()

print(f"Signal: {signal} dBm")
print(f"Operator: {operator}")
print(f"Netzwerk: {network}")

# Alle Werte auf einmal
status = client.get_all_status()
print(status)

# Formatierte Ausgabe
print(client.format_signal_strength(signal))
```

## Verfügbare Module

### 1. snmp_client.py

SNMP-Client für RUT241 Router.

**Hauptklasse:** `RUT241SNMPClient`

**Wichtige Methoden:**
- `get_signal_strength()` - RSSI in dBm
- `get_network_type()` - Netzwerktyp (LTE, 3G, etc.)
- `get_operator()` - Mobilfunk-Operator
- `get_connection_state()` - Verbindungsstatus
- `get_signal_details()` - RSSI, RSRP, RSRQ, SINR
- `get_all_status()` - Alle Werte auf einmal
- `format_signal_strength(rssi)` - Formatierte Signalstärke

**Verwendung:**
```python
from src.snmp_client import RUT241SNMPClient

client = RUT241SNMPClient(host='192.168.1.1', community='public')
status = client.get_all_status()
```

### 2. display_handler.py

OLED Display Handler für Waveshare 2.23" Display.

**Hauptklasse:** `OLEDDisplay`

**Wichtige Methoden:**
- `display_status(status)` - Zeigt Status-Dictionary an
- `display_text(text, x, y)` - Zeigt Text an Position an
- `display_multiline(lines)` - Zeigt mehrere Zeilen an
- `display_error(error_msg)` - Zeigt Fehlermeldung an
- `clear()` - Löscht Display

**Verwendung:**
```python
from src.display_handler import OLEDDisplay

display = OLEDDisplay(width=128, height=64)
display.display_text("Hello World", 10, 20)
```

**Hinweis:** Funktioniert auch ohne echte Hardware (Console-Ausgabe als Fallback).

### 3. main.py

Hauptanwendung - kombiniert SNMP und Display.

**Hauptklasse:** `LTERackMonitor`

**Verwendung:**
```python
from src.main import LTERackMonitor

monitor = LTERackMonitor(
    host='192.168.1.1',
    community='public',
    update_interval=5
)

monitor.test_connection()  # Verbindung testen
monitor.run()              # Monitoring starten
```

## Verfügbare OIDs (RUT241)

### Standard-System-OIDs
```
System Name:        1.3.6.1.2.1.1.5.0
System Description: 1.3.6.1.2.1.1.1.0
System Uptime:      1.3.6.1.2.1.1.3.0
```

### Teltonika RUT241 spezifisch
```
Signalstärke (RSSI): 1.3.6.1.4.1.48690.2.1.1.2.1.0
RSRP:                1.3.6.1.4.1.48690.2.1.1.2.2.0
RSRQ:                1.3.6.1.4.1.48690.2.1.1.2.3.0
SINR:                1.3.6.1.4.1.48690.2.1.1.2.4.0
Netzwerktyp:         1.3.6.1.4.1.48690.2.1.1.3.1.0
Operator:            1.3.6.1.4.1.48690.2.1.1.4.1.0
Verbindungsstatus:   1.3.6.1.4.1.48690.2.1.1.5.1.0
WAN IP:              1.3.6.1.4.1.48690.2.3.1.0
```

## Troubleshooting

### Problem: "Keine Verbindung zum Router"

**Lösung:**
1. IP-Adresse prüfen: `ping 192.168.1.1`
2. SNMP aktiviert?: Router-Web-Interface -> Services -> SNMP
3. Community String korrekt?
4. Firewall-Regeln prüfen

**Test mit snmpget:**
```bash
snmpget -v2c -c public 192.168.1.1 1.3.6.1.2.1.1.1.0
```

### Problem: "Display nicht gefunden"

**Lösung:**
1. I2C aktiviert?
   ```bash
   sudo raspi-config
   # Interface Options -> I2C -> Enable
   ```

2. I2C-Geräte prüfen:
   ```bash
   sudo i2cdetect -y 1
   ```

3. Verkabelung prüfen (SPI):
   - VCC -> 3.3V
   - GND -> GND
   - DIN -> MOSI (GPIO 10)
   - CLK -> SCLK (GPIO 11)
   - CS -> CE0 (GPIO 8)
   - DC -> GPIO 24
   - RST -> GPIO 25

### Problem: "pip install schlägt fehl"

**Lösung:**
```bash
# Virtual Environment neu erstellen
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# pip upgraden
pip install --upgrade pip

# Abhängigkeiten neu installieren
pip install -r requirements.txt
```

### Problem: "Zu langsam auf Pi Zero"

**Lösung:**
Verwenden Sie die Performance-optimierte Version:

```bash
# System-Bibliothek installieren
sudo apt-get install libsnmp-dev

# Performance-Abhängigkeiten installieren
source venv/bin/activate
pip install -r requirements-performance.txt
```

## Tipps & Tricks

### 1. Update-Intervall anpassen

Je kleiner das Intervall, desto mehr CPU-Last:
```bash
# In config.env
DISPLAY_UPDATE_INTERVAL=10  # 10 Sekunden statt 5
```

### 2. Nur Console-Ausgabe (ohne Display)

Der Display-Handler funktioniert automatisch als Fallback ohne echte Hardware und gibt auf der Console aus.

### 3. Logging anpassen

```python
# In src/main.py
logging.basicConfig(
    level=logging.DEBUG,  # Mehr Details
    # level=logging.WARNING,  # Weniger Details
)
```

### 4. Eigene OIDs hinzufügen

```python
# In src/snmp_client.py, OIDS Dictionary erweitern:
OIDS = {
    # ... bestehende OIDs ...
    'my_custom_oid': '1.3.6.1.4.1.48690.x.x.x',
}

# Eigene Methode hinzufügen:
def get_my_custom_value(self):
    return self.get_oid(self.OIDS['my_custom_oid'])
```

### 5. SNMP v3 verwenden (sicherer)

In `config.env`:
```bash
SNMP_VERSION=3
SNMP_USER=your_username
SNMP_AUTH_PROTOCOL=SHA
SNMP_AUTH_PASSWORD=your_auth_password
SNMP_PRIV_PROTOCOL=AES
SNMP_PRIV_PASSWORD=your_priv_password
```

**Hinweis:** SNMP v3 Support muss in `snmp_client.py` noch implementiert werden.

## Weiterführende Ressourcen

- **RUT241 Manual:** https://wiki.teltonika-networks.com/view/RUT241
- **SNMP OIDs:** https://wiki.teltonika-networks.com/view/RUT241_SNMP
- **Waveshare Display:** https://www.waveshare.com/wiki/2.23inch_OLED_HAT
- **pysnmp Dokumentation:** https://pysnmp.readthedocs.io/
- **luma.oled Dokumentation:** https://luma-oled.readthedocs.io/

## Support

Bei Problemen:
1. Prüfen Sie die Logs: `sudo journalctl -u lte-rack-oled -f`
2. Testen Sie SNMP separat: `python3 test_snmp.py`
3. Prüfen Sie die Hardware-Verbindung
4. Siehe DEPENDENCY_ANALYSIS.md für detaillierte Informationen

---

**Version:** 1.0.0
**Letzte Aktualisierung:** 2026-01-11
