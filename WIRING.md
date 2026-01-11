# Verkabelungsanleitung - KY040 Rotary Encoder & OLED Display

## Übersicht

Dieses Dokument beschreibt die Verkabelung des Raspberry Pi Zero mit:
- **Waveshare 2.23" OLED Display** (128x64 Pixel, SSD1305)
- **KY040 Rotary Encoder** (Drehgeber mit Druckknopf)

---

## 🔌 Hardware-Anforderungen

### Komponenten
- Raspberry Pi Zero W/WH
- Waveshare 2.23" OLED Display (128x64)
- KY040 Rotary Encoder Modul
- Jumper-Kabel (Female-to-Female oder Female-to-Male)
- Breadboard (optional, für einfacheren Aufbau)

### Netzteil
- 5V, mindestens 1A (besser 2A für stabilen Betrieb)

---

## 📟 Waveshare 2.23" OLED Display

### Display Spezifikationen
- **Auflösung**: 128x64 Pixel
- **Controller**: SSD1305
- **Interface**: SPI (4-Wire)
- **Betriebsspannung**: 3.3V
- **Helligkeit**: Einstellbar

### Verkabelung Display

| Display Pin | Raspberry Pi Pin | GPIO | Beschreibung |
|-------------|------------------|------|--------------|
| VCC         | Pin 1            | 3.3V | Stromversorgung |
| GND         | Pin 6            | GND  | Masse |
| DIN (MOSI)  | Pin 19           | GPIO 10 (MOSI) | Daten |
| CLK (SCLK)  | Pin 23           | GPIO 11 (SCLK) | Clock |
| CS          | Pin 24           | GPIO 8 (CE0) | Chip Select |
| DC          | Pin 18           | GPIO 24 | Data/Command |
| RST         | Pin 22           | GPIO 25 | Reset |

### Detaillierte Pinbelegung Display

```
Raspberry Pi Zero           Waveshare OLED
┌──────────────┐            ┌──────────────┐
│   Pin 1  3.3V├───────────►│ VCC          │
│   Pin 6  GND ├───────────►│ GND          │
│   Pin 19 MOSI├───────────►│ DIN          │
│   Pin 23 SCLK├───────────►│ CLK          │
│   Pin 24 CE0 ├───────────►│ CS           │
│   Pin 18 GPIO├───────────►│ DC           │
│   Pin 22 GPIO├───────────►│ RST          │
└──────────────┘            └──────────────┘
```

### SPI Aktivieren

```bash
sudo raspi-config
# Wählen:
# 3 Interface Options
# I4 SPI
# Ja (Enable)
# OK
# Finish
# Reboot: Ja
```

Überprüfung:
```bash
lsmod | grep spi
# Sollte spi_bcm2835 anzeigen
```

---

## 🎛️ KY040 Rotary Encoder

### Encoder Spezifikationen
- **Typ**: Mechanischer Rotary Encoder mit Druckknopf
- **Schritte**: 20 Schritte pro Umdrehung (rastend)
- **Betriebsspannung**: 5V (funktioniert auch mit 3.3V)
- **Ausgänge**: CLK, DT, SW (Button)
- **Bauform**: KY-040 Modul mit Pull-up Widerständen

### Verkabelung Encoder

| KY040 Pin | Raspberry Pi Pin | GPIO | Beschreibung |
|-----------|------------------|------|--------------|
| +         | Pin 1            | 3.3V | Stromversorgung |
| GND       | Pin 9            | GND  | Masse |
| CLK       | Pin 11           | GPIO 17 | Clock Signal |
| DT        | Pin 13           | GPIO 27 | Data Signal |
| SW        | Pin 15           | GPIO 22 | Switch/Button |

**Hinweis**: Die GPIO-Nummern sind über `config.env` konfigurierbar!

### Detaillierte Pinbelegung Encoder

```
Raspberry Pi Zero           KY040 Encoder
┌──────────────┐            ┌──────────────┐
│   Pin 1  3.3V├───────────►│ +            │
│   Pin 9  GND ├───────────►│ GND          │
│   Pin 11 GPIO├───────────►│ CLK          │
│   Pin 13 GPIO├───────────►│ DT           │
│   Pin 15 GPIO├───────────►│ SW           │
└──────────────┘            └──────────────┘
```

### Alternative GPIO Pins

Sie können andere GPIO Pins verwenden, indem Sie die `config.env` anpassen:

```bash
# In config.env
ENCODER_CLK=17    # CLK Pin
ENCODER_DT=27     # DT Pin
ENCODER_SW=22     # SW (Button) Pin
```

Freie GPIO Pins auf Raspberry Pi Zero:
- GPIO 2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 17, 18, 22, 23, 24, 25, 27

---

## 🔄 Gesamtverkabelung

### Raspberry Pi Zero Pinout (40-Pin Header)

```
         3.3V (1) (2)  5V
    SDA  GPIO2 (3) (4)  5V
    SCL  GPIO3 (5) (6)  GND
         GPIO4 (7) (8)  GPIO14  TXD
           GND (9) (10) GPIO15  RXD
ENCODER  GPIO17 (11)(12) GPIO18  DISPLAY
ENCODER  GPIO27 (13)(14) GND
ENCODER  GPIO22 (15)(16) GPIO23
          3.3V (17)(18) GPIO24  DISPLAY
 DISPLAY GPIO10 (19)(20) GND
 DISPLAY GPIO9  (21)(22) GPIO25  DISPLAY
 DISPLAY GPIO11 (23)(24) GPIO8   DISPLAY
           GND (25)(26) GPIO7
         GPIO0  (27)(28) GPIO1
         GPIO5  (29)(30) GND
         GPIO6  (31)(32) GPIO12
         GPIO13 (33)(34) GND
         GPIO19 (35)(36) GPIO16
         GPIO26 (37)(38) GPIO20
           GND (39)(40) GPIO21
```

### Verwendete Pins Zusammenfassung

| Pin # | GPIO | Verwendung | Komponente |
|-------|------|------------|------------|
| 1     | 3.3V | Stromversorgung | Display & Encoder |
| 6     | GND  | Masse | Display |
| 9     | GND  | Masse | Encoder |
| 11    | 17   | CLK | Encoder |
| 13    | 27   | DT | Encoder |
| 15    | 22   | SW | Encoder |
| 18    | 24   | DC | Display |
| 19    | 10   | MOSI/DIN | Display |
| 22    | 25   | RST | Display |
| 23    | 11   | SCLK/CLK | Display |
| 24    | 8    | CE0/CS | Display |

---

## 🛠️ Breadboard Aufbau (Optional)

Für einen übersichtlicheren Aufbau können Sie ein Breadboard verwenden:

```
Raspberry Pi Zero
      │
      ├──3.3V──┬───► OLED VCC
      │        └───► KY040 +
      │
      ├──GND───┬───► OLED GND
      │        └───► KY040 GND
      │
      ├──GPIO10───► OLED DIN
      ├──GPIO11───► OLED CLK
      ├──GPIO8────► OLED CS
      ├──GPIO24───► OLED DC
      ├──GPIO25───► OLED RST
      │
      ├──GPIO17───► KY040 CLK
      ├──GPIO27───► KY040 DT
      └──GPIO22───► KY040 SW
```

---

## 📸 Verkabelungs-Checkliste

### Vor dem Einschalten

- [ ] Alle Verbindungen doppelt geprüft
- [ ] Keine Kurzschlüsse zwischen 3.3V und GND
- [ ] Display-Pins korrekt verbunden (besonders VCC und GND!)
- [ ] Encoder-Pins korrekt verbunden
- [ ] Keine losen Kabel
- [ ] SPI aktiviert in raspi-config

### Nach dem Einschalten

- [ ] Display leuchtet leicht (auch wenn leer)
- [ ] Keine ungewöhnlichen Geräusche oder Gerüche
- [ ] Raspberry Pi bootet normal
- [ ] Test-Script funktioniert

---

## 🧪 Hardware-Tests

### 1. SPI Test

```bash
# SPI Geräte anzeigen
ls -l /dev/spidev*
# Sollte /dev/spidev0.0 und /dev/spidev0.1 zeigen

# SPI Module prüfen
lsmod | grep spi
```

### 2. GPIO Test

```bash
# GPIO Export testen
echo "17" > /sys/class/gpio/export
echo "in" > /sys/class/gpio/gpio17/direction
cat /sys/class/gpio/gpio17/value
# Sollte 0 oder 1 ausgeben

# Aufräumen
echo "17" > /sys/class/gpio/unexport
```

### 3. Display Test

```bash
cd /home/user/LTE_Rack_OLED
source venv/bin/activate
python3 src/display_handler.py
```

### 4. Encoder Test

```bash
cd /home/user/LTE_Rack_OLED
source venv/bin/activate
python3 src/rotary_encoder.py
# Encoder drehen und Knopf drücken
# Strg+C zum Beenden
```

### 5. Vollständiger Test

```bash
cd /home/user/LTE_Rack_OLED
source venv/bin/activate
python3 src/main_with_menu.py
```

---

## 🔧 Troubleshooting

### Problem: Display zeigt nichts an

**Lösungen:**
1. **Stromversorgung prüfen**
   - VCC an 3.3V (NICHT 5V!)
   - GND korrekt verbunden

2. **SPI aktiviert?**
   ```bash
   sudo raspi-config
   # Interface Options -> SPI -> Enable
   sudo reboot
   ```

3. **Verkabelung prüfen**
   - MOSI (GPIO 10) korrekt?
   - SCLK (GPIO 11) korrekt?
   - Alle Pins fest verbunden?

4. **Code-Test**
   ```bash
   python3 src/display_handler.py
   ```

### Problem: Encoder reagiert nicht

**Lösungen:**
1. **GPIO Pins prüfen**
   - CLK, DT, SW korrekt verbunden?
   - Nicht vertauscht?

2. **Stromversorgung**
   - + an 3.3V oder 5V
   - GND verbunden

3. **Code-Test**
   ```bash
   python3 src/rotary_encoder.py
   ```

4. **GPIO Berechtigungen**
   ```bash
   sudo usermod -a -G gpio $USER
   # Logout und wieder einloggen
   ```

### Problem: Encoder dreht in falsche Richtung

**Lösung:**
CLK und DT vertauschen oder in `config.env`:
```bash
ENCODER_CLK=27
ENCODER_DT=17
```

### Problem: Ungewollte Encoder-Signale (Bouncing)

**Lösung:**
In `config.env` Debounce-Zeit erhöhen (in der zukünftigen Version):
```bash
ENCODER_DEBOUNCE=10  # Millisekunden
```

### Problem: Display flackert

**Lösungen:**
1. **Stromversorgung verbessern**
   - Stärkeres Netzteil (2A statt 1A)
   - Kürzere Kabel verwenden

2. **Kondensator hinzufügen**
   - 100µF zwischen 3.3V und GND (nahe Display)

3. **Update-Intervall erhöhen**
   ```bash
   # In config.env
   DISPLAY_UPDATE_INTERVAL=10  # Statt 5
   ```

---

## 💡 Tipps & Best Practices

### Verkabelung

1. **Kurze Kabel verwenden** - Reduziert Störungen und Spannungsabfall
2. **Ordentliche Kabelführung** - Verhindert versehentliches Herausziehen
3. **Beschriftung** - Kabel beschriften für einfachere Fehlersuche
4. **Breadboard** - Für Prototyping sehr hilfreich
5. **Löten** - Für permanenten Aufbau empfohlen

### Stromversorgung

1. **Qualitäts-Netzteil** - Mindestens 2A für stabilen Betrieb
2. **Nicht über USB** - Pi Zero braucht stabilen Strom
3. **Kondensatoren** - Für sauberere Stromversorgung

### Schutz

1. **ESD-Schutz** - Vor Berührung erden
2. **Kurzschluss-Schutz** - Doppelt prüfen vor Einschalten
3. **Überspannungsschutz** - Gutes Netzteil verwenden

---

## 📐 Gehäuse-Empfehlungen

### Display-Montage
- Ausschnitt: ca. 60mm x 30mm
- Befestigung: M2.5 Schrauben oder Heißkleber
- Position: Gut sichtbar, nicht direkt über Pi (Wärme)

### Encoder-Montage
- Loch: 7mm Durchmesser
- Befestigung: Mitgelieferte Mutter
- Position: Leicht erreichbar für Bedienung

### Kabel-Management
- Kabel bündeln mit Kabelbindern
- Zugentlastung für Display-Kabel
- Genug Platz für Luftzirkulation

---

## 🔗 Weiterführende Informationen

### Datasheets
- **SSD1305**: https://www.solomon-systech.com/product/ssd1305/
- **KY-040**: Verschiedene Hersteller, kompatibel
- **Raspberry Pi Zero**: https://www.raspberrypi.org/documentation/

### Tutorials
- **Waveshare Wiki**: https://www.waveshare.com/wiki/2.23inch_OLED_HAT
- **luma.oled Docs**: https://luma-oled.readthedocs.io/
- **RPi.GPIO Docs**: https://sourceforge.net/p/raspberry-gpio-python/wiki/

---

## ✅ Checkliste für Erstinbetriebnahme

### Hardware
- [ ] Raspberry Pi Zero W mit Raspberry Pi OS
- [ ] Waveshare 2.23" OLED Display
- [ ] KY040 Rotary Encoder
- [ ] Gute Jumper-Kabel (mind. 10cm)
- [ ] 2A Netzteil

### Software-Vorbereitung
- [ ] Raspberry Pi OS aktualisiert
- [ ] SPI aktiviert (raspi-config)
- [ ] Python 3.11+ installiert
- [ ] git installiert

### Verkabelung
- [ ] Display nach Tabelle verkabelt
- [ ] Encoder nach Tabelle verkabelt
- [ ] Alle Verbindungen fest
- [ ] Keine Kurzschlüsse

### Installation
- [ ] Repository geklont
- [ ] `./install.sh` ausgeführt
- [ ] `config.env` angepasst

### Tests
- [ ] SPI Test erfolgreich
- [ ] GPIO Test erfolgreich
- [ ] Display Test erfolgreich
- [ ] Encoder Test erfolgreich
- [ ] Anwendung startet

---

**Version:** 1.0
**Datum:** 2026-01-11
**Kompatibilität:** Raspberry Pi Zero W/WH, Waveshare 2.23" OLED, KY040
