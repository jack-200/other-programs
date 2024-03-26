# Other-Programs

This is a collection of standalone programs that offer tools for file management, system optimization, and programming.

# pdf_and_image_tool.pyw

![image](https://github.com/jack-200/other-programs/assets/86848773/36828772-6db2-4904-a790-3283728a1d60)

This program comes with a GUI and buttons connecting to various PDF and image functions. The constant variable
PATH_TO_FOLDER must be changed to the desired directory. The constant variable POPPLER_PATH must be changed to
the ```bin``` folder of poppler. Instructions to install poppler can be found in the README
here: https://github.com/Belval/pdf2image

* **Merge PDFs**: Merges all the PDF files into a single resulting PDF file.
* **Stitch PDFs**: Stiches all pages of a PDF into one, creating two versions: one with vertical stitching, another with
  horizontal.
* **Resave Files**: Resave PDFs and images, stripping metadata and potentially reducing size.
* **Encrypt PDF**: Encrypts all PDF files using user-inputted key.
* **Save Page Range**: Saves a range of pages from each PDF file. Formats: '9-99' for pages 9 to 99, '-99' for 1 to
  99, '99-' for 99 onwards, '99' for page 99 only.
* **PDF To Image**: Converts PDF pages to individual PNG files.
* **Image To PDF**: Converts PNG and JPG files to individual PDFs.
* **Sanitize**: Strips metadata and sets a generic name.
* **Crop Images**: Crops images based on predefined dimensions.
* **Merge Images**: Merges all image files in the directory and save them as a combination of horizontally and
  vertically merged PNG and JPG formats.
* **Convert Images**: Converts existing image files to a duplicate PNG or JPG format.
* **Img To Ico**: Converts image files to ICO format
* **Print Metadata**: Prints out the metadata for all image and PDF files.
* **Duplicate Detector**: Scans a directory and identifies any duplicate files using MD5 hashing.
* **Restart**: Restarts the program as a quick way to apply any code changes and detach from using files.
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

# directory_indexer.py

Console-based program with functions that filter file names in three different ways. Optionally, the search results can
be copied over to another location. These functions include:

* **filter_filetype()**: Filters out files of a specific filetype
* **filter_regex()**: Filters out files using regular expression to search for a pattern
* **filter_by_first_character()**: Filters out files that start with a specific character
