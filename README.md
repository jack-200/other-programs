# Other-Programs

This is a collection of standalone programs that offer tools for file management, system optimization, and programming.

# pdf_and_image_tools.pyw

![image](https://user-images.githubusercontent.com/86848773/208513617-40b3e4df-9212-4ab5-be8a-a4891a100c11.png)

This program comes with a GUI and buttons connecting to various PDF and image functions. The constant variable
PATH_TO_FOLDER must be changed to the desired directory. The constant variable POPPLER_PATH must be changed to
the ```bin``` folder of poppler. Instructions to install poppler can be found in the README
here: https://github.com/Belval/pdf2image

* **Merge PDFs**: Merges all the PDF files into a single resulting PDF
* **Stitch PDFs**: Stitches all the PDF pages into a single page. Each PDF file will result in one version with the
  pages stitched vertically and the other horizontally.
* **Resave PDFs**: Loads and resaves all the PDF files to reduce file size and prevent PDF mapping errors
* **PDF To Image**: Converts each PDF page to a separate PNG file
* **Image To PDF**: Converts all PNG and JPG files to separate PDF files
* **Crop Images**: Crops images based on user-defined dimensions
* **Merge Images**: Merges all the PNG and JPG files in the directory and saves them as a combination of horizontally
  and vertically merged PNG and JPG formats.
* **Convert Images**: Converts existing image files to a duplicate PNG or JPG format
* **Restart**: Restarts the program as a quick way to apply any code changes and detach from using files
* Files are processed in alphabetical order

# Optimizations.bat

Windows Batch File with commands to clean up the system, apply Windows updates, terminate user-defined programs, and
other performance-improving actions. By default, the script will restart after all the actions. Anytime during the
process, the user has the option to close the window and cancel.

# directory_indexer.py

Console-based program with functions that filter file names in three different ways. Optionally, the search results can
be copied over to another location. These functions include:

* **filter_filetype()**: Filters out files of a specific filetype
* **filter_regex()**: Filters out files using regular expression to search for a pattern
* **filter_by_first_character()**: Filters out files that start with a specific character

# execution_time_tester.py

A simple way to compare the execution times of code in two different functions. The NUMBER_OF_EXECUTIONS variable
dictates how many times to execute the functions. The console prints out the faster function.
