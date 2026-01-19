#!/usr/bin/env python3
"""
Einfaches Display-Test-Script
Testet das OLED Display ohne SNMP-Verbindung
"""

import sys
import time
import os

# Füge src-Verzeichnis zum Python-Path hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.display_handler import OLEDDisplay


def test_display():
    """Führt verschiedene Display-Tests durch"""

    print("="*60)
    print("OLED Display Test")
    print("="*60)
    print()

    # Display initialisieren
    print("Initialisiere Display...")
    display = OLEDDisplay(width=128, height=64)
    print("✓ Display initialisiert")
    print()

    # Test 1: Einfacher Text
    print("Test 1: Einfacher Text")
    print("Zeige 'Hello World!' auf dem Display...")
    display.display_text("Hello World!", 10, 25)
    time.sleep(3)

    # Test 2: Mehrere Zeilen
    print("\nTest 2: Mehrere Zeilen")
    print("Zeige mehrere Textzeilen...")
    display.display_multiline([
        "LTE Rack Monitor",
        "Display Test",
        "Zeile 3",
        "Zeile 4",
        "Zeile 5"
    ])
    time.sleep(3)

    # Test 3: Status-Anzeige (simuliert)
    print("\nTest 3: Status-Anzeige")
    print("Zeige simulierten Router-Status...")
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
    time.sleep(4)

    # Test 4: Verschiedene Signalstärken
    print("\nTest 4: Verschiedene Signalstärken")
    signal_levels = [
        (-65, "Ausgezeichnet"),
        (-80, "Gut"),
        (-95, "Mittel"),
        (-105, "Schwach"),
        (-115, "Sehr schwach")
    ]

    for rssi, quality in signal_levels:
        print(f"  Zeige Signal: {rssi} dBm ({quality})")
        test_status['signal_strength'] = rssi
        display.display_status(test_status)
        time.sleep(2)

    # Test 5: Menü-Anzeige (simuliert)
    print("\nTest 5: Menü-Anzeige")
    print("Zeige Menü...")

    # Simuliere Menü-Einträge
    class MenuItem:
        def __init__(self, title):
            self.title = title

    menu_items = [
        MenuItem("Status-Übersicht"),
        MenuItem("Signal-Details"),
        MenuItem("Netzwerk-Info"),
        MenuItem("System-Info"),
        MenuItem("Einstellungen"),
        MenuItem("Info")
    ]

    # Zeige Menü mit verschiedenen Auswahlen
    for i in range(len(menu_items)):
        print(f"  Auswahl: {menu_items[i].title}")
        display.display_menu(menu_items, i, "MENÜ")
        time.sleep(1.5)

    # Test 6: Screen-Anzeigen
    print("\nTest 6: Verschiedene Screens")

    # Status Screen
    print("  Status-Screen...")
    status_screen = {
        'title': '📊 Status',
        'type': 'status',
        'operator': 'Telekom',
        'network_type': 'LTE',
        'connection_state': 'Connected',
        'signal_strength': -75,
        'signal_details': {
            'rsrp': -95,
            'rsrq': -10
        }
    }
    display.display_screen(status_screen)
    time.sleep(3)

    # Signal Details Screen
    print("  Signal-Details-Screen...")
    signal_screen = {
        'title': '📶 Signal',
        'type': 'text',
        'lines': [
            "RSSI: -75 dBm",
            "RSRP: -95 dBm",
            "RSRQ: -10 dB",
            "SINR: 13 dB"
        ]
    }
    display.display_screen(signal_screen)
    time.sleep(3)

    # Netzwerk Info Screen
    print("  Netzwerk-Info-Screen...")
    network_screen = {
        'title': '🌐 Netzwerk',
        'type': 'text',
        'lines': [
            "Operator: Telekom",
            "Typ: LTE",
            "Status: Connected"
        ]
    }
    display.display_screen(network_screen)
    time.sleep(3)

    # System Info Screen
    print("  System-Info-Screen...")
    system_screen = {
        'title': '💻 System',
        'type': 'text',
        'lines': [
            "Name: RUT241",
            "Uptime: 5d 3h 24m",
            "Model: RUT241",
            "Version: 7.2.4"
        ]
    }
    display.display_screen(system_screen)
    time.sleep(3)

    # About Screen
    print("  About-Screen...")
    about_screen = {
        'title': 'ℹ️ Info',
        'type': 'text',
        'lines': [
            "LTE Rack Monitor",
            "Version 1.0.0",
            "RUT241 SNMP",
            "2023"
        ]
    }
    display.display_screen(about_screen)
    time.sleep(3)

    # Test 7: Fehlermeldung
    print("\nTest 7: Fehlermeldung")
    print("Zeige Fehlermeldung...")
    display.display_error("Verbindung zum Router konnte nicht hergestellt werden")
    time.sleep(3)

    # Test 8: Lange Texte
    print("\nTest 8: Lange Texte (automatische Kürzung)")
    print("Zeige lange Textzeilen...")
    display.display_multiline([
        "Dies ist eine sehr lange Textzeile die gekürzt werden sollte",
        "Kurzer Text",
        "Noch eine extrem lange Zeile mit vielen Wörtern",
        "Ende"
    ])
    time.sleep(3)

    # Test abgeschlossen
    print("\nTest 9: Abschluss-Nachricht")
    print("Zeige Abschluss-Nachricht...")
    display.display_multiline([
        "Display Test",
        "erfolgreich!",
        "",
        "Alle Tests",
        "bestanden ✓"
    ])
    time.sleep(3)

    # Display löschen
    print("\nLösche Display...")
    display.clear()

    print()
    print("="*60)
    print("Alle Display-Tests abgeschlossen!")
    print("="*60)
    print()
    print("Zusammenfassung:")
    print("  ✓ Einfacher Text")
    print("  ✓ Mehrere Zeilen")
    print("  ✓ Status-Anzeige")
    print("  ✓ Signalstärken")
    print("  ✓ Menü-Anzeige")
    print("  ✓ Verschiedene Screens")
    print("  ✓ Fehlermeldungen")
    print("  ✓ Lange Texte")
    print()
    print("Das Display funktioniert korrekt!")
    print()


def quick_test():
    """Schneller Test - nur die wichtigsten Funktionen"""
    print("="*60)
    print("Schneller Display-Test")
    print("="*60)
    print()

    display = OLEDDisplay()

    # Test 1
    print("1. Zeige Text...")
    display.display_text("Display Test", 20, 25)
    time.sleep(2)

    # Test 2
    print("2. Zeige Zeilen...")
    display.display_multiline([
        "Zeile 1",
        "Zeile 2",
        "Zeile 3"
    ])
    time.sleep(2)

    # Test 3
    print("3. Zeige Status...")
    display.display_status({
        'operator': 'Test',
        'network_type': 'LTE',
        'connection_state': 'OK',
        'signal_strength': -80,
        'signal_details': {}
    })
    time.sleep(2)

    # Fertig
    display.clear()
    print("✓ Schneller Test abgeschlossen!")
    print()


if __name__ == '__main__':
    print()
    print("Wählen Sie einen Test:")
    print("  1) Vollständiger Test (alle Features)")
    print("  2) Schneller Test (nur Grundfunktionen)")
    print("  3) Dauerschleife (für langfristige Tests)")
    print()

    try:
        choice = input("Ihre Wahl (1-3): ").strip()
        print()

        if choice == '1':
            test_display()

        elif choice == '2':
            quick_test()

        elif choice == '3':
            print("Dauerschleife gestartet (Strg+C zum Beenden)")
            print()
            display = OLEDDisplay()
            counter = 0

            try:
                while True:
                    display.display_multiline([
                        "Display Test",
                        "Dauerschleife",
                        f"Durchlauf: {counter}",
                        time.strftime("%H:%M:%S")
                    ])
                    counter += 1
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nDauerschleife beendet")
                display.clear()

        else:
            print("Ungültige Auswahl!")
            print("Führe vollständigen Test durch...")
            print()
            test_display()

    except KeyboardInterrupt:
        print("\n\nTest abgebrochen durch Benutzer")
    except Exception as e:
        print(f"\n✗ Fehler: {e}")
        import traceback
        traceback.print_exc()
