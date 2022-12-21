import os
import re
import shutil


def filter_filetype(filetypes):
    """Filters out files of a specific filetype

    Args:
        filetypes (list): list containing the filetypes
    """
    results = []
    for filepath in paths_in_directory:
        if not filepath.endswith("\\"):  # skip empty folders
            if filepath.split(".")[-1] in filetypes:  # if correct file type
                copy_over(f"{src_path}{filepath}")
                results.append(filepath)
    print(f"\n{len(results)} of {len(paths_in_directory)} are of the specified filetype")
    print(f"{num_copied} files were copied over")


def filter_regex(pattern):
    """Filters out files using regular expression to search for a pattern

    Args:
        pattern (str): the regex search pattern
    """
    results = []
    for path in paths_in_directory:
        if path.endswith("\\"):  # skip paths that lead to empty folder
            continue
        file_name = path.split("\\")[-1]  # only keep file name section of path
        search_result = re.search(pattern, file_name)
        if search_result:
            copy_over(f"{src_path}{path}")
            results.append(search_result)
    print(f"{len(results)} of {len(paths_in_directory)} contain given regular expression pattern")
    print(f"{num_copied} files were copied over")


def filter_by_first_character(char):
    """Filters out files that start with a specific character

    Args:
        char (str): the first character to filter by
    """
    results = []
    char = char.lower()
    for path in paths_in_directory:
        file_name = path.split("\\")[-1]
        if file_name[0] == char:
            copy_over(f"{src_path}{path}")
            results.append(path)
            continue
    # print out count even if zero files
    print(f"{len(results)} of {len(paths_in_directory)} paths begin with \"{char}\"")
    print(f"{num_copied} files were copied over")


def copy_over(source):
    """Takes path of the file name of file to be copied

    Args:
        source (str): the full path of file to copy over
    """
    if copyOver:
        dst_path = f"{moveChoice[1]}\\{source.split(chr(92))[-1]}"
        if not os.path.exists(dst_path):  # make sure nothing is overwritten
            shutil.copy(source, dst_path)
            global num_copied
            num_copied += 1


def index_directory():
    """Get the list of all paths found in the user-specified directory.

    Returns:
        list: A list of strings of the relative paths
    """
    paths = []
    length_of_path = len(src_path)
    for subdir, dirs, files in os.walk(src_path):
        if dirs == files == []:  # if there are no files in a folder, add that folder to list with a backslash appended
            if subdir != src_path:  # make sure that empty folder is not the source folder
                paths.append(subdir[length_of_path:] + "\\")
        for file in files:
            paths.append(os.path.join(subdir[length_of_path:], file))  # append paths relative to target path
    paths = sorted(paths, key = str.casefold)  # sort list
    print(f"Found {len(paths)} files and empty folders.")
    return paths


while True:
    print("\nChoose a function:")
    print(f"1. {filter_filetype.__name__}(): {filter_filetype.__doc__.split(chr(10))[0]}")
    print(f"2. {filter_regex.__name__}(): {filter_regex.__doc__.split(chr(10))[0]}")
    print(f"3. {filter_by_first_character.__name__}(): {filter_by_first_character.__doc__.split(chr(10))[0]}")
    print("Q. Quit")
    print("\nYour choice: ", end = "")
    choice = input().lower()

    if choice == "q":
        quit()

    print("Directory of source files: ", end = "")
    src_path = input() + "\\"  # path should end with backslash, so it can be used as a relative path
    paths_in_directory = index_directory()
    if len(paths_in_directory) == 0:
        continue
    print("Copy files to another directory? ", end = "")
    print("If yes, input \"Y\" followed by a space and the path. If no, input anything else: ", end = "")

    moveChoice = input().strip().lower().split(" ")
    copyOver = True if ((len(moveChoice) == 2) and (moveChoice[0] == "y")) else False
    num_copied = 0

    if choice == "1":
        print("Input file type(s) to filter by. Separate multiple inputs with comma (png, jpg): ", end = "")
        filetypes = input().lower().split(",")
        for index, filetype in enumerate(filetypes):  # remove any whitespace
            filetypes[index] = f"{filetype.strip()}"
        filter_filetype(filetypes)

    elif choice == "2":
        print("Regular expression with re.search(): ", end = "")
        expression = input()
        filter_regex(expression)

    elif choice == "3":
        print("What is the character to filter by? ", end = "")
        character = input()
        filter_by_first_character(character)
