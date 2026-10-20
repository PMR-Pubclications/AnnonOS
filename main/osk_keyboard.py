#!/usr/bin/env python3
"""
AnnonOS: On-Screen Virtual Keyboard Subsystem
Provides an English QWERTY touch keyboard interface for mobile operating system software.
"""

class AnnonVirtualKeyboard:
    def __init__(self, screen_width=480, screen_height=320):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active_buffer = ""
        self.is_visible = False
        self.layout = self._build_qwerty_layout()

    def _build_qwerty_layout(self):
        """Generates bounding boxes for standard English QWERTY layout."""
        keys = []
        
        # Row 1: Q W E R T Y U I O P
        row1 = "QWERTYUIOP"
        start_x, start_y = 10, 120
        key_w, key_h, spacing = 28, 32, 4
        
        for i, char in enumerate(row1):
            keys.append({
                "char": char,
                "x": start_x + (i * (key_w + spacing)),
                "y": start_y,
                "w": key_w,
                "h": key_h
            })

        # Row 2: A S D F G H J K L
        row2 = "ASDFGHJKL"
        start_x, start_y = 24, 156
        for i, char in enumerate(row2):
            keys.append({
                "char": char,
                "x": start_x + (i * (key_w + spacing)),
                "y": start_y,
                "w": key_w,
                "h": key_h
            })

        # Row 3: Z X C V B N M [BKSP]
        row3 = "ZXCVBNM"
        start_x, start_y = 52, 192
        for i, char in enumerate(row3):
            keys.append({
                "char": char,
                "x": start_x + (i * (key_w + spacing)),
                "y": start_y,
                "w": key_w,
                "h": key_h
            })
            
        # Backspace key
        keys.append({
            "char": "BKSP",
            "x": start_x + (7 * (key_w + spacing)),
            "y": start_y,
            "w": 40,
            "h": key_h
        })
        
        return keys

    def toggle_keyboard(self, visible: bool):
        """Shows or hides the on-screen keyboard."""
        self.is_visible = visible
        print(f"[AnnonOS] Virtual Keyboard Visible: {self.is_visible}")

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


# Example Execution Loop
if __name__ == "__main__":
    osk = AnnonVirtualKeyboard()
    osk.toggle_keyboard(True)

    print("Simulating touch input...")
    osk.handle_touch_event(146, 120)  # Approximate coordinates for 'T'
    osk.handle_touch_event(56, 156)   # Approximate coordinates for 'S'
