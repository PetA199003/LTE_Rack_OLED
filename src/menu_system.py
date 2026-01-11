"""
Menü-System für LTE Rack OLED Monitor
Navigierbar mit KY040 Rotary Encoder
"""

import logging
from typing import Optional, Dict, Any, List, Callable
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MenuScreen(Enum):
    """Verfügbare Menü-Bildschirme"""
    STATUS_OVERVIEW = "status_overview"      # Haupt-Status-Übersicht
    SIGNAL_DETAILS = "signal_details"        # Detaillierte Signal-Informationen
    NETWORK_INFO = "network_info"            # Netzwerk-Informationen
    SYSTEM_INFO = "system_info"              # System-Informationen
    SETTINGS = "settings"                    # Einstellungen
    ABOUT = "about"                          # Info über die Anwendung


class MenuItem:
    """Ein Menü-Eintrag"""

    def __init__(
        self,
        screen: MenuScreen,
        title: str,
        icon: str = "•",
        show_in_menu: bool = True
    ):
        """
        Args:
            screen: Zugehöriger MenuScreen
            title: Anzeigetitel
            icon: Icon/Symbol (für Anzeige)
            show_in_menu: Soll im Menü angezeigt werden?
        """
        self.screen = screen
        self.title = title
        self.icon = icon
        self.show_in_menu = show_in_menu


class MenuSystem:
    """
    Menü-System mit Rotary Encoder Navigation

    Unterstützt:
    - Navigation zwischen verschiedenen Ansichten
    - Auswahl mit Knopfdruck
    - Zurück-Navigation mit langem Knopfdruck
    """

    def __init__(self):
        """Initialisiert das Menü-System"""
        self.current_screen = MenuScreen.STATUS_OVERVIEW
        self.in_menu_mode = False
        self.menu_selection = 0

        # Menü-Einträge definieren
        self.menu_items = [
            MenuItem(MenuScreen.STATUS_OVERVIEW, "Status-Übersicht", "📊"),
            MenuItem(MenuScreen.SIGNAL_DETAILS, "Signal-Details", "📶"),
            MenuItem(MenuScreen.NETWORK_INFO, "Netzwerk-Info", "🌐"),
            MenuItem(MenuScreen.SYSTEM_INFO, "System-Info", "💻"),
            MenuItem(MenuScreen.SETTINGS, "Einstellungen", "⚙️"),
            MenuItem(MenuScreen.ABOUT, "Info", "ℹ️"),
        ]

        # Einstellungen
        self.settings = {
            'update_interval': 5,
            'brightness': 100,
            'auto_rotate_screens': False,
            'auto_rotate_interval': 10,
        }

        # Callbacks
        self._screen_change_callback: Optional[Callable[[MenuScreen], None]] = None
        self._settings_change_callback: Optional[Callable[[str, Any], None]] = None

        logger.info("Menü-System initialisiert")

    def handle_rotation(self, direction: int):
        """
        Behandelt Rotary Encoder Drehung

        Args:
            direction: 1 für rechts, -1 für links
        """
        if self.in_menu_mode:
            # Im Menü: Navigation zwischen Einträgen
            self.menu_selection = (self.menu_selection + direction) % len(self.menu_items)
            logger.debug(f"Menü-Auswahl: {self.menu_selection} - {self.menu_items[self.menu_selection].title}")
        else:
            # Nicht im Menü: Navigation zwischen Screens
            screens = [item.screen for item in self.menu_items]
            current_index = screens.index(self.current_screen)
            new_index = (current_index + direction) % len(screens)
            self.current_screen = screens[new_index]
            logger.debug(f"Screen gewechselt: {self.current_screen.value}")

            # Callback aufrufen
            if self._screen_change_callback:
                self._screen_change_callback(self.current_screen)

    def handle_press(self):
        """Behandelt Rotary Encoder Knopfdruck (kurz)"""
        if self.in_menu_mode:
            # Im Menü: Auswahl bestätigen
            selected_item = self.menu_items[self.menu_selection]
            self.current_screen = selected_item.screen
            self.in_menu_mode = False
            logger.info(f"Screen gewählt: {self.current_screen.value}")

            # Callback aufrufen
            if self._screen_change_callback:
                self._screen_change_callback(self.current_screen)
        else:
            # Nicht im Menü: Menü öffnen
            self.in_menu_mode = True
            # Aktuellen Screen im Menü vorauswählen
            screens = [item.screen for item in self.menu_items]
            if self.current_screen in screens:
                self.menu_selection = screens.index(self.current_screen)
            logger.info("Menü geöffnet")

    def handle_long_press(self):
        """Behandelt langen Knopfdruck"""
        if self.in_menu_mode:
            # Im Menü: Zurück zur Status-Übersicht
            self.in_menu_mode = False
            self.current_screen = MenuScreen.STATUS_OVERVIEW
            logger.info("Zurück zur Status-Übersicht")

            # Callback aufrufen
            if self._screen_change_callback:
                self._screen_change_callback(self.current_screen)
        else:
            # Nicht im Menü: Direkt zur Status-Übersicht
            self.current_screen = MenuScreen.STATUS_OVERVIEW
            logger.info("Zurück zur Status-Übersicht")

            # Callback aufrufen
            if self._screen_change_callback:
                self._screen_change_callback(self.current_screen)

    def get_current_screen(self) -> MenuScreen:
        """
        Gibt den aktuellen Screen zurück

        Returns:
            Aktueller MenuScreen
        """
        return self.current_screen

    def is_in_menu(self) -> bool:
        """
        Prüft ob im Menü-Modus

        Returns:
            True wenn im Menü, sonst False
        """
        return self.in_menu_mode

    def get_menu_items(self) -> List[MenuItem]:
        """
        Gibt alle Menü-Einträge zurück

        Returns:
            Liste mit MenuItem Objekten
        """
        return self.menu_items

    def get_selected_menu_item(self) -> MenuItem:
        """
        Gibt den aktuell ausgewählten Menü-Eintrag zurück

        Returns:
            Ausgewählter MenuItem
        """
        return self.menu_items[self.menu_selection]

    def get_menu_selection_index(self) -> int:
        """
        Gibt den Index der Menü-Auswahl zurück

        Returns:
            Index (0-basiert)
        """
        return self.menu_selection

    def format_screen_data(self, screen: MenuScreen, status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formatiert Daten für einen bestimmten Screen

        Args:
            screen: MenuScreen für den die Daten formatiert werden sollen
            status: Status-Daten vom SNMP Client

        Returns:
            Dictionary mit formatierten Daten für Display
        """
        if screen == MenuScreen.STATUS_OVERVIEW:
            return self._format_status_overview(status)
        elif screen == MenuScreen.SIGNAL_DETAILS:
            return self._format_signal_details(status)
        elif screen == MenuScreen.NETWORK_INFO:
            return self._format_network_info(status)
        elif screen == MenuScreen.SYSTEM_INFO:
            return self._format_system_info(status)
        elif screen == MenuScreen.SETTINGS:
            return self._format_settings()
        elif screen == MenuScreen.ABOUT:
            return self._format_about()
        else:
            return {'title': 'Unbekannt', 'lines': ['N/A']}

    def _format_status_overview(self, status: Dict[str, Any]) -> Dict[str, Any]:
        """Formatiert Status-Übersicht"""
        return {
            'title': '📊 Status',
            'type': 'status',
            'operator': status.get('operator', 'N/A'),
            'network_type': status.get('network_type', 'N/A'),
            'connection_state': status.get('connection_state', 'N/A'),
            'signal_strength': status.get('signal_strength'),
            'signal_details': status.get('signal_details', {}),
        }

    def _format_signal_details(self, status: Dict[str, Any]) -> Dict[str, Any]:
        """Formatiert Signal-Details"""
        details = status.get('signal_details', {})
        return {
            'title': '📶 Signal',
            'type': 'text',
            'lines': [
                f"RSSI: {details.get('rssi', 'N/A')} dBm",
                f"RSRP: {details.get('rsrp', 'N/A')} dBm",
                f"RSRQ: {details.get('rsrq', 'N/A')} dB",
                f"SINR: {details.get('sinr', 'N/A')} dB",
            ]
        }

    def _format_network_info(self, status: Dict[str, Any]) -> Dict[str, Any]:
        """Formatiert Netzwerk-Informationen"""
        return {
            'title': '🌐 Netzwerk',
            'type': 'text',
            'lines': [
                f"Operator: {status.get('operator', 'N/A')}",
                f"Typ: {status.get('network_type', 'N/A')}",
                f"Status: {status.get('connection_state', 'N/A')}",
            ]
        }

    def _format_system_info(self, status: Dict[str, Any]) -> Dict[str, Any]:
        """Formatiert System-Informationen"""
        sys_info = status.get('system_info', {})
        return {
            'title': '💻 System',
            'type': 'text',
            'lines': [
                f"Name: {sys_info.get('name', 'N/A')}",
                f"Uptime: {sys_info.get('uptime', 'N/A')}",
                f"Beschreibung:",
                f"{(sys_info.get('description', 'N/A'))[:40]}...",
            ]
        }

    def _format_settings(self) -> Dict[str, Any]:
        """Formatiert Einstellungen"""
        return {
            'title': '⚙️ Einstellungen',
            'type': 'text',
            'lines': [
                f"Update: {self.settings['update_interval']}s",
                f"Helligkeit: {self.settings['brightness']}%",
                f"Auto-Rotate: {'AN' if self.settings['auto_rotate_screens'] else 'AUS'}",
            ]
        }

    def _format_about(self) -> Dict[str, Any]:
        """Formatiert Info-Screen"""
        return {
            'title': 'ℹ️ Info',
            'type': 'text',
            'lines': [
                "LTE Rack Monitor",
                "v1.0.0",
                "RUT241 SNMP",
                "KY040 Navigation",
            ]
        }

    def on_screen_change(self, callback: Callable[[MenuScreen], None]):
        """
        Registriert Callback für Screen-Wechsel

        Args:
            callback: Funktion die bei Screen-Wechsel aufgerufen wird
        """
        self._screen_change_callback = callback

    def on_settings_change(self, callback: Callable[[str, Any], None]):
        """
        Registriert Callback für Einstellungs-Änderung

        Args:
            callback: Funktion die bei Einstellungs-Änderung aufgerufen wird
        """
        self._settings_change_callback = callback

    def get_setting(self, key: str) -> Any:
        """
        Gibt eine Einstellung zurück

        Args:
            key: Einstellungs-Schlüssel

        Returns:
            Wert der Einstellung oder None
        """
        return self.settings.get(key)

    def set_setting(self, key: str, value: Any):
        """
        Setzt eine Einstellung

        Args:
            key: Einstellungs-Schlüssel
            value: Neuer Wert
        """
        if key in self.settings:
            self.settings[key] = value
            logger.info(f"Einstellung geändert: {key} = {value}")

            # Callback aufrufen
            if self._settings_change_callback:
                self._settings_change_callback(key, value)


def main():
    """Test-Funktion"""
    print("="*60)
    print("Menü-System Test")
    print("="*60)
    print()

    menu = MenuSystem()

    # Callback registrieren
    def on_screen_change(screen: MenuScreen):
        print(f"→ Screen gewechselt: {screen.value}")

    menu.on_screen_change(on_screen_change)

    # Simuliere Navigation
    print("Teste Navigation...")
    print()

    # Test 1: Durch Screens navigieren
    print("1. Durch Screens navigieren (nicht im Menü):")
    for i in range(3):
        menu.handle_rotation(1)
        print(f"   Aktueller Screen: {menu.get_current_screen().value}")

    print()

    # Test 2: Menü öffnen
    print("2. Menü öffnen:")
    menu.handle_press()
    print(f"   Im Menü: {menu.is_in_menu()}")
    print(f"   Auswahl: {menu.get_selected_menu_item().title}")

    print()

    # Test 3: Im Menü navigieren
    print("3. Im Menü navigieren:")
    for i in range(3):
        menu.handle_rotation(1)
        print(f"   Auswahl: {menu.get_selected_menu_item().title}")

    print()

    # Test 4: Auswahl bestätigen
    print("4. Auswahl bestätigen:")
    menu.handle_press()
    print(f"   Im Menü: {menu.is_in_menu()}")
    print(f"   Aktueller Screen: {menu.get_current_screen().value}")

    print()

    # Test 5: Langer Tastendruck (zurück)
    print("5. Langer Tastendruck (zurück zur Status-Übersicht):")
    menu.handle_long_press()
    print(f"   Aktueller Screen: {menu.get_current_screen().value}")

    print()

    # Test 6: Daten formatieren
    print("6. Daten formatieren:")
    test_status = {
        'operator': 'Telekom',
        'network_type': 'LTE',
        'connection_state': 'Connected',
        'signal_strength': -75,
        'signal_details': {
            'rssi': -75,
            'rsrp': -95,
            'rsrq': -10,
            'sinr': 13
        }
    }

    formatted = menu.format_screen_data(MenuScreen.STATUS_OVERVIEW, test_status)
    print(f"   Formatierte Daten: {formatted}")

    print()
    print("Test abgeschlossen!")


if __name__ == '__main__':
    main()
