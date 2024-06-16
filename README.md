# Other-Programs

This is a collection of standalone programs that offer tools for file management, system optimization, and programming.

# [PDF and Image Tools](GUI-Applications/pdf_and_image_tools.pyw)

![image](https://github.com/jack-200/other-programs/assets/86848773/51f71f89-5644-4c4c-b7d4-956c193e49ac)

This program comes with a GUI and buttons connecting to various PDF and image functions. The constant variable
PATH_TO_FOLDER must be changed to the desired directory. The constant variable POPPLER_PATH must be changed to
the ```bin``` folder of poppler. Instructions to install poppler can be found in the README
here: https://github.com/Belval/pdf2image

* **Merge PDFs**: Combines all PDFs in the directory into one PDF file.
* **Stitch PDFs**: Stitches all PDF pages into one, creating vertical and horizontal versions.
* **Encrypt PDF**: Encrypts PDFs in the directory with the user-provided key.
* **Save Page Range**: Saves a range of pages from each PDF file. Formats: '9-99' for pages 9 to 99, '-99' for 1 to
  99, '99-' for 99 onwards, '99' for page 99 only.
* **Resave Files**: Resave PDFs and images, stripping metadata and potentially reducing size.
* **PDF To Image**: Converts PDF pages to individual PNG files.
* **Image To PDF**: Converts PNG and JPG files to individual PDFs.
* **Sanitize**: Strips metadata and sets a generic file name.
* **Crop Images**: Crops images based on predefined dimensions.
* **Merge Images**: Merges all image files in the directory and save them as a combination of horizontally and
  vertically merged PNG and JPG formats.
* **Convert Images**: Converts existing image files to a duplicate PNG or JPG format.
* **Img To Ico**: Converts image files to ICO format
* **Print Metadata**: Prints out the metadata for all image and PDF files.
* **Duplicate Detector**: Scans a directory and identifies any duplicate files using MD5 hashing.
* **Get Image Colors**: Get the average color and most common colors of all images in the directory.
* **Crop By 90**: Crops images by 90% of their dimensions, removing the outer parts of the image.
* **Enhance Contrast**: Enhance the contrast of a PDF by 25%.
* **Restart Program**: Restarts the program to apply code changes and detach from file usage.
* **Quit**: Handle quit button click event.
* Files are processed in alphabetical order

<br><br>

# [Web Content Downloader](GUI-Applications/web_content_downloader/web_content_downloader.py)

![image](https://github.com/jack-200/other-programs/assets/86848773/f61602b8-f7b5-4e7f-a7c1-36cd3c115d47)
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

# [Directory Filter](GUI-Applications/directory_filter.pyw)

![image](https://github.com/jack-200/other-programs/assets/86848773/4d4429af-28c5-4db4-a068-150aab34edf2)

A tool for filtering files in a directory with the following functionalities:

* **Filter files by file type:** Files in the source directory that match the specified list of file types.

* **Filter files by substring:** Files in the source directory whose names contain the specified substring.

* **Filter files by regex:** Files in the source directory whose names match the specified regular expression pattern.

* **Copy files:** The filtered files can be copied to a specified destination directory.
