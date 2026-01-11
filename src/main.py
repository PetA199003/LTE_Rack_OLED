#!/usr/bin/env python3
"""
LTE Rack OLED Display - Hauptanwendung
Überwacht Teltonika RUT241 Router und zeigt Status auf OLED Display an
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


# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LTERackMonitor:
    """
    Hauptanwendung für LTE Rack OLED Monitor

    Überwacht kontinuierlich den RUT241 Router und zeigt Status an
    """

    def __init__(
        self,
        host: str,
        community: str = 'public',
        update_interval: int = 5,
        display_width: int = 128,
        display_height: int = 64
    ):
        """
        Initialisiert den Monitor

        Args:
            host: IP-Adresse des RUT241
            community: SNMP Community String
            update_interval: Update-Intervall in Sekunden
            display_width: Display-Breite in Pixel
            display_height: Display-Höhe in Pixel
        """
        self.host = host
        self.community = community
        self.update_interval = update_interval
        self.running = False

        logger.info(f"Initialisiere LTE Rack Monitor für {host}")

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

        # Signal Handler für sauberes Beenden
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handler für Beendigungs-Signale"""
        logger.info(f"Signal {signum} empfangen - beende Anwendung...")
        self.running = False

    def run(self):
        """Startet die Haupt-Monitoring-Schleife"""
        logger.info("Starte Monitoring...")
        self.running = True

        # Startmeldung auf Display
        self.display.display_multiline([
            "LTE Rack Monitor",
            "Starte...",
            f"Host: {self.host}",
            f"Interval: {self.update_interval}s"
        ])
        time.sleep(2)

        error_count = 0
        max_errors = 5

        while self.running:
            try:
                # Status vom Router abrufen
                logger.debug("Rufe Status ab...")
                status = self.snmp_client.get_all_status()

                # Auf Display anzeigen
                self.display.display_status(status)

                # Fehler-Counter zurücksetzen bei Erfolg
                error_count = 0

                # Warten bis zum nächsten Update
                time.sleep(self.update_interval)

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

            if status.get('operator') or status.get('system_info', {}).get('name'):
                logger.info("✓ Verbindung erfolgreich")
                return True
            else:
                logger.warning("⚠ Verbindung hergestellt, aber keine Daten empfangen")
                return False

        except Exception as e:
            logger.error(f"✗ Verbindungstest fehlgeschlagen: {e}")
            return False


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

    return config


def main():
    """Hauptfunktion"""
    print("="*60)
    print("LTE Rack OLED Monitor")
    print("Teltonika RUT241 SNMP Monitor mit OLED Display")
    print("="*60)

    # Konfiguration laden
    config = load_config()

    print(f"\nKonfiguration:")
    print(f"  Host: {config['host']}")
    print(f"  Community: {config['community']}")
    print(f"  Update-Intervall: {config['update_interval']}s")
    print(f"  Display: {config['display_width']}x{config['display_height']}")
    print()

    # Monitor initialisieren
    monitor = LTERackMonitor(
        host=config['host'],
        community=config['community'],
        update_interval=config['update_interval'],
        display_width=config['display_width'],
        display_height=config['display_height']
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
    print("\nStarte Monitoring...")
    print("Drücken Sie Strg+C zum Beenden\n")

    # Monitoring starten
    try:
        monitor.run()
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
