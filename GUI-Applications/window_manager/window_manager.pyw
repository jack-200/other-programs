"""
This script is used to manage the size, position, and visibility of windows.

When running this script as a shortcut:

1. Add pythonw to the beginning of the target path.
2. Check the "Run as Administrator" box.
"""

import json
import os
import tkinter as tk

import win32con
import win32gui


class Window:
    def __init__(self, parent_widget, window_index, file_path):
        # Initialize window properties
        self.idx = window_index
        self.props = ["name", "x", "y", "width", "height"]
        self.file_path = file_path

        # Create property entries
        self.entries = {prop: tk.Entry(parent_widget, width=30 if prop == "name" else 5) for prop in self.props}

        # Pack entry widgets
        for widget in self.entries.values():
            widget.pack(side=tk.LEFT, padx=5)

    def load_values(self):
        try:
            with open(self.file_path, "r") as json_file:
                data = json.load(json_file)

            # Extract window data and insert into widgets
            window_data = data[self.idx]
            for prop, widget in self.entries.items():
                widget.insert(0, window_data.get(prop, ""))
        except (FileNotFoundError, IndexError):
            pass

    def get_values(self):
        # Return current values of entry widgets
        return {prop: widget.get() for prop, widget in self.entries.items()}


class WindowManager:
    def __init__(self, num_windows):
        # Window setup
        self.main_window = tk.Tk()
        self.main_window.title("Window Manager")
        self.num_windows = num_windows
        self.file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "window_manager.json")

        # Window dimensions
        self.width, self.height = 600, 400
        self.main_window.geometry(f"{self.width}x{self.height}")

        # Screen dimensions
        self.screen_width = self.main_window.winfo_screenwidth()
        self.screen_height = self.main_window.winfo_screenheight()

        # Centering the window
        center_x = int((self.screen_width / 2) - (self.width / 2))
        center_y = int((self.screen_height / 2) - (self.height / 2))
        self.main_window.geometry(f"+{center_x}+{center_y}")

        # Widget creation and main loop
        self.create_widgets()
        self.main_window.mainloop()

    def create_widgets(self):
        # Define and pack title frames and labels
        self.frames = [tk.Frame(self.main_window) for _ in range(self.num_windows + 1)]
        self.titles = [tk.Label(self.frames[0], text="Print Window Titles", font=("Arial", 16))]
        self.titles += [tk.Label(self.frames[i], text=f"Window {i}", font=("Arial", 16)) for i in
                        range(1, self.num_windows + 1)]
        for i in range(self.num_windows + 1):
            self.frames[i].pack(fill=tk.X, padx=5, pady=5)
            self.titles[i].pack(side=tk.LEFT)

        # Create Window objects and load values
        self.windows = [Window(frame, i, self.file_path) for i, frame in enumerate(self.frames[1:])]
        for window in self.windows:
            window.load_values()

        # Pack spacer frame
        tk.Frame(self.frames[0], width=290, height=1).pack(side=tk.LEFT)

        # Define and pack Print button
        self.print_button = tk.Button(self.frames[0], text="Print", command=self.print_button, width=13)
        self.print_button.pack(side=tk.LEFT)

        # Define and pack Update buttons
        self.update_buttons = [tk.Button(self.frames[i], text="Update", command=lambda i=i: self.update_button(i - 1))
                               for i in range(1, self.num_windows + 1)]
        for button in self.update_buttons:
            button.pack(side=tk.LEFT, padx=5)

        # Define and pack Toggle buttons
        self.hide_buttons = [
            tk.Button(self.frames[i], text="Toggle", command=lambda i=i: self.update_button(i - 1, toggle=True)) for i
            in range(1, self.num_windows + 1)]
        for button in self.hide_buttons:
            button.pack(side=tk.LEFT, padx=5)

        # Define and pack result frame
        self.result_frame = tk.Frame(self.main_window)
        self.result_frame.pack(padx=10, pady=10)

        # Define and pack result text widget
        self.result_text = tk.Text(self.result_frame, font=("Arial", 10))
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Define and pack result text widget scrollbar
        self.scrollbar = tk.Scrollbar(self.result_frame, command=self.result_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=self.scrollbar.set)

    def update_button(self, index, toggle=False):
        # Get window data and update the target window
        window_data = self.windows[index].get_values()
        self.resize_show_window(self, **window_data, toggle=toggle)

        # Load existing data from file or initialize as empty list if file not found
        try:
            with open(self.file_path, "r") as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = []

        # Update existing data with new window data
        if len(existing_data) > index:
            existing_data[index] = window_data
        else:
            existing_data.append(window_data)

        # Write updated data back to file
        with open(self.file_path, "w") as file:
            json.dump(existing_data, file, indent=4)

    def print_button(self):
        # Collect visible window information
        window_info = []

        def handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    rect = win32gui.GetWindowRect(hwnd)
                    x, y, w, h = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
                    window_info.append(f"{title}\nPosition: ({x}, {y}), Size: ({w}, {h})")

        win32gui.EnumWindows(handler, None)
        window_info.sort()

        # Print result to text widget
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "\n\n".join(window_info))

    @staticmethod
    def resize_show_window(self, name, x, y, width, height, toggle=False):
        # Move to center if x and y are -1
        if x == "-1" and y == "-1":
            x = int((self.screen_width / 2) - (int(width) / 2))
            y = int((self.screen_height / 2) - (int(height) / 2))

        def win_enum_handler(hwnd, _):
            # Check if window name matches
            if win32gui.GetWindowText(hwnd) != name:
                return

            # Move and resize window
            win32gui.SetForegroundWindow(hwnd)
            win32gui.MoveWindow(hwnd, int(x), int(y), int(width), int(height), True)

            # Toggle window visibility if toggle flag is set
            if toggle:
                win32gui.ShowWindow(hwnd,
                                    win32con.SW_HIDE if win32gui.IsWindowVisible(hwnd) else win32con.SW_SHOWNORMAL)

        win32gui.EnumWindows(win_enum_handler, None)


if __name__ == "__main__":
    WindowManager(num_windows=5)
