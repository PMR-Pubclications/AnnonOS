#!/usr/bin/env python3
"""
AnnonOS: Voice-Controlled On-Screen Virtual Keyboard Subsystem
Supports multi-language layouts (English, Russian, etc.) and voice command parsing.
"""

class AnnonVirtualKeyboard:
    def __init__(self, screen_width=480, screen_height=320):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active_buffer = ""
        self.is_visible = False
        self.current_language = "english"
        self.layout = self._build_layout(self.current_language)

    def _build_layout(self, language: str):
        """Generates key bounding boxes based on the selected language layout."""
        keys = []
        key_w, key_h, spacing = 28, 32, 4
        
        if language.lower() == "russian":
            row1 = "ЙЦУКЕНГШЩЗ"
            row2 = "ФЫВАПРОЛДЖ"
            row3 = "ЯЧСМИТЬБЮ"
        else:  # Default English QWERTY
            row1 = "QWERTYUIOP"
            row2 = "ASDFGHJKL"
            row3 = "ZXCVBNM"

        # Build Row 1
        start_x, start_y = 10, 120
        for i, char in enumerate(row1):
            keys.append({"char": char, "x": start_x + (i * (key_w + spacing)), "y": start_y, "w": key_w, "h": key_h})

        # Build Row 2
        start_x, start_y = 24, 156
        for i, char in enumerate(row2):
            keys.append({"char": char, "x": start_x + (i * (key_w + spacing)), "y": start_y, "w": key_w, "h": key_h})

        # Build Row 3 + Backspace
        start_x, start_y = 52, 192
        for i, char in enumerate(row3):
            keys.append({"char": char, "x": start_x + (i * (key_w + spacing)), "y": start_y, "w": key_w, "h": key_h})
            
        keys.append({"char": "BKSP", "x": start_x + (len(row3) * (key_w + spacing)), "y": start_y, "w": 40, "h": key_h})
        
        return keys

    def toggle_keyboard(self, visible: bool):
        """Shows or hides the on-screen keyboard."""
        self.is_visible = visible
        print(f"[AnnonOS] Virtual Keyboard Visible: {self.is_visible} ({self.current_language.upper()})")

    def change_layout(self, language: str):
        """Switches keyboard layout format (e.g., english, russian)."""
        lang = language.lower()
        if lang in ["english", "russian"]:
            self.current_language = lang
            self.layout = self._build_layout(self.current_language)
            print(f"[AnnonOS] Keyboard format changed to: {self.current_language.upper()}")
        else:
            print(f"[AnnonOS] Error: Unsupported layout format '{language}'")

    def process_voice_command(self, voice_transcript: str):
        """Parses speech transcripts from the AI pipeline to control keyboard states."""
        transcript = voice_transcript.lower().strip()
        
        if "open keyboard" in transcript:
            self.toggle_keyboard(True)
        elif "close keyboard" in transcript:
            self.toggle_keyboard(False)
        elif "change keyboard format" in transcript or "switch keyboard" in transcript:
            if "russian" in transcript:
                self.change_layout("russian")
            elif "english" in transcript:
                self.change_layout("english")
            else:
                print("[AnnonOS] Voice command received, but target language format was unclear.")
        else:
            print(f"[AnnonOS] Unrecognized voice command: '{voice_transcript}'")

    def handle_touch_event(self, touch_x: int, touch_y: int) -> str:
        """Processes touch screen coordinates and updates input buffer."""
        if not self.is_visible:
            return self.active_buffer

        for key in self.layout:
            if (key["x"] <= touch_x <= key["x"] + key["w"]) and \
               (key["y"] <= touch_y <= key["y"] + key["h"]):
                
                if key["char"] == "BKSP":
                    if len(self.active_buffer) > 0:
                        self.active_buffer = self.active_buffer[:-1]
                else:
                    self.active_buffer += key["char"]
                
                print(f"[OSK] Current Input: {self.active_buffer}")
                break
                
        return self.active_buffer

    def get_input_buffer(self) -> str:
        return self.active_buffer


# Example Execution & Voice Command Simulation
if __name__ == "__main__":
    osk = AnnonVirtualKeyboard()

    print("--- Simulating Voice Control Pipeline ---")
    osk.process_voice_command("Open keyboard")
    osk.process_voice_command("Change keyboard format Russian")
    osk.process_voice_command("Switch keyboard to English")
    osk.process_voice_command("Close keyboard")
