"""
SNMP Client für Teltonika RUT241 Router
Liest diverse Status-Informationen über SNMP aus
"""

import logging
from typing import Optional, Dict, Any
from pysnmp.hlapi import (
    getCmd,
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
)


# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RUT241SNMPClient:
    """
    SNMP Client für Teltonika RUT241 Router

    Wichtige OIDs für RUT241:
    - Signalstärke (RSSI): 1.3.6.1.4.1.48690.2.1.1.2.1.0
    - Netzwerktyp: 1.3.6.1.4.1.48690.2.1.1.3.1.0
    - Operator: 1.3.6.1.4.1.48690.2.1.1.4.1.0
    - Verbindungsstatus: 1.3.6.1.4.1.48690.2.1.1.5.1.0
    - System Beschreibung: 1.3.6.1.2.1.1.1.0
    - System Uptime: 1.3.6.1.2.1.1.3.0
    """

    # Teltonika RUT241 spezifische OIDs
    OIDS = {
        'signal_strength': '1.3.6.1.4.1.48690.2.1.1.2.1.0',
        'network_type': '1.3.6.1.4.1.48690.2.1.1.3.1.0',
        'operator': '1.3.6.1.4.1.48690.2.1.1.4.1.0',
        'connection_state': '1.3.6.1.4.1.48690.2.1.1.5.1.0',
        'system_description': '1.3.6.1.2.1.1.1.0',
        'system_uptime': '1.3.6.1.2.1.1.3.0',
        'system_name': '1.3.6.1.2.1.1.5.0',
        'wan_ip': '1.3.6.1.4.1.48690.2.3.1.0',
        'mobile_signal_rssi': '1.3.6.1.4.1.48690.2.1.1.2.1.0',
        'mobile_signal_rsrp': '1.3.6.1.4.1.48690.2.1.1.2.2.0',
        'mobile_signal_rsrq': '1.3.6.1.4.1.48690.2.1.1.2.3.0',
        'mobile_signal_sinr': '1.3.6.1.4.1.48690.2.1.1.2.4.0',
    }

    def __init__(
        self,
        host: str,
        community: str = 'public',
        port: int = 161,
        timeout: int = 2,
        retries: int = 3
    ):
        """
        Initialisiert den SNMP Client

        Args:
            host: IP-Adresse oder Hostname des RUT241
            community: SNMP Community String (Standard: 'public')
            port: SNMP Port (Standard: 161)
            timeout: Timeout in Sekunden
            retries: Anzahl der Wiederholungsversuche
        """
        self.host = host
        self.community = community
        self.port = port
        self.timeout = timeout
        self.retries = retries

        logger.info(f"SNMP Client initialisiert für {host}:{port}")

    def get_oid(self, oid: str) -> Optional[str]:
        """
        Führt SNMP GET für eine einzelne OID aus

        Args:
            oid: Die abzufragende OID

        Returns:
            Der Wert als String oder None bei Fehler
        """
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.host, self.port), timeout=self.timeout, retries=self.retries),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )

            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

            if errorIndication:
                logger.error(f"SNMP Fehler: {errorIndication}")
                return None
            elif errorStatus:
                logger.error(f"SNMP Fehler: {errorStatus.prettyPrint()}")
                return None
            else:
                for varBind in varBinds:
                    value = varBind[1].prettyPrint()
                    logger.debug(f"OID {oid} = {value}")
                    return value

        except Exception as e:
            logger.error(f"Fehler beim Abrufen von OID {oid}: {e}")
            return None

    def get_signal_strength(self) -> Optional[int]:
        """Liest die Signalstärke (RSSI) aus"""
        value = self.get_oid(self.OIDS['mobile_signal_rssi'])
        if value and value.lstrip('-').isdigit():
            return int(value)
        return None

    def get_network_type(self) -> Optional[str]:
        """Liest den Netzwerktyp aus (z.B. LTE, 3G, 4G)"""
        return self.get_oid(self.OIDS['network_type'])

    def get_operator(self) -> Optional[str]:
        """Liest den Mobilfunk-Operator aus"""
        return self.get_oid(self.OIDS['operator'])

    def get_connection_state(self) -> Optional[str]:
        """Liest den Verbindungsstatus aus"""
        return self.get_oid(self.OIDS['connection_state'])

    def get_system_info(self) -> Dict[str, Optional[str]]:
        """Liest allgemeine System-Informationen aus"""
        return {
            'description': self.get_oid(self.OIDS['system_description']),
            'uptime': self.get_oid(self.OIDS['system_uptime']),
            'name': self.get_oid(self.OIDS['system_name']),
        }

    def get_signal_details(self) -> Dict[str, Optional[int]]:
        """
        Liest detaillierte LTE Signalwerte aus

        Returns:
            Dictionary mit RSSI, RSRP, RSRQ, SINR Werten
        """
        result = {}

        for key in ['mobile_signal_rssi', 'mobile_signal_rsrp', 'mobile_signal_rsrq', 'mobile_signal_sinr']:
            value = self.get_oid(self.OIDS[key])
            if value and value.lstrip('-').isdigit():
                result[key.replace('mobile_signal_', '')] = int(value)
            else:
                result[key.replace('mobile_signal_', '')] = None

        return result

    def get_all_status(self) -> Dict[str, Any]:
        """
        Liest alle wichtigen Status-Informationen auf einmal aus

        Returns:
            Dictionary mit allen Status-Informationen
        """
        logger.info("Lese alle Status-Informationen aus...")

        status = {
            'signal_strength': self.get_signal_strength(),
            'network_type': self.get_network_type(),
            'operator': self.get_operator(),
            'connection_state': self.get_connection_state(),
            'signal_details': self.get_signal_details(),
            'system_info': self.get_system_info(),
        }

        logger.info(f"Status erfolgreich ausgelesen: {status}")
        return status

    def format_signal_strength(self, rssi: Optional[int]) -> str:
        """
        Formatiert die Signalstärke mit visueller Darstellung

        Args:
            rssi: RSSI-Wert in dBm

        Returns:
            Formatierter String mit Balken-Darstellung
        """
        if rssi is None:
            return "N/A"

        # RSSI Bewertung (typische Werte für LTE)
        if rssi >= -70:
            quality = "Ausgezeichnet"
            bars = "████"
        elif rssi >= -85:
            quality = "Gut"
            bars = "███░"
        elif rssi >= -100:
            quality = "Mittel"
            bars = "██░░"
        elif rssi >= -110:
            quality = "Schwach"
            bars = "█░░░"
        else:
            quality = "Sehr schwach"
            bars = "░░░░"

        return f"{rssi} dBm [{bars}] {quality}"


def main():
    """Test-Funktion"""
    import sys

    # Beispiel-Verwendung
    host = input("RUT241 IP-Adresse (z.B. 192.168.1.1): ").strip() or "192.168.1.1"
    community = input("SNMP Community (Standard: public): ").strip() or "public"

    print(f"\nVerbinde mit {host}...")
    client = RUT241SNMPClient(host=host, community=community)

    print("\n" + "="*60)
    print("Lese Status-Informationen aus...")
    print("="*60)

    status = client.get_all_status()

    print("\n📡 Mobilfunk-Verbindung:")
    print(f"  Operator: {status['operator']}")
    print(f"  Netzwerktyp: {status['network_type']}")
    print(f"  Status: {status['connection_state']}")

    print("\n📶 Signalstärke:")
    rssi = status['signal_strength']
    print(f"  {client.format_signal_strength(rssi)}")

    details = status['signal_details']
    if details.get('rsrp'):
        print(f"  RSRP: {details['rsrp']} dBm")
    if details.get('rsrq'):
        print(f"  RSRQ: {details['rsrq']} dB")
    if details.get('sinr'):
        print(f"  SINR: {details['sinr']} dB")

    print("\n💻 System-Info:")
    sys_info = status['system_info']
    if sys_info['name']:
        print(f"  Name: {sys_info['name']}")
    if sys_info['uptime']:
        print(f"  Uptime: {sys_info['uptime']}")
    if sys_info['description']:
        print(f"  Beschreibung: {sys_info['description'][:80]}...")

    print("\n" + "="*60)


if __name__ == '__main__':
    main()
