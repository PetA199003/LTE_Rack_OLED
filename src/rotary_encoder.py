"""
KY040 Rotary Encoder Treiber für Raspberry Pi
Unterstützt Drehung (CLK/DT) und Knopfdruck (SW)
"""

import logging
from typing import Callable, Optional
import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO nicht verfügbar - Rotary Encoder im Dummy-Modus")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KY040RotaryEncoder:
    """
    Treiber für KY040 Rotary Encoder

    Hardware-Anschluss:
    - CLK -> GPIO (z.B. GPIO 17)
    - DT  -> GPIO (z.B. GPIO 27)
    - SW  -> GPIO (z.B. GPIO 22)
    - +   -> 3.3V
    - GND -> GND

    Verwendung:
        encoder = KY040RotaryEncoder(clk_pin=17, dt_pin=27, sw_pin=22)
        encoder.on_rotate(lambda direction: print(f"Gedreht: {direction}"))
        encoder.on_press(lambda: print("Gedrückt"))
        encoder.start()
    """

    CLOCKWISE = 1
    COUNTER_CLOCKWISE = -1

    def __init__(
        self,
        clk_pin: int = 17,
        dt_pin: int = 27,
        sw_pin: int = 22,
        debounce_time: int = 5,  # ms
        long_press_time: float = 1.0  # Sekunden
    ):
        """
        Initialisiert den Rotary Encoder

        Args:
            clk_pin: GPIO Pin für CLK (Clock)
            dt_pin: GPIO Pin für DT (Data)
            sw_pin: GPIO Pin für SW (Switch/Button)
            debounce_time: Entprellzeit in Millisekunden
            long_press_time: Zeit für langen Tastendruck in Sekunden
        """
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.sw_pin = sw_pin
        self.debounce_time = debounce_time
        self.long_press_time = long_press_time

        self.clk_last_state = None
        self.button_press_time = None

        # Callback-Funktionen
        self._rotate_callback: Optional[Callable[[int], None]] = None
        self._press_callback: Optional[Callable[[], None]] = None
        self._long_press_callback: Optional[Callable[[], None]] = None
        self._release_callback: Optional[Callable[[], None]] = None

        self.running = False
        self._dummy_mode = not GPIO_AVAILABLE

        if not self._dummy_mode:
            self._setup_gpio()
        else:
            logger.warning("KY040 läuft im Dummy-Modus (keine Hardware)")

    def _setup_gpio(self):
        """Initialisiert GPIO Pins"""
        try:
            # GPIO Modus setzen
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            # Pins konfigurieren
            GPIO.setup(self.clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            # Initialen Zustand lesen
            self.clk_last_state = GPIO.input(self.clk_pin)

            # Interrupts einrichten
            GPIO.add_event_detect(
                self.clk_pin,
                GPIO.BOTH,
                callback=self._rotation_callback,
                bouncetime=self.debounce_time
            )

            GPIO.add_event_detect(
                self.sw_pin,
                GPIO.BOTH,
                callback=self._button_callback,
                bouncetime=self.debounce_time
            )

            logger.info(f"KY040 initialisiert: CLK={self.clk_pin}, DT={self.dt_pin}, SW={self.sw_pin}")

        except Exception as e:
            logger.error(f"Fehler beim Initialisieren von GPIO: {e}")
            self._dummy_mode = True

    def _rotation_callback(self, channel):
        """Callback für Drehung"""
        if self._dummy_mode or not self._rotate_callback:
            return

        try:
            clk_state = GPIO.input(self.clk_pin)
            dt_state = GPIO.input(self.dt_pin)

            # Nur bei fallender Flanke von CLK
            if clk_state == 0 and clk_state != self.clk_last_state:
                # Drehrichtung bestimmen
                if dt_state == 0:
                    direction = self.CLOCKWISE
                else:
                    direction = self.COUNTER_CLOCKWISE

                # Callback aufrufen
                if self._rotate_callback:
                    self._rotate_callback(direction)

            self.clk_last_state = clk_state

        except Exception as e:
            logger.error(f"Fehler im Rotations-Callback: {e}")

    def _button_callback(self, channel):
        """Callback für Knopfdruck"""
        if self._dummy_mode:
            return

        try:
            button_state = GPIO.input(self.sw_pin)

            if button_state == 0:  # Knopf gedrückt (LOW)
                self.button_press_time = time.time()
                if self._press_callback:
                    self._press_callback()

            else:  # Knopf losgelassen (HIGH)
                if self.button_press_time:
                    press_duration = time.time() - self.button_press_time

                    # Langer Tastendruck?
                    if press_duration >= self.long_press_time:
                        if self._long_press_callback:
                            self._long_press_callback()
                    # Kurzer Tastendruck wird bereits bei Press behandelt

                    self.button_press_time = None

                if self._release_callback:
                    self._release_callback()

        except Exception as e:
            logger.error(f"Fehler im Button-Callback: {e}")

    def on_rotate(self, callback: Callable[[int], None]):
        """
        Registriert Callback für Drehung

        Args:
            callback: Funktion die bei Drehung aufgerufen wird
                     Erhält direction (1=rechts, -1=links) als Parameter
        """
        self._rotate_callback = callback

    def on_press(self, callback: Callable[[], None]):
        """
        Registriert Callback für Knopfdruck

        Args:
            callback: Funktion die bei Knopfdruck aufgerufen wird
        """
        self._press_callback = callback

    def on_long_press(self, callback: Callable[[], None]):
        """
        Registriert Callback für langen Knopfdruck

        Args:
            callback: Funktion die bei langem Knopfdruck aufgerufen wird
        """
        self._long_press_callback = callback

    def on_release(self, callback: Callable[[], None]):
        """
        Registriert Callback für Knopf loslassen

        Args:
            callback: Funktion die beim Loslassen aufgerufen wird
        """
        self._release_callback = callback

    def start(self):
        """Startet den Encoder"""
        self.running = True
        logger.info("KY040 Rotary Encoder gestartet")

    def stop(self):
        """Stoppt den Encoder"""
        self.running = False
        logger.info("KY040 Rotary Encoder gestoppt")

    def cleanup(self):
        """Räumt GPIO Ressourcen auf"""
        self.stop()
        if not self._dummy_mode:
            try:
                GPIO.cleanup([self.clk_pin, self.dt_pin, self.sw_pin])
                logger.info("GPIO aufgeräumt")
            except Exception as e:
                logger.error(f"Fehler beim Aufräumen von GPIO: {e}")

    def simulate_rotation(self, direction: int):
        """
        Simuliert eine Drehung (für Tests ohne Hardware)

        Args:
            direction: 1 für rechts, -1 für links
        """
        if self._rotate_callback:
            self._rotate_callback(direction)

    def simulate_press(self):
        """Simuliert einen Knopfdruck (für Tests ohne Hardware)"""
        if self._press_callback:
            self._press_callback()

    def simulate_long_press(self):
        """Simuliert einen langen Knopfdruck (für Tests ohne Hardware)"""
        if self._long_press_callback:
            self._long_press_callback()


def main():
    """Test-Funktion"""
    print("="*60)
    print("KY040 Rotary Encoder Test")
    print("="*60)
    print()

    if not GPIO_AVAILABLE:
        print("⚠ RPi.GPIO nicht verfügbar - Dummy-Modus")
        print("Verwenden Sie die simulate_* Methoden zum Testen")
        print()

    # Encoder erstellen
    encoder = KY040RotaryEncoder(
        clk_pin=17,
        dt_pin=27,
        sw_pin=22
    )

    # Callbacks registrieren
    def on_rotate(direction):
        if direction == KY040RotaryEncoder.CLOCKWISE:
            print("↻ Rechts gedreht")
        else:
            print("↺ Links gedreht")

    def on_press():
        print("✓ Knopf gedrückt")

    def on_long_press():
        print("⏱ Langer Knopfdruck erkannt")

    def on_release():
        print("○ Knopf losgelassen")

    encoder.on_rotate(on_rotate)
    encoder.on_press(on_press)
    encoder.on_long_press(on_long_press)
    encoder.on_release(on_release)

    # Encoder starten
    encoder.start()

    print("Encoder bereit!")
    print("Drehen Sie den Encoder oder drücken Sie den Knopf")
    print("Strg+C zum Beenden")
    print()

    if not GPIO_AVAILABLE:
        print("Simuliere Eingaben (ohne echte Hardware):")
        print()
        import time
        for i in range(5):
            time.sleep(1)
            encoder.simulate_rotation(1)
        for i in range(3):
            time.sleep(1)
            encoder.simulate_rotation(-1)
        time.sleep(1)
        encoder.simulate_press()
        time.sleep(2)
        encoder.simulate_long_press()
        print("\nSimulation beendet")
    else:
        try:
            # Warten auf Eingaben
            import signal
            signal.pause()
        except KeyboardInterrupt:
            print("\nBeende...")

    # Aufräumen
    encoder.cleanup()
    print("Test beendet")


if __name__ == '__main__':
    main()
