"""
OLED Display Handler für 2.23" Waveshare OLED Display
Zeigt LTE Status-Informationen an
"""

import logging
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont

try:
    from luma.core.interface.serial import spi
    from luma.core.render import canvas
    from luma.oled.device import ssd1305
    DISPLAY_AVAILABLE = True
except ImportError:
    DISPLAY_AVAILABLE = False
    logging.warning("luma.oled nicht installiert - Display-Funktionen nicht verfügbar")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OLEDDisplay:
    """
    Handler für 2.23" Waveshare OLED Display (128x64 Pixel)

    Unterstützt SPI-Verbindung zum Raspberry Pi
    """

    def __init__(self, width: int = 128, height: int = 64):
        """
        Initialisiert das OLED Display

        Args:
            width: Display-Breite in Pixel (Standard: 128)
            height: Display-Höhe in Pixel (Standard: 64)
        """
        self.width = width
        self.height = height
        self.device = None

        if not DISPLAY_AVAILABLE:
            logger.warning("Display-Bibliotheken nicht verfügbar - Dummy-Modus aktiv")
            return

        try:
            # SPI-Verbindung initialisieren
            # Waveshare 2.23" OLED verwendet SSD1305 Controller
            serial = spi(device=0, port=0)
            self.device = ssd1305(serial, width=width, height=height)
            logger.info(f"OLED Display initialisiert ({width}x{height})")
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren des Displays: {e}")
            logger.warning("Fortfahren im Dummy-Modus")

    def clear(self):
        """Löscht den Display-Inhalt"""
        if self.device:
            self.device.clear()

    def draw_signal_bars(self, draw: ImageDraw, x: int, y: int, rssi: Optional[int]):
        """
        Zeichnet Signal-Balken basierend auf RSSI

        Args:
            draw: ImageDraw Objekt
            x: X-Position
            y: Y-Position
            rssi: RSSI-Wert in dBm
        """
        bar_width = 4
        bar_spacing = 2
        max_height = 12

        if rssi is None:
            # Zeichne "X" bei keinem Signal
            draw.text((x, y), "X", fill="white")
            return

        # Berechne Anzahl der aktiven Balken (1-5)
        if rssi >= -70:
            active_bars = 5
        elif rssi >= -85:
            active_bars = 4
        elif rssi >= -100:
            active_bars = 3
        elif rssi >= -110:
            active_bars = 2
        else:
            active_bars = 1

        # Zeichne 5 Balken mit unterschiedlicher Höhe
        for i in range(5):
            bar_x = x + i * (bar_width + bar_spacing)
            bar_height = ((i + 1) * max_height) // 5

            if i < active_bars:
                # Aktiver Balken (gefüllt)
                draw.rectangle(
                    [bar_x, y + max_height - bar_height, bar_x + bar_width, y + max_height],
                    fill="white"
                )
            else:
                # Inaktiver Balken (Umriss)
                draw.rectangle(
                    [bar_x, y + max_height - bar_height, bar_x + bar_width, y + max_height],
                    outline="white"
                )

    def display_status(self, status: Dict[str, Any]):
        """
        Zeigt Status-Informationen auf dem Display an

        Args:
            status: Dictionary mit Status-Informationen vom SNMP Client
        """
        if not self.device:
            # Dummy-Modus: Ausgabe in Console
            self._print_status_console(status)
            return

        try:
            with canvas(self.device) as draw:
                # Standard-Font verwenden (PIL default)
                # Für bessere Fonts: ImageFont.truetype("/path/to/font.ttf", size)

                # Zeile 1: Operator und Netzwerktyp
                operator = status.get('operator', 'N/A')
                network_type = status.get('network_type', 'N/A')
                draw.text((2, 2), f"{operator}", fill="white")
                draw.text((90, 2), f"{network_type}", fill="white")

                # Zeile 2: Trennlinie
                draw.line([(0, 14), (128, 14)], fill="white")

                # Zeile 3: Verbindungsstatus
                conn_state = status.get('connection_state', 'N/A')
                draw.text((2, 18), f"Status: {conn_state}", fill="white")

                # Zeile 4: Signal-Balken und RSSI
                rssi = status.get('signal_strength')
                self.draw_signal_bars(draw, 2, 32)
                if rssi is not None:
                    draw.text((40, 32), f"{rssi} dBm", fill="white")
                else:
                    draw.text((40, 32), "N/A", fill="white")

                # Zeile 5: Zusätzliche Signal-Details (wenn verfügbar)
                details = status.get('signal_details', {})
                y_pos = 48
                if details.get('rsrp'):
                    draw.text((2, y_pos), f"RSRP:{details['rsrp']}", fill="white")
                if details.get('rsrq'):
                    draw.text((65, y_pos), f"RSRQ:{details['rsrq']}", fill="white")

            logger.debug("Display aktualisiert")

        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Displays: {e}")

    def display_text(self, text: str, x: int = 0, y: int = 0):
        """
        Zeigt einfachen Text auf dem Display an

        Args:
            text: Anzuzeigender Text
            x: X-Position (Standard: 0)
            y: Y-Position (Standard: 0)
        """
        if not self.device:
            print(f"[Display] {text}")
            return

        try:
            with canvas(self.device) as draw:
                draw.text((x, y), text, fill="white")
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen von Text: {e}")

    def display_multiline(self, lines: list):
        """
        Zeigt mehrere Textzeilen auf dem Display an

        Args:
            lines: Liste mit Textzeilen
        """
        if not self.device:
            for line in lines:
                print(f"[Display] {line}")
            return

        try:
            with canvas(self.device) as draw:
                y = 2
                line_height = 12
                for line in lines[:5]:  # Max 5 Zeilen für 64px Höhe
                    draw.text((2, y), str(line), fill="white")
                    y += line_height
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen mehrerer Zeilen: {e}")

    def display_error(self, error_msg: str):
        """
        Zeigt eine Fehlermeldung auf dem Display an

        Args:
            error_msg: Fehlermeldung
        """
        if not self.device:
            print(f"[Display ERROR] {error_msg}")
            return

        try:
            with canvas(self.device) as draw:
                # Große "ERROR" Überschrift
                draw.text((20, 10), "ERROR", fill="white")
                draw.line([(0, 24), (128, 24)], fill="white")

                # Fehlermeldung (max 3 Zeilen)
                words = error_msg.split()
                lines = []
                current_line = ""

                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if len(test_line) <= 18:  # ca. 18 Zeichen pro Zeile
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word

                if current_line:
                    lines.append(current_line)

                y = 30
                for line in lines[:3]:
                    draw.text((2, y), line, fill="white")
                    y += 12

        except Exception as e:
            logger.error(f"Fehler beim Anzeigen der Fehlermeldung: {e}")

    def _print_status_console(self, status: Dict[str, Any]):
        """
        Gibt Status in der Console aus (Fallback ohne Display)

        Args:
            status: Status-Dictionary
        """
        print("\n" + "="*50)
        print("📺 OLED DISPLAY (Console-Modus)")
        print("="*50)
        print(f"Operator: {status.get('operator', 'N/A')}")
        print(f"Netzwerk: {status.get('network_type', 'N/A')}")
        print(f"Status: {status.get('connection_state', 'N/A')}")

        rssi = status.get('signal_strength')
        if rssi is not None:
            bars = "█" * min(5, max(1, (rssi + 110) // 10))
            print(f"Signal: {bars} {rssi} dBm")
        else:
            print("Signal: N/A")

        details = status.get('signal_details', {})
        if details:
            print(f"Details: RSRP={details.get('rsrp', 'N/A')} "
                  f"RSRQ={details.get('rsrq', 'N/A')} "
                  f"SINR={details.get('sinr', 'N/A')}")
        print("="*50)


def main():
    """Test-Funktion"""
    print("OLED Display Test")
    print("="*50)

    display = OLEDDisplay()

    # Test 1: Einfacher Text
    print("\nTest 1: Einfacher Text")
    display.display_text("Hello World!", 10, 20)
    input("Drücken Sie Enter für den nächsten Test...")

    # Test 2: Mehrere Zeilen
    print("\nTest 2: Mehrere Zeilen")
    display.display_multiline([
        "Zeile 1",
        "Zeile 2",
        "Zeile 3",
        "Zeile 4"
    ])
    input("Drücken Sie Enter für den nächsten Test...")

    # Test 3: Status-Anzeige (simuliert)
    print("\nTest 3: Status-Anzeige")
    test_status = {
        'operator': 'Telekom',
        'network_type': 'LTE',
        'connection_state': 'Connected',
        'signal_strength': -75,
        'signal_details': {
            'rsrp': -95,
            'rsrq': -10,
            'sinr': 13
        }
    }
    display.display_status(test_status)
    input("Drücken Sie Enter für den nächsten Test...")

    # Test 4: Fehlermeldung
    print("\nTest 4: Fehlermeldung")
    display.display_error("Verbindung zum Router fehlgeschlagen")
    input("Drücken Sie Enter zum Beenden...")

    display.clear()
    print("\nTest abgeschlossen!")


if __name__ == '__main__':
    main()
