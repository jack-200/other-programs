# Other-Programs

A collection of standalone programs offering tools for file management, system optimization, and programming utilities.

## 📋 Table of Contents

- [PDF and Image Tools](#pdf-and-image-tools)
- [Web Content Downloader](#web-content-downloader)
- [Window Manager](#window-manager)
- [Directory Filter](#directory-filter)
- [Report Generator](#report-generator)
- [Setup Instructions](#setup-instructions)

---

## 📄 [PDF and Image Tools](pdf_and_image_tools/main.pyw)

![PDF and Image Tools Interface](https://github.com/jack-200/other-programs/assets/86848773/71a45eee-b12a-418b-ab6f-77007146ba91)

A comprehensive GUI application for PDF and image manipulation with various processing capabilities.

### 📋 PDF Operations

| Feature              | Description                                                                                                                                             |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Merge PDFs**       | Combines all PDFs in the directory into one PDF file                                                                                                    |
| **Stitch PDFs**      | Stitches all PDF pages into one, creating vertical and horizontal versions                                                                              |
| **Encrypt PDF**      | Encrypts PDFs in the directory with a user-provided key                                                                                                 |
| **Save Page Range**  | Saves a range of pages from each PDF file. Formats: `9-99` for pages 9 to 99, `-99` for pages 1 to 99, `99-` for page 99 onwards, `99` for page 99 only |
| **Enhance Contrast** | Enhances the contrast of a PDF by 25%                                                                                                                   |
| **PDF To Image**     | Converts PDF pages to individual PNG files                                                                                                              |

### 🖼️ Image Operations

| Feature              | Description                                                                                                                       |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Image To PDF**     | Converts PNG and JPG files to individual PDFs                                                                                     |
| **Crop Images**      | Crops images based on predefined dimensions                                                                                       |
| **Merge Images**     | Merges all image files in the directory and saves them as a combination of horizontally and vertically merged PNG and JPG formats |
| **Convert Images**   | Converts existing image files to duplicate PNG or JPG format                                                                      |
| **Img To ICO**       | Converts image files to ICO format                                                                                                |
| **Get Image Colors** | Gets the average color and most common colors of all images in the directory                                                      |
| **Crop By 90%**      | Crops images by 90% of their dimensions, removing the outer parts of the image                                                    |

### 🛠️ General File Operations

| Feature                | Description                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------ |
| **Resave Files**       | Resaves PDFs and images, stripping metadata and potentially reducing file size       |
| **Sanitize**           | Strips metadata and sets a generic filename                                          |
| **Print Metadata**     | Prints out the metadata for all image and PDF files                                  |
| **Rename Files**       | Renames all files in a directory with a specified base name and sequential numbering |
| **Duplicate Detector** | Scans a directory and identifies any duplicate files using MD5 hashing               |

### ⚙️ Settings

| Feature             | Description                                                           |
| ------------------- | --------------------------------------------------------------------- |
| **Restart Program** | Restarts the program to apply code changes and detach from file usage |
| **Quit**            | Handles quit button click event                                       |

### 🔧 Configuration

- Files are processed in alphabetical order
- The variable `PATH_TO_FOLDER` points to the source directory. It defaults to the `Downloads/PDF-IMG` folder
- The variable `POPPLER_PATH` must be set to the `bin` folder of Poppler. Instructions to install Poppler can be found in the README here: https://github.com/Belval/pdf2image
- `cairosvg` and `img2pdf` require additional dependencies. They enable the conversion of SVG files to PNG and increase the contrast of PDFs
- `PyQt5` requires the "Desktop development with C++" workload from the Microsoft C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/

---

## 🌐 [Web Content Downloader](web_content_downloader/main.py)

![Web Content Downloader Interface](https://github.com/jack-200/other-programs/assets/86848773/f61602b8-f7b5-4e7f-a7c1-36cd3c115d47)
![Web Content Downloader Example](https://github.com/jack-200/Other-Programs/assets/86848773/3933d1f2-21cb-4f3e-92cc-15de7be5c46b)

Simple standalone tool to download YouTube videos as MP4 and webpages as PDF.

### 📋 Features

| Feature                    | Description                                                                              |
| -------------------------- | ---------------------------------------------------------------------------------------- |
| **YouTube Video Download** | Downloads YouTube videos as MP4 files                                                    |
| **Webpage to PDF**         | Converts webpages to PDF format                                                          |
| **Playlist Support**       | Inputting a YouTube playlist will copy all video links in that playlist to the clipboard |
| **Local Storage**          | Files are saved in same location as script                                               |

### 🔧 Requirements

- **wkhtmltopdf** is needed for webpage conversion and can be downloaded from https://wkhtmltopdf.org/

---

## 🪟 Window Manager

**File:** [`window_manager/window_manager.pyw`](window_manager/window_manager.pyw)

![Window Manager Interface](https://github.com/jack-200/other-programs/assets/86848773/fdedc72a-0016-46e0-8cb8-ab6aac16fd14)

A tool for managing windows on the desktop with comprehensive window control functionalities.

### 📋 Features

| Feature                  | Description                                                    |
| ------------------------ | -------------------------------------------------------------- |
| **Print**                | Outputs details (title, position, size) of all visible windows |
| **Update**               | Modifies the specified window's location and dimensions        |
| **Toggle**               | Applies Update and additionally toggles window visibility      |
| **Settings Persistence** | Input values are saved to a .json file                         |

### 🔧 Installation as Executable

This program can be converted to an executable using PyInstaller:

```bash
pyinstaller --onefile --windowed window_manager\window_manager.pyw
```

---

## 📁 Directory Filter

**File:** [`content-tools/directory_filter.pyw`](content-tools/directory_filter.pyw)

![Directory Filter Interface](https://github.com/jack-200/other-programs/assets/86848773/4d4429af-28c5-4db4-a068-150aab34edf2)

A tool for filtering files in a directory with multiple filtering options and file management capabilities.

### 📋 Features

| Feature                 | Description                                                                              |
| ----------------------- | ---------------------------------------------------------------------------------------- |
| **Filter by File Type** | Files in the source directory that match the specified list of file types                |
| **Filter by Substring** | Files in the source directory whose names contain the specified substring                |
| **Filter by Regex**     | Files in the source directory whose names match the specified regular expression pattern |
| **Copy Files**          | The filtered files can be copied to a specified destination directory                    |

---

## 📊 Report Generator

**File:** [`shell-scripts/ReportGenerator.ps1`](shell-scripts/ReportGenerator.ps1)

![Report Generator Output](https://github.com/jack-200/other-programs/assets/86848773/43e68edb-0c8f-4773-a053-147f9e04e3c2)

This PowerShell script generates comprehensive system reports and saves them in the user's Downloads folder with the current date in the filename.

### 📋 Generated Reports

| Report Type            | Description                                         |
| ---------------------- | --------------------------------------------------- |
| **Battery Report**     | Current battery status and detailed battery history |
| **System Information** | Comprehensive system information report             |
| **DirectX Diagnostic** | Graphics and multimedia diagnostics report          |

### 🔧 Setup Requirements

| Requirement                   | Command/Description                                                       |
| ----------------------------- | ------------------------------------------------------------------------- |
| **Enable PowerShell Scripts** | Use `Set-ExecutionPolicy RemoteSigned`. Note the potential security risks |
| **Run with Admin Rights**     | Use `powershell.exe -File "C:\path\to\script.ps1"`                        |

---

## 🚀 Setup Instructions

### 💾 Installation

```bash
# Create Virtual Environment
python -m venv venv

# Activate Environment and Install Dependencies
venv\Scripts\activate && python -m pip install --upgrade -r requirements.txt
```

### ▶️ Running the Applications

```bash
# PDF and Image Tools
venv\Scripts\activate && python pdf_and_image_tools\main.pyw

# Web Content Downloader
venv\Scripts\activate && python web_content_downloader\main.py

# Directory Filter
venv\Scripts\activate && python content-tools\directory_filter.pyw

# Window Manager
venv\Scripts\activate && python window_manager\window_manager.pyw
```
