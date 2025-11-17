import os
import re
import shutil
import tkinter as tk
from typing import List


def filter_paths_by_filetype(paths: List[str], file_types: str) -> List[str]:
    """Filters files of a specific filetype from a list of file paths."""
    file_types = [file_type.strip().lower() for file_type in file_types.split(",")]
    return [path for path in paths if any(path.lower().endswith(file_type) for file_type in file_types)]


def filter_paths_by_substring(paths: List[str], substring: str) -> List[str]:
    """Filters files containing a given substring (case-insensitive)."""
    return [path for path in paths if substring.lower() in path.lower()]


def filter_paths_by_regex(paths: List[str], pattern: str) -> List[str]:
    """Filter out files from a list of file paths using a regular expression pattern."""
    return [path for path in paths if re.search(pattern, path)]


def filter_by_filetype():
    result_field.delete('1.0', tk.END)
    paths = index_directory(source_path_input.get())
    print(f"{filter_paths_by_filetype.__name__}(): {source_path_input.get()}")
    filtered_paths = filter_paths_by_filetype(paths, filetypes_input.get())
    result_field.insert(tk.END, "\n".join(filtered_paths))
    if copy_over_flag.get():
        copy_file_to_destination(filtered_paths)


def filter_by_substring():
    result_field.delete('1.0', tk.END)
    paths = index_directory(source_path_input.get())
    filtered_paths = filter_paths_by_substring(paths, substring_input.get())
    result_field.insert(tk.END, "\n".join(filtered_paths))
    if copy_over_flag.get():
        copy_file_to_destination(filtered_paths)


def filter_by_regex():
    result_field.delete('1.0', tk.END)
    paths = index_directory(source_path_input.get())
    filtered_paths = filter_paths_by_regex(paths, pattern_input.get())
    result_field.insert(tk.END, "\n".join(filtered_paths))
    if copy_over_flag.get():
        copy_file_to_destination(filtered_paths)


def copy_file_to_destination(file_names: List[str]) -> None:
    """Copies a file from source to destination if it doesn't exist in the destination."""
    global num_copied
    for file_name in file_names:
        destination_file_path = os.path.join(destination_path, os.path.basename(file_name))
        print(f"Destination file path: {destination_file_path}")
        print(f"Destination path: {destination_path}")
        print(f"File name: {file_name}")

        if not os.path.exists(destination_file_path):
            print(f"Copying {source_file_path} to {destination_file_path}")
            shutil.copy(source_file_path, destination_file_path)
            num_copied += 1
        else:
            print(f"Skipped {source_file_path}")


def index_directory(source_path: str) -> List[str]:
    """Get the list of all paths found in the user-specified directory."""

    # Initialize variables
    paths = []
    path_len = len(source_path)

    # Walk through the directory and collect paths
    for subdir, dirs, files in os.walk(source_path):
        # Handle empty directories
        if not dirs and not files and subdir != source_path:
            paths.append(subdir[path_len:] + "\\")

        # Collect file paths
        for file in files:
            paths.append(os.path.join(subdir[path_len:], file))

    # Sort paths and print the count
    paths.sort(key=str.casefold)
    print(f"\nFound {len(paths)} files and empty folders.")

    return paths


def create_input_field(root, text, row):
    label = tk.Label(root, text=text)
    label.grid(row=row, column=0, padx=10, pady=10)
    input_field = tk.Entry(root)
    input_field.grid(row=row, column=1, padx=10, pady=10)
    return input_field


def create_button(root, text, command, row):
    button = tk.Button(root, text=text, command=command)
    button.grid(row=row, column=2, padx=10, pady=10)


def create_text_field(root, row, column, rowspan):
    text_field = tk.Text(root)
    text_field.grid(row=row, column=column, padx=10, pady=10, rowspan=rowspan)
    return text_field


def create_checkbox(root, text, row):
    var = tk.BooleanVar()
    checkbox = tk.Checkbutton(root, text=text, variable=var)
    checkbox.grid(row=row, column=2, padx=10, pady=10)
    return var


if __name__ == "__main__":
    # Initialize root window
    root = tk.Tk()
    root.geometry("1050x410")
    root.title("Directory Filter")
    num_copied = 0

    # Create input fields for source path, destination path, file types, substring, and regex pattern
    source_path_input = create_input_field(root, "Source Path:", 0)
    destination_path_input = create_input_field(root, "Destination Path:", 1)
    copy_over_flag = create_checkbox(root, "Copy Over", 1)

    filetypes_input = create_input_field(root, "File types:", 2)
    substring_input = create_input_field(root, "Substring:", 3)
    pattern_input = create_input_field(root, "Pattern:", 4)

    # Create the text field for displaying results
    result_field = create_text_field(root, 0, 3, 5)  # Starts at row 0, column 2 and spans 5 rows

    # Create buttons for filtering by filetype, substring, and regex
    create_button(root, "Filter by Filetype", filter_by_filetype, 2)
    create_button(root, "Filter by Substring", filter_by_substring, 3)
    create_button(root, "Filter by Regex", filter_by_regex, 4)

    root.mainloop()
