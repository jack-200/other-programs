# Other-Programs

This is a collection of standalone programs that offer tools for file management, system optimization, and programming.

# pdf_and_image_tools.pyw

![image](https://github.com/jack-200/Other-Programs/assets/86848773/99f814a8-228e-46df-be05-1f299b68d823)

This program comes with a GUI and buttons connecting to various PDF and image functions. The constant variable
PATH_TO_FOLDER must be changed to the desired directory. The constant variable POPPLER_PATH must be changed to
the ```bin``` folder of poppler. Instructions to install poppler can be found in the README
here: https://github.com/Belval/pdf2image

* **Merge PDFs**: Merges all the PDF files into a single resulting PDF
* **Stitch PDFs**: Stitches all the PDF pages of a single PDF file into a single page. For each PDF file, there will be two resulting versions - one with the pages stitched vertically and another with the pages stitched horizontally.
* **Resave Files**: Resave all the PDF and image files to strip metadata and potentially reduce file size
* **Encrypt PDF**: Encrypts all PDF files using user-inputted key
* **Save Page Range**: Saves the user-specified page range from each PDF file. 9-99 saves pages 9 to 99. -99 saves pages 1 to 99. 99- saves pages 99 and those succeeding. 99 saves page 99. 
* **PDF To Image**: Converts each PDF page to a separate PNG file
* **Image To PDF**: Converts all PNG and JPG files to separate PDF files
* **Crop Images**: Crops images based on user-defined dimensions
* **Merge Images**: Merges all image files in the directory and save them as a combination of horizontally and vertically merged PNG and JPG formats.
* **Convert Images**: Converts existing image files to a duplicate PNG or JPG format
* **Img To Ico**: Converts image files to ICO format
* **Print Metadata**: prints out the metadata of all image and PDF files
* **Restart**: Restarts the program as a quick way to apply any code changes and detach from using files
* Files are processed in alphabetical order

<br><br>

# web_content_downloader.py
![image](https://github.com/jack-200/Other-Programs/assets/86848773/cba73f51-605f-42a1-9ada-b1cdc57a47d4)
![image](https://github.com/jack-200/Other-Programs/assets/86848773/3933d1f2-21cb-4f3e-92cc-15de7be5c46b)

Simple standalone tool to download YouTube videos as MP4 and webpages as PDF.
* wkhtmltopdf is needed for the later and can be downloaded from https://wkhtmltopdf.org/.
* Inputting a YouTube playlist will copy the all video links in that playlist to the clipboard.
* Files are saved in same location as script.

To run, the following packages must be installed:
```
python -m pip install --upgrade bs4
python -m pip install --upgrade pdfkit
python -m pip install --upgrade pyperclip
python -m pip install --upgrade pytube
python -m pip install --upgrade requests
```

<br><br>

# Optimizations.bat

Windows Batch File to update important Python packages, run disk cleanup, defrag C drive, repair windows image, run full Microsoft Defender Antivirus scan, and other performance-improving actions.

<br><br>

# directory_indexer.py

Console-based program with functions that filter file names in three different ways. Optionally, the search results can
be copied over to another location. These functions include:

* **filter_filetype()**: Filters out files of a specific filetype
* **filter_regex()**: Filters out files using regular expression to search for a pattern
* **filter_by_first_character()**: Filters out files that start with a specific character
