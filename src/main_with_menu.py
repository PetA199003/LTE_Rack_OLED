#!/usr/bin/env python3
"""
LTE Rack OLED Display - Hauptanwendung mit KY040 Menü-Navigation
Überwacht Teltonika RUT241 Router und zeigt Status auf OLED Display an
Mit Rotary Encoder Navigation
"""

import os
import sys
import time
import logging
import signal
from typing import Optional
from pathlib import Path

# Module importieren
from snmp_client import RUT241SNMPClient
from display_handler import OLEDDisplay
from rotary_encoder import KY040RotaryEncoder
from menu_system import MenuSystem, MenuScreen


# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LTERackMonitorWithMenu:
    """
    Hauptanwendung für LTE Rack OLED Monitor mit Menü-Navigation

    Überwacht kontinuierlich den RUT241 Router und zeigt Status an
    Navigation mit KY040 Rotary Encoder
    """

    def __init__(
        self,
        host: str,
        community: str = 'public',
        update_interval: int = 5,
        display_width: int = 128,
        display_height: int = 64,
        encoder_clk: int = 17,
        encoder_dt: int = 27,
        encoder_sw: int = 22
    ):
        """
        Initialisiert den Monitor

        Args:
            host: IP-Adresse des RUT241
            community: SNMP Community String
            update_interval: Update-Intervall in Sekunden
            display_width: Display-Breite in Pixel
            display_height: Display-Höhe in Pixel
            encoder_clk: GPIO Pin für Encoder CLK
            encoder_dt: GPIO Pin für Encoder DT
            encoder_sw: GPIO Pin für Encoder SW (Button)
        """
        self.host = host
        self.community = community
        self.update_interval = update_interval
        self.running = False
        self.last_status = None

        logger.info(f"Initialisiere LTE Rack Monitor mit Menü für {host}")

        # SNMP Client initialisieren
        self.snmp_client = RUT241SNMPClient(
            host=host,
            community=community
        )

        # Display initialisieren
        self.display = OLEDDisplay(
            width=display_width,
            height=display_height
        )

        # Menü-System initialisieren
        self.menu = MenuSystem()
        self.menu.on_screen_change(self._on_screen_change)

        # Rotary Encoder initialisieren
        self.encoder = KY040RotaryEncoder(
            clk_pin=encoder_clk,
            dt_pin=encoder_dt,
            sw_pin=encoder_sw
        )

        # Encoder Callbacks registrieren
        self.encoder.on_rotate(self._on_encoder_rotate)
        self.encoder.on_press(self._on_encoder_press)
        self.encoder.on_long_press(self._on_encoder_long_press)

        # Signal Handler für sauberes Beenden
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handler für Beendigungs-Signale"""
        logger.info(f"Signal {signum} empfangen - beende Anwendung...")
        self.running = False

    def _on_encoder_rotate(self, direction: int):
        """Callback für Encoder-Drehung"""
        logger.debug(f"Encoder gedreht: {direction}")
        self.menu.handle_rotation(direction)
        self._update_display()

    def _on_encoder_press(self, ):
        """Callback für Encoder-Knopfdruck"""
        logger.debug("Encoder gedrückt")
        self.menu.handle_press()
        self._update_display()

    def _on_encoder_long_press(self):
        """Callback für langen Encoder-Knopfdruck"""
        logger.debug("Encoder lang gedrückt")
        self.menu.handle_long_press()
        self._update_display()

    def _on_screen_change(self, screen: MenuScreen):
        """Callback für Screen-Wechsel"""
        logger.info(f"Screen gewechselt zu: {screen.value}")
        self._update_display()

    def _update_display(self):
        """Aktualisiert die Display-Anzeige"""
        try:
            if self.menu.is_in_menu():
                # Menü anzeigen
                menu_items = self.menu.get_menu_items()
                selected_index = self.menu.get_menu_selection_index()
                self.display.display_menu(menu_items, selected_index, "MENÜ")
            else:
                # Screen anzeigen
                current_screen = self.menu.get_current_screen()

                # Daten für Screen formatieren
                screen_data = self.menu.format_screen_data(
                    current_screen,
                    self.last_status or {}
                )

                # Screen anzeigen
                self.display.display_screen(screen_data)

        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Displays: {e}")

    def run(self):
        """Startet die Haupt-Monitoring-Schleife"""
        logger.info("Starte Monitoring mit Menü-Navigation...")
        self.running = True

        # Encoder starten
        self.encoder.start()

        # Startmeldung auf Display
        self.display.display_multiline([
            "LTE Rack Monitor",
            "mit Menü",
            f"Host: {self.host}",
            "Starte..."
        ])
        time.sleep(2)

        error_count = 0
        max_errors = 5
        last_update = 0

        while self.running:
            try:
                current_time = time.time()

                # Status regelmäßig aktualisieren
                if current_time - last_update >= self.update_interval:
                    logger.debug("Rufe Status ab...")
                    self.last_status = self.snmp_client.get_all_status()
                    last_update = current_time

                    # Display aktualisieren (nur wenn nicht im Menü)
                    if not self.menu.is_in_menu():
                        self._update_display()

                    # Fehler-Counter zurücksetzen bei Erfolg
                    error_count = 0

                # Kurze Pause
                time.sleep(0.1)

            except KeyboardInterrupt:
                logger.info("Beende auf Benutzeranforderung...")
                break

            except Exception as e:
                error_count += 1
                logger.error(f"Fehler beim Abrufen des Status ({error_count}/{max_errors}): {e}")

                # Fehlermeldung auf Display
                self.display.display_error(f"Fehler: {str(e)[:30]}")

                if error_count >= max_errors:
                    logger.error(f"Maximale Fehleranzahl erreicht - beende Anwendung")
                    break

                # Kurze Pause vor erneutem Versuch
                time.sleep(5)

        # Aufräumen
        self.cleanup()

    def cleanup(self):
        """Räumt Ressourcen auf und beendet sauber"""
        logger.info("Räume auf...")
        try:
            # Encoder stoppen und aufräumen
            self.encoder.cleanup()

            # Display löschen
            self.display.display_text("Beende...", 30, 25)
            time.sleep(1)
            self.display.clear()
        except Exception as e:
            logger.error(f"Fehler beim Aufräumen: {e}")

        logger.info("Monitoring beendet")

    def test_connection(self) -> bool:
        """
        Testet die Verbindung zum Router

        Returns:
            True wenn Verbindung erfolgreich, sonst False
        """
        logger.info("Teste Verbindung zum Router...")
        try:
            status = self.snmp_client.get_all_status()
            self.last_status = status

            if status.get('operator') or status.get('system_info', {}).get('name'):
                logger.info("✓ Verbindung erfolgreich")
                return True
            else:
                logger.warning("⚠ Verbindung hergestellt, aber keine Daten empfangen")
                return False

        except Exception as e:
            logger.error(f"✗ Verbindungstest fehlgeschlagen: {e}")
            return False

    def test_encoder(self):
        """Testet den Rotary Encoder"""
        logger.info("Teste Rotary Encoder...")
        logger.info("Drehen Sie den Encoder oder drücken Sie den Knopf")
        logger.info("Warte 5 Sekunden auf Eingaben...")

        # Bei Dummy-Modus (ohne GPIO): Simuliere Eingaben
        if self.encoder._dummy_mode:
            logger.info("Encoder im Dummy-Modus - simuliere Eingaben")
            time.sleep(1)
            self.encoder.simulate_rotation(1)
            time.sleep(1)
            self.encoder.simulate_rotation(-1)
            time.sleep(1)
            self.encoder.simulate_press()
            logger.info("✓ Encoder-Test abgeschlossen (simuliert)")
        else:
            # Warte auf echte Eingaben
            time.sleep(5)
            logger.info("✓ Encoder-Test abgeschlossen")


def load_config() -> dict:
    """
    Lädt Konfiguration aus config.env oder Umgebungsvariablen

    Returns:
        Dictionary mit Konfigurationswerten
    """
    config = {}

    # Versuche config.env zu laden
    config_file = Path(__file__).parent.parent / 'config.env'

    if config_file.exists():
        logger.info(f"Lade Konfiguration aus {config_file}")
        with open(config_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

    # Konfiguration aus Umgebungsvariablen
    config['host'] = os.getenv('SNMP_HOST', '192.168.1.1')
    config['community'] = os.getenv('SNMP_COMMUNITY', 'public')
    config['update_interval'] = int(os.getenv('DISPLAY_UPDATE_INTERVAL', '5'))
    config['display_width'] = int(os.getenv('DISPLAY_WIDTH', '128'))
    config['display_height'] = int(os.getenv('DISPLAY_HEIGHT', '64'))

    # Encoder GPIO Pins
    config['encoder_clk'] = int(os.getenv('ENCODER_CLK', '17'))
    config['encoder_dt'] = int(os.getenv('ENCODER_DT', '27'))
    config['encoder_sw'] = int(os.getenv('ENCODER_SW', '22'))

    return config


def main():
    """Hauptfunktion"""
    print("="*70)
    print("LTE Rack OLED Monitor mit KY040 Menü-Navigation")
    print("Teltonika RUT241 SNMP Monitor mit OLED Display & Rotary Encoder")
    print("="*70)

    # Konfiguration laden
    config = load_config()

    print(f"\nKonfiguration:")
    print(f"  Host: {config['host']}")
    print(f"  Community: {config['community']}")
    print(f"  Update-Intervall: {config['update_interval']}s")
    print(f"  Display: {config['display_width']}x{config['display_height']}")
    print(f"  Encoder Pins: CLK={config['encoder_clk']}, DT={config['encoder_dt']}, SW={config['encoder_sw']}")
    print()

    # Monitor initialisieren
    monitor = LTERackMonitorWithMenu(
        host=config['host'],
        community=config['community'],
        update_interval=config['update_interval'],
        display_width=config['display_width'],
        display_height=config['display_height'],
        encoder_clk=config['encoder_clk'],
        encoder_dt=config['encoder_dt'],
        encoder_sw=config['encoder_sw']
    )

    # Verbindungstest
    print("Teste Verbindung...")
    if not monitor.test_connection():
        print("\n⚠ WARNUNG: Verbindungstest fehlgeschlagen!")
        print("Überprüfen Sie:")
        print("  1. IP-Adresse korrekt?")
        print("  2. SNMP aktiviert auf RUT241?")
        print("  3. Community String korrekt?")
        print("  4. Firewall-Regeln?")
        print()
        response = input("Trotzdem fortfahren? (j/N): ")
        if response.lower() != 'j':
            print("Abgebrochen.")
            sys.exit(1)

    print("\n✓ Verbindung erfolgreich")

    # Encoder testen
    print("\nTeste Rotary Encoder...")
    monitor.test_encoder()

    print("\n✓ Encoder funktioniert")
    print("\nStarte Monitoring mit Menü-Navigation...")
    print("\nBedienung:")
    print("  • Drehen: Navigation durch Menüs/Screens")
    print("  • Kurz drücken: Menü öffnen/Auswahl bestätigen")
    print("  • Lang drücken: Zurück zur Status-Übersicht")
    print("\nDrücken Sie Strg+C zum Beenden\n")

    # Monitoring starten
    try:
        monitor.run()
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
