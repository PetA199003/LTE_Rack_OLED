#!/usr/bin/env python3
"""
Einfaches Test-Script für SNMP-Verbindung zum RUT241
Kann ohne Display-Hardware verwendet werden
"""

import sys
import os

# Füge src-Verzeichnis zum Python-Path hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.snmp_client import RUT241SNMPClient


def print_banner():
    """Gibt Banner aus"""
    print("="*70)
    print(" Teltonika RUT241 SNMP Test")
    print(" Testet SNMP-Verbindung ohne Display")
    print("="*70)
    print()


def test_basic_oids(client: RUT241SNMPClient):
    """Testet grundlegende OIDs"""
    print("📋 Teste grundlegende System-OIDs...")
    print("-"*70)

    tests = [
        ('System Name', client.OIDS['system_name']),
        ('System Description', client.OIDS['system_description']),
        ('System Uptime', client.OIDS['system_uptime']),
    ]

    for name, oid in tests:
        value = client.get_oid(oid)
        status = "✓" if value else "✗"
        print(f"{status} {name:25} : {value or 'N/A'}")

    print()


def test_mobile_info(client: RUT241SNMPClient):
    """Testet Mobilfunk-spezifische OIDs"""
    print("📡 Teste Mobilfunk-OIDs...")
    print("-"*70)

    # Operator
    operator = client.get_operator()
    print(f"  Operator: {operator or 'N/A'}")

    # Netzwerktyp
    network = client.get_network_type()
    print(f"  Netzwerk: {network or 'N/A'}")

    # Verbindungsstatus
    state = client.get_connection_state()
    print(f"  Status: {state or 'N/A'}")

    print()


def test_signal_strength(client: RUT241SNMPClient):
    """Testet Signalstärke-Messungen"""
    print("📶 Teste Signal-Messungen...")
    print("-"*70)

    details = client.get_signal_details()

    measurements = [
        ('RSSI', details.get('rssi')),
        ('RSRP', details.get('rsrp')),
        ('RSRQ', details.get('rsrq')),
        ('SINR', details.get('sinr')),
    ]

    for name, value in measurements:
        if value is not None:
            formatted = client.format_signal_strength(value) if name == 'RSSI' else f"{value} {'dBm' if name in ['RSRP'] else 'dB'}"
            print(f"  {name}: {formatted}")
        else:
            print(f"  {name}: N/A")

    print()


def test_all_oids(client: RUT241SNMPClient):
    """Testet alle definierten OIDs"""
    print("🔍 Teste alle definierten OIDs...")
    print("-"*70)

    success = 0
    failed = 0

    for name, oid in client.OIDS.items():
        value = client.get_oid(oid)
        if value:
            success += 1
            print(f"✓ {name:30} : {value[:50] if len(str(value)) > 50 else value}")
        else:
            failed += 1
            print(f"✗ {name:30} : N/A")

    print()
    print(f"Ergebnis: {success} erfolgreich, {failed} fehlgeschlagen")
    print()


def interactive_mode(client: RUT241SNMPClient):
    """Interaktiver Modus zum Testen eigener OIDs"""
    print("🔧 Interaktiver Modus")
    print("-"*70)
    print("Geben Sie eine OID ein zum Testen (oder 'q' zum Beenden)")
    print("Beispiel: 1.3.6.1.2.1.1.1.0")
    print()

    while True:
        try:
            oid = input("OID> ").strip()

            if oid.lower() in ['q', 'quit', 'exit']:
                break

            if not oid:
                continue

            value = client.get_oid(oid)
            if value:
                print(f"✓ Wert: {value}")
            else:
                print(f"✗ Keine Antwort oder Fehler")
            print()

        except KeyboardInterrupt:
            print("\nBeendet.")
            break
        except Exception as e:
            print(f"✗ Fehler: {e}")


def main():
    """Hauptfunktion"""
    print_banner()

    # Konfiguration
    host = os.getenv('SNMP_HOST', '192.168.1.1')
    community = os.getenv('SNMP_COMMUNITY', 'public')

    # Kommandozeilenargumente
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        community = sys.argv[2]

    print(f"Verbinde mit: {host}")
    print(f"Community: {community}")
    print()

    # Client erstellen
    client = RUT241SNMPClient(host=host, community=community, timeout=3)

    # Menü
    while True:
        print("Wählen Sie einen Test:")
        print("  1) Basis System-Informationen")
        print("  2) Mobilfunk-Informationen")
        print("  3) Signal-Messungen")
        print("  4) Alle OIDs testen")
        print("  5) Vollständiger Status (wie in Hauptanwendung)")
        print("  6) Interaktiver Modus (eigene OIDs testen)")
        print("  0) Beenden")
        print()

        try:
            choice = input("Auswahl> ").strip()

            if choice == '0':
                print("Auf Wiedersehen!")
                break
            elif choice == '1':
                test_basic_oids(client)
            elif choice == '2':
                test_mobile_info(client)
            elif choice == '3':
                test_signal_strength(client)
            elif choice == '4':
                test_all_oids(client)
            elif choice == '5':
                print("📊 Vollständiger Status...")
                print("-"*70)
                status = client.get_all_status()
                for key, value in status.items():
                    print(f"{key}: {value}")
                print()
            elif choice == '6':
                interactive_mode(client)
            else:
                print("Ungültige Auswahl!\n")

        except KeyboardInterrupt:
            print("\n\nAuf Wiedersehen!")
            break
        except Exception as e:
            print(f"✗ Fehler: {e}\n")


if __name__ == '__main__':
    main()
