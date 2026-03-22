"""
This script is used to manage the size, position, and visibility of windows.

When running this script as a shortcut:

1. Add pythonw to the beginning of the target path.
2. Check the "Run as Administrator" box.
"""

import ctypes
import json
import os
import sys
import tkinter as tk
import tkinter.messagebox

if sys.platform == "win32":
    import win32con
    import win32gui
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False
    
    if not is_admin:
        tk.messagebox.showerror("Error", "This program requires administrator privileges on Windows. Please run as administrator.")
        sys.exit()
else:
    # On macOS/Linux, we don't use win32con/win32gui or this admin check
    win32con = None
    win32gui = None
    is_admin = True


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

        # Determine the directory of the executable
        if getattr(sys, 'frozen', False):
            self.file_path = os.path.join(os.path.dirname(sys.executable), "window_manager.json")
        else:
            self.file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "window_manager.json")

        # Window dimensions and centering
        self.width, self.height = 600, 400
        self.screen_width = self.main_window.winfo_screenwidth()
        self.screen_height = self.main_window.winfo_screenheight()
        center_x = int((self.screen_width / 2) - (self.width / 2))
        center_y = int((self.screen_height / 2) - (self.height / 2))
        self.main_window.geometry(f"{self.width}x{self.height}+{center_x}+{center_y}")

        # Widget creation and main loop
        self.create_widgets()
        self.main_window.mainloop()

    def create_widgets(self):
        # Define and pack title frames and labels
        self.total_frames = self.num_windows + 2
        self.frames = [tk.Frame(self.main_window) for _ in range(self.total_frames)]
        self.titles = [tk.Label(self.frames[0], text="Print Window Titles", font=("Arial", 16))]
        self.titles.append(tk.Label(self.frames[1], text="Window Properties", font=("Arial", 16)))
        self.window_frames_index_offset = 2

        # Add column labels for input boxes
        self.column_labels = ["                           ", "Name", "                                             ",
            "X", " ", "Y", " ", "Width", "Height"]
        for i, label in enumerate(self.column_labels):
            tk.Label(self.frames[1], text=label, font=("Arial", 8)).pack(side=tk.LEFT, padx=5)

        self.titles += [
            tk.Label(self.frames[i], text=f"Window {i - self.window_frames_index_offset + 1}", font=("Arial", 16)) for i
            in range(self.window_frames_index_offset, self.total_frames)]
        for i in range(self.total_frames):
            self.frames[i].pack(fill=tk.X, padx=5, pady=5)
            if i != 1:  # Skip packing the title for the column labels frame
                self.titles[i].pack(side=tk.LEFT)

        # Create Window objects and load values
        self.windows = [Window(frame, i - self.window_frames_index_offset, self.file_path) for i, frame in
                        enumerate(self.frames[self.window_frames_index_offset:], start=self.window_frames_index_offset)]
        for window in self.windows:
            window.load_values()

        # Pack spacer frame
        tk.Frame(self.frames[0], width=290, height=1).pack(side=tk.LEFT)

        # Define and pack Print button
        self.print_button = tk.Button(self.frames[0], text="Print", command=self.print_button, width=13)
        self.print_button.pack(side=tk.LEFT)

        # Define and pack Update buttons
        self.update_buttons = [tk.Button(self.frames[i], text="Update",
                                         command=lambda i=i: self.update_button(i - self.window_frames_index_offset))
                               for i in range(self.window_frames_index_offset, self.total_frames)]
        for button in self.update_buttons:
            button.pack(side=tk.LEFT, padx=5)

        # Define and pack Toggle buttons
        self.hide_buttons = [tk.Button(self.frames[i], text="Toggle",
                                       command=lambda i=i: self.update_button(i - self.window_frames_index_offset,
                                                                              toggle=True)) for i in
            range(self.window_frames_index_offset, self.total_frames)]
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
        window_data['name'] = window_data['name'].strip()  # Strip the window title
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
        visible_windows = []

        if sys.platform == "win32":
            def window_handler(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title:
                        window_rect = win32gui.GetWindowRect(hwnd)
                        x, y, width, height = window_rect[0], window_rect[1], window_rect[2] - window_rect[0], window_rect[
                            3] - window_rect[1]
                        visible_windows.append(f"{window_title}\nPosition: ({x}, {y}), Size: ({width}, {height})")

            win32gui.EnumWindows(window_handler, None)
        elif sys.platform == "darwin":
            import subprocess
            # Get visible windows and their properties using AppleScript
            script = 'tell application "System Events" to get {name of every window, name} of (every process whose visible is true)'
            output = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip()
            
            # Basic parsing of osascript output (this can be complex, doing a best effort here)
            # The output format is: window_names_list, app_names_list
            # Example: {{}, {Window Name}, {}}, {System, App, Process}
            # We'll try a simpler script to get more structured info
            script = '''
            tell application "System Events"
                set results to ""
                set processList to every process whose visible is true
                repeat with proc in processList
                    set procName to name of proc
                    repeat with win in every window of proc
                        set winName to name of win
                        set winPos to position of win
                        set winSize to size of win
                        set results to results & procName & " - " & winName & "|" & (item 1 of winPos) & "," & (item 2 of winPos) & "|" & (item 1 of winSize) & "," & (item 2 of winSize) & "\n"
                    end repeat
                end repeat
                return results
            end tell
            '''
            output = subprocess.check_output(['osascript', '-e', script]).decode('utf-8').strip()
            if output:
                for line in output.split('\n'):
                    if not line: continue
                    parts = line.split('|')
                    if len(parts) == 3:
                        title = parts[0]
                        pos = parts[1].split(',')
                        size = parts[2].split(',')
                        visible_windows.append(f"{title}\nPosition: ({pos[0]}, {pos[1]}), Size: ({size[0]}, {size[1]})")
        visible_windows.sort()

        # Print result to text widget
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "\n\n".join(visible_windows))

    @staticmethod
    def resize_show_window(self, name, x, y, width, height, toggle=False):
        # Move to center if x and y are -1
        if x == "-1" and y == "-1":
            x = int((self.screen_width / 2) - (int(width) / 2))
            y = int((self.screen_height / 2) - (int(height) / 2))

        if sys.platform == "win32":
            def win_enum_handler(hwnd, _):
                # Check if window name matches
                if win32gui.GetWindowText(hwnd) != name:
                    return

                # Move and resize window
                win32gui.SetForegroundWindow(hwnd)
                win32gui.MoveWindow(hwnd, int(x), int(y), int(width), int(height), True)

                print(f"Window {name} updated to: ({x}, {y}), ({width}, {height})")

                # Toggle window visibility if toggle flag is set
                if toggle:
                    win32gui.ShowWindow(hwnd,
                                        win32con.SW_HIDE if win32gui.IsWindowVisible(hwnd) else win32con.SW_SHOWNORMAL)

            win32gui.EnumWindows(win_enum_handler, None)
        elif sys.platform == "darwin":
            import subprocess
            # name can be "ProcessName - WindowName" or just "WindowName"
            # We'll split it or just try both
            proc_search = name.split(" - ")[0]
            
            # Simple script to find the window and update it
            # This searches for a window with the given name in all processes
            script = f'''
            tell application "System Events"
                set found to false
                set processList to every process whose visible is true
                repeat with proc in processList
                    set procName to name of proc
                    repeat with win in every window of proc
                        set winName to name of win
                        set combinedName to procName & " - " & winName
                        if combinedName is "{name}" or winName is "{name}" then
                            set position of win to {{{x}, {y}}}
                            set size of win to {{{width}, {height}}}
                            set frontmost of proc to true
                            if {str(toggle).lower()} then
                                set visible of proc to not (visible of proc)
                            end if
                            set found to true
                            exit repeat
                        end if
                    end repeat
                    if found then exit repeat
                end repeat
            end tell
            '''
            try:
                subprocess.run(['osascript', '-e', script], check=True)
                print(f"Window {name} updated to: ({x}, {y}), ({width}, {height})")
            except subprocess.CalledProcessError as e:
                print(f"Failed to update window {name}: {e}")


if __name__ == "__main__":
    WindowManager(num_windows=5)
