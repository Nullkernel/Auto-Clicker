#!/usr/bin/env python3

"""
AutoTap v1.0
A feature-rich auto-clicker with customizable settings and improved user interface.
"""

import time
import threading
import argparse
import sys
from typing import Optional
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener, KeyCode, Key


class AutoClicker:
    """Auto-Clicker with customizable settings and better error handling."""

    def __init__(self, delay: float = 0.1, button: Button = Button.left, 
                 clicks_per_second: Optional[float] = None):
        """
        Initialize the Auto-Clicker.

        Args:
            delay: Delay between clicks in seconds
            button: Mouse button to click (left, right, middle)
            clicks_per_second: Alternative way to set click rate
        """
        self.mouse = MouseController()

        # Calculate delay from CPS if provided
        if clicks_per_second:
            self.delay = 1.0 / clicks_per_second
        else:
            self.delay = max(0.001, delay)  # Minimum delay to prevent system overload

        self.button = button
        self.running = False
        self.program_running = True
        self.click_count = 0
        self.start_time = None

        # Configurable hotkeys
        self.toggle_key = KeyCode(char='1')
        self.stop_key = KeyCode(char='0')
        self.pause_key = KeyCode(char='2')
        self.stats_key = KeyCode(char='3')

        # Threading
        self.click_thread = None
        self.lock = threading.Lock()

        self._print_banner()
        self._print_instructions()

    def _print_banner(self):
        """Print the application banner."""
        banner = """

░█████╗░██╗░░░██╗████████╗░█████╗░████████╗░█████╗░██████╗░
██╔══██╗██║░░░██║╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗
███████║██║░░░██║░░░██║░░░██║░░██║░░░██║░░░███████║██████╔╝
██╔══██║██║░░░██║░░░██║░░░██║░░██║░░░██║░░░██╔══██║██╔═══╝░
██║░░██║╚██████╔╝░░░██║░░░╚█████╔╝░░░██║░░░██║░░██║██║░░░░░
╚═╝░░╚═╝░╚═════╝░░░░╚═╝░░░░╚════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░░░░
        """
        print(banner)

    def _print_instructions(self):
        """Print usage instructions."""
        instructions = f"""
#  Configuration:
   • Click Delay: {self.delay:.3f}s ({1/self.delay:.1f} clicks/second)
   • Mouse Button: {self.button.name.title()}

# Controls:
   • Press '1' - Start/Stop clicking.
   • Press '2' - Pause/Resume clicking.  
   • Press '3' - Show statistics.
   • Press '0' - Exit program.
   • Press 'Esc' - Emergency stop.

>>> Status: Ready - Press '1' to begin.
        """
        print(instructions)

    def start_clicking(self):
        """Start the auto-clicking process."""
        with self.lock:
            if not self.running:
                self.running = True
                self.start_time = time.time()
                print("Auto-Clicker STARTED!")

                if self.click_thread is None or not self.click_thread.is_alive():
                    self.click_thread = threading.Thread(target=self._click_loop, daemon=True)
                    self.click_thread.start()

    def stop_clicking(self):
        """Stop the auto-clicking process."""
        with self.lock:
            if self.running:
                self.running = False
                print("Auto-Clicker STOPPED.")

    def toggle_clicking(self):
        """Toggle the clicking state."""
        if self.running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def show_statistics(self):
        """Display clicking statistics."""
        if self.start_time and self.click_count > 0:
            elapsed = time.time() - self.start_time
            cps = self.click_count / elapsed if elapsed > 0 else 0
            print(f"""
# Statistics:
   • Total Clicks: {self.click_count:,}
   • Runtime: {elapsed:.1f}s
   • Average CPS: {cps:.1f}
   • Status: {'Running' if self.running else 'Stopped'}
            """)
        else:
            print("# No statistics available - Start clicking first!")

    def _click_loop(self):
        """Main clicking loop running in separate thread."""
        while self.program_running:
            if self.running:
                try:
                    self.mouse.click(self.button)
                    self.click_count += 1
                
                    # Removed progress printing to prevent CLI pausing.
                    # Progress can be checked using the '3' key for statistics.
                    
                    time.sleep(self.delay)
                except Exception as e:
                    print(f"# Error during clicking: {e}")
                    self.stop_clicking()
                    break
            else:
                time.sleep(0.01)  # Small delay when not clicking

    def on_key_press(self, key):
        """Handle keyboard input."""
        try:
            if hasattr(key, 'char') and key.char:
                if key.char == '1':
                    self.toggle_clicking()
                elif key.char == '2':
                    if self.running:
                        self.stop_clicking()
                        print("# Paused - Press '1' to resume.")
                    else:
                        print("[1] Use '1' to start/resume clicking.")
                elif key.char == '3':
                    self.show_statistics()
                elif key.char == '0':
                    self.exit_program()
                    return False
            elif key == Key.esc:
                print("# Emergency stop!")
                self.exit_program()
                return False
        except AttributeError:
            pass  # Special keys without char attribute

    def exit_program(self):
        """Gracefully exit the program."""
        print("\n# Shutting down Auto-Clicker...")
        self.running = False
        self.program_running = False
        self.show_statistics()
        print("# Exiting...")

    def run(self):
        """Start the keyboard listener and main program loop."""
        print("# Auto-Clicker is ready! Press hotkeys to control.")

        try:
            with Listener(on_press=self.on_key_press) as listener:
                listener.join()
        except KeyboardInterrupt:
            self.exit_program()
        except Exception as e:
            print(f"# Unexpected error: {e}")
        finally:
            self.program_running = False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Enhanced Auto-Clicker v2.0')
    parser.add_argument('--delay', '-d', type=float, default=0.1,
                       help='Delay between clicks in seconds (default: 0.1)')
    parser.add_argument('--cps', '-c', type=float,
                       help='Clicks per second (overrides delay)')
    parser.add_argument('--button', '-b', choices=['left', 'right', 'middle'],
                       default='left', help='Mouse button to click (default: left)')
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    # Convert button string to Button enum
    button_map = {
        'left': Button.left,
        'right': Button.right,
        'middle': Button.middle
    }

    try:
        clicker = AutoClicker(
            delay=args.delay,
            button=button_map[args.button],
            clicks_per_second=args.cps
        )
        clicker.run()
    except KeyboardInterrupt:
        print("\n# Program interrupted by user.")
    except ImportError as e:
        print(f"# Missing dependency: {e}")
        print("# Install required packages: pip install pynput")
        sys.exit(1)
    except Exception as e:
        print(f"# Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
