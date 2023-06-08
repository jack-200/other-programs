# Other-Programs

This is a collection of standalone programs that offer tools for file management, system optimization, and programming.

# pdf_and_image_tools.pyw

![image](https://user-images.githubusercontent.com/86848773/222896366-230e914b-e057-4059-b1b6-56ecf0acb445.png)

This program comes with a GUI and buttons connecting to various PDF and image functions. The constant variable
PATH_TO_FOLDER must be changed to the desired directory. The constant variable POPPLER_PATH must be changed to
the ```bin``` folder of poppler. Instructions to install poppler can be found in the README
here: https://github.com/Belval/pdf2image

* **Merge PDFs**: Merges all the PDF files into a single resulting PDF
* **Stitch PDFs**: Stitches all the PDF pages of a single PDF file into a single page. For each PDF file, there will be two resulting versions - one with the pages stitched vertically and another with the pages stitched horizontally.
* **Resave PDFs**: Load and resave all the PDF files to reduce file size
* **Encrypt PDF**: Encrypts all PDF files using user-inputted key
* **Save Page Range**: Saves the user-specified page range from each PDF file. 9-99 saves pages 9 to 99. -99 saves pages 1 to 99. 99- saves pages 99 and those succeeding. 99 saves page 99.
* **PDF To Image**: Converts each PDF page to a separate PNG file
* **Image To PDF**: Converts all PNG and JPG files to separate PDF files
* **Crop Images**: Crops images based on user-defined dimensions
* **Merge Images**: Merges all image files in the directory and save them as a combination of horizontally and vertically merged PNG and JPG formats.
* **Img To Ico**: Converts image files to ICO format
* **Img Metadata**: Prints out image metadata
* **Convert Images**: Converts existing image files to a duplicate PNG or JPG format
* **Restart**: Restarts the program as a quick way to apply any code changes and detach from using files
* Files are processed in alphabetical order

# web_content_downloader.py

Simple tool to download YouTube videos as MP4 and webpages as PDF. wkhtmltopdf is needed for the later and can be downloaded from https://wkhtmltopdf.org/. Files are saved in same location as script. 

# Optimizations.bat

Windows Batch File to update important Python packages, run disk cleanup, defrag C drive, repair windows image, run full Microsoft Defender Antivirus scan, and other performance-improving actions.

# directory_indexer.py

Console-based program with functions that filter file names in three different ways. Optionally, the search results can
be copied over to another location. These functions include:

* **filter_filetype()**: Filters out files of a specific filetype
* **filter_regex()**: Filters out files using regular expression to search for a pattern
* **filter_by_first_character()**: Filters out files that start with a specific character
