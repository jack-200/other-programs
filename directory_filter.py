import os
import re
import shutil
from typing import List


def filter_paths_by_substring(paths: List[str], substring: str) -> List[str]:
    """Filters files containing a given substring (case-insensitive)."""
    return [path for path in paths if substring.lower() in path.lower()]


def filter_paths_by_filetype(paths: List[str], file_types: str) -> List[str]:
    """Filters files of a specific filetype from a list of file paths."""
    file_types = [file_type.strip().lower() for file_type in file_types.split(",")]
    return [path for path in paths if any(path.lower().endswith(file_type) for file_type in file_types)]


def filter_paths_by_regex(paths: List[str], pattern: str) -> List[str]:
    """Filter out files from a list of file paths using a regular expression pattern."""
    return [path for path in paths if re.search(pattern, path)]


def copy_file_to_destination(file_name):
    """Copies a file from source to destination if it doesn't exist in the destination."""
    destination_file_path = os.path.join(destination_path, os.path.basename(file_name))
    if not os.path.exists(destination_file_path):
        shutil.copy(os.path.join(source_path, file_name), destination_file_path)
        global num_copied
        num_copied += 1
    else:
        print(f"Skipped {os.path.join(source_path, file_name)}")


def index_directory():
    """Get the list of all paths found in the user-specified directory."""
    paths = []
    length_of_path = len(source_path)
    for subdir, dirs, files in os.walk(source_path):
        if dirs == files == []:  # if no files in folder
            if subdir != source_path:  # make sure that empty folder is not the source folder
                paths.append(subdir[length_of_path:] + "\\")  # add with backslash
        for file in files:
            paths.append(os.path.join(subdir[length_of_path:], file))  # append paths relative to target path
    paths = sorted(paths, key=str.casefold)  # sort paths case-insensitively
    print(f"\nFound {len(paths)} files and empty folders.")
    return paths


def print_file_types(paths):
    """Count and print the number of each file type."""

    def get_file_type(path):
        return path.split(".")[-1].strip()

    file_types = {}
    for path in paths:
        if "." in path:
            file_type = get_file_type(path)
            file_types[file_type] = file_types.get(file_type, 0) + 1
    print(dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)))  # sort by count


while True:
    print("\nChoose a function:")
    print(f"1. {filter_paths_by_substring.__name__}(): {filter_paths_by_substring.__doc__}")
    print(f"2. {filter_paths_by_filetype.__name__}(): {filter_paths_by_filetype.__doc__}")
    print(f"3. {filter_paths_by_regex.__name__}(): {filter_paths_by_regex.__doc__}")
    print("Q. Quit")
    print("\nYour choice: ", end="")

    choice = input().lower()
    if choice == "q":
        quit()

    print("Directory of source files: ", end="")
    source_path = input() + "\\"
    paths_in_directory = index_directory()
    print_file_types(paths_in_directory)
    if len(paths_in_directory) == 0:
        continue
    print("Copy files to another directory? ", end="")
    print('If yes, input "Y" followed by a space and the path. If no, input anything else: ', end="", )

    moveChoice = input().strip().lower().split(" ")
    destination_path = " ".join(moveChoice[1:])
    copyOver = True if ((len(moveChoice) > 1) and (moveChoice[0] == "y")) else False
    num_copied = 0
    result = []

    if choice == "1":
        print("Input substring to filter by: ", end="")
        result = filter_paths_by_substring(paths_in_directory, input())
    elif choice == "2":
        print("Input file types to filter by png,jpg,: ", end="")
        result = filter_paths_by_filetype(paths_in_directory, input())
    elif choice == "3":
        print("Input regular expression pattern: ", end="")
        result = filter_paths_by_regex(paths_in_directory, input())

    print(f"\n{len(result)} files matched. Copying over...")
    [copy_file_to_destination(path) for path in result]
    print(f"\n{num_copied} files copied over.")
