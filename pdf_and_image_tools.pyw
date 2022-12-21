import os
import random
import sys

import numpy
from PIL import Image
from PyPDF2 import PdfFileMerger
from PyPDF3 import PdfFileWriter, PdfFileReader
from PyPDF3.pdf import PageObject
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
from pdf2image import convert_from_path

PATH_TO_FOLDER = r""
POPPLER_PATH = r""


def merge_pdfs(path):
    """Merges all the PDF files into a single resulting PDF"""
    file_paths = index_directory(path, "pdf")
    result_name = f"{path}\\!{file_paths[0].split(chr(92))[-1]}"  # use "!" + first PDF as result name
    merger = PdfFileMerger()
    for pdf in file_paths:
        merger.append(pdf)
    merger.write(f"{result_name}")
    merger.close()
    print(f"\nMerge PDF Result: {result_name}")


def stitch_pdfs(path):
    """Stitches all the PDF pages into a single page. Each PDF file will result in one version with the pages
    stitched vertically and the other horizontally."""
    file_paths = index_directory(path, "pdf")

    for file_name in file_paths:
        pdf_file = PdfFileReader(open(file_name, "rb"), strict = False)
        if pdf_file.getNumPages() < 2:
            print(f"Skipped {file_name}: Too little pages")
            continue

        max_width = max_height = total_width = total_height = 0
        pages_data = []
        for count in range(pdf_file.getNumPages()):  # gather page dimension info
            pdf_page = pdf_file.getPage(count)
            pages_data.append(pdf_page)
            width, height = pdf_page.mediaBox.getWidth(), pdf_page.mediaBox.getHeight()
            total_width += width
            total_height += height
            if width > max_width:
                max_width = width
            if height > max_height:
                max_height = height

        result_name_pt1 = f"{'.'.join(file_name.split('.')[:-1])}"
        x_pos = y_pos = 0
        new_page = PageObject.createBlankPage(None, max_width, total_height)  # vertically stitch
        for pdf_page in pages_data[::-1]:  # reverse list
            new_page.mergeTranslatedPage(pdf_page, 0, y_pos)
            y_pos += pdf_page.mediaBox.getHeight()
        output = PdfFileWriter()
        output.addPage(new_page)
        output.write(open(f"{result_name_pt1} !vertical.pdf", "wb"))  # append " !vertical" to file name

        new_page = PageObject.createBlankPage(None, total_width, max_height)  # horizontally stitch
        for pdf_page in pages_data:
            new_page.mergeTranslatedPage(pdf_page, x_pos, 0)
            x_pos += pdf_page.mediaBox.getWidth()
        output = PdfFileWriter()
        output.addPage(new_page)
        output.write(open(f"{result_name_pt1} !horizontal.pdf", "wb"))  # append " !horizontal" to file name


def resave_pdfs(path):
    """Loads and resaves all the PDF files to reduce file size and prevent PDF mapping errors"""
    file_paths = index_directory(path, "pdf")
    for file_path in file_paths:
        saver = PdfFileMerger(strict = False)
        saver.append(file_path)
        while True:  # save to a temporary random-numbered file to delete old file
            temp_pdf_name = "\\\\".join(file_path.split("\\")[:-1])
            temp_pdf_name = f"{temp_pdf_name}{random.randint(0, 10 ** 50)}"
            if temp_pdf_name not in file_paths:
                break
        saver.write(temp_pdf_name)
        saver.close()
        os.remove(file_path)
        saver = PdfFileMerger()
        saver.append(temp_pdf_name)
        saver.write(file_path)
        saver.close()
        os.remove(temp_pdf_name)


def pdf_to_image(path):
    """Converts each PDF page to a separate PNG file"""
    file_paths = index_directory(path, "pdf")
    global POPPLER_PATH
    for file in file_paths:
        pdf_pages = convert_from_path(file, dpi = 300, poppler_path = POPPLER_PATH)
        for page_num, pdf_page in enumerate(pdf_pages):
            pdf_page.save(f"{'.'.join(file.split('.')[:-1])} {page_num}.png")  # append " {page_num}" to file name


def image_to_pdf(path):
    """Converts all PNG and JPG files to separate PDF files"""
    file_paths = index_directory(path, file_types = ["png", "jpg"])
    for file_path in file_paths:
        img = Image.open(file_path)
        img.save(f"{file_path[:-4]}.pdf")


def crop_images(path):
    """Crops images based on user-defined dimensions"""
    file_paths = index_directory(path, file_types = ["png", "jpg"])
    i_right = None
    for file_path in file_paths:  # image cropping is handled on a case-by-case basis
        img_orig = Image.open(file_path)
        if img_orig.size == (1280, 1080):
            i_left = img_orig.crop(box = (0, 0, 1280, 720))  # left, upper, right, and lower coord
        elif img_orig.size == (2560, 720):
            i_left = img_orig.crop(box = (0, 0, 1280, 720))
            i_right = img_orig.crop(box = (1280, 0, 2560, 720))
        elif img_orig.size == (3200, 1080):
            i_left = img_orig.crop(box = (0, 0, 1920, 1080))
            i_right = img_orig.crop(box = (1920, 0, 3200, 1080))
        else:
            print(f"Configuration for {file_path} not set ({img_orig.size})")
            continue
        file_type = file_path.split(".")[-1]
        file_path = ".".join(file_path.split(".")[:-1])
        if i_left:
            i_left.save(f"{file_path} !CROPPED 1.{file_type}")
        if i_right:
            i_right.save(f"{file_path} !CROPPED 2.{file_type}")
        print(f"Cropped {file_path}")


def merge_images(path):
    """Merges all the PNG and JPG files in the directory and saves them as a combination of
    horizontally and vertically merged PNG and JPG formats."""
    file_paths = index_directory(path, file_types = ["png", "jpg"])
    if len(file_paths) == 1:
        print("failed to merge images: need more than one image to merge")
        return

    max_width = max_height = total_height = total_width = 0
    imgs = []
    for file_path in file_paths:  # load image files + get page dimensions
        img_temp = Image.open(file_path)
        imgs.append(img_temp)
        width, height = img_temp.size
        total_width += width
        total_height += height
        if width > max_width:
            max_width = width
        if height > max_height:
            max_height = height

    # merge vertically: scale all images to the largest width value
    v_scaled_imgs = []
    for img in imgs:
        scale_factor = max_width / img.width
        v_scaled_imgs.append(img.resize((max_width, round(scale_factor * img.height))))

    # use vstack to combine images vertically
    imgs_comb = numpy.vstack((numpy.asarray([i for i in v_scaled_imgs], dtype = object)))
    imgs_comb = Image.fromarray(imgs_comb)
    imgs_comb.save(f'{path}\\!vertical.png')
    imgs_comb.convert('RGB').save(f'{path}\\!vertical.jpg')  # discard the Alpha channel for JPG

    # merge horizontally: scale all images to the largest height value
    h_scaled_imgs = []
    for img in imgs:
        scale_factor = max_height / img.height
        h_scaled_imgs.append(img.resize((round(scale_factor * img.width), max_height)))

    # use hstack to combine images horizontally
    imgs_comb = numpy.hstack((numpy.asarray([i for i in h_scaled_imgs], dtype = object)))
    imgs_comb = Image.fromarray(imgs_comb)
    imgs_comb.save(f'{path}\\!horizontal.png')
    imgs_comb.convert('RGB').save(f'{path}\\!horizontal.jpg')


def convert_images(path):
    """Converts existing image files to a duplicate PNG or JPG format"""
    file_paths = index_directory(path, file_types = ["png", "jpg"])
    for file_path in file_paths:
        file_type = file_path.split(".")[-1].lower()
        if "png" == file_type:
            Image.open(file_paths[0]).convert('RGB').save(f"{file_path[:-4]}.jpg")
        elif "jpg" == file_type:
            Image.open(file_paths[0]).save(f"{file_path[:-4]}.png")


def index_directory(path, file_types):
    """Get the list of file names in the target directory"""
    if type(file_types) == list:  # convert file_types into list
        file_types = [f".{i.lower()}" for i in file_types]
    else:
        file_types = [f".{file_types}"]
    file_paths = []
    for subdir, dirs, files in os.walk(path):
        for file in files:
            file_type = f".{file.split('.')[-1].lower()}"
            if file_type in file_types:  # filter by file type
                file_paths.append(f"{subdir}\\{file}")
    print(f"\n{path}: {len(file_paths)} file(s) with file type {file_types}")  # print out the file names found
    for count, file_name in enumerate(file_paths):
        print(f"{count + 1}. {file_name}")
    return file_paths


def calculate_button_position_size(row, col, btn):
    """Size, show and move a button to it's predetermined values"""
    x = (col - 1) * colSpacing
    y = (row - 1) * rowSpacing
    btn.setFixedSize(buttonWidth, buttonHeight)
    btn.move(x, y)
    btn.show()


def restart():
    """Restarts the program as a quick way to apply any code changes and detach from using files"""
    print(restart.__name__)
    python = sys.executable
    os.execl(python, python, *sys.argv)


def quit_clicked():
    """Quit button exits the program"""
    quit_box = QMessageBox()
    quit_box.setText("Are you sure you want to quit?")
    quit_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Ok)
    quit_box.exec_()
    sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QWidget()
    # define structure of buttons
    buttonWidth, buttonHeight = 110, 30
    rowSpacingActual = 20
    colSpacingActual = 10
    rowSpacing = buttonHeight + rowSpacingActual
    colSpacing = buttonWidth + colSpacingActual
    widget.resize(3 * colSpacing - colSpacingActual,
                  4 * rowSpacing - rowSpacingActual)  # ints define how many rows/col to scale window to
    widget.setWindowTitle("PDF and Image Tools")

    # Merge PDFs
    btn = QPushButton(widget)
    btn.setText("Merge PDFs")
    calculate_button_position_size(1, 1, btn)
    btn.clicked.connect(lambda: merge_pdfs(PATH_TO_FOLDER))
    # Stitch PDF pages
    btn = QPushButton(widget)
    btn.setText("Stitch PDFs")
    calculate_button_position_size(1, 2, btn)
    btn.clicked.connect(lambda: stitch_pdfs(PATH_TO_FOLDER))
    # Resave PDF pages
    btn = QPushButton(widget)
    btn.setText("Resave PDFs")
    calculate_button_position_size(1, 3, btn)
    btn.clicked.connect(lambda: resave_pdfs(PATH_TO_FOLDER))

    # PDF to Image
    btn = QPushButton(widget)
    btn.setText("PDF to Image")
    calculate_button_position_size(2, 1, btn)
    btn.clicked.connect(lambda: pdf_to_image(PATH_TO_FOLDER))
    # Image to PDF
    btn = QPushButton(widget)
    btn.setText("Image to PDF")
    calculate_button_position_size(2, 2, btn)
    btn.clicked.connect(lambda: image_to_pdf(PATH_TO_FOLDER))

    # Crop Image
    btn = QPushButton(widget)
    btn.setText("Crop Images")
    calculate_button_position_size(3, 1, btn)
    btn.clicked.connect(lambda: crop_images(PATH_TO_FOLDER))
    # Merge Images
    btn = QPushButton(widget)
    btn.setText("Merge Images")
    calculate_button_position_size(3, 2, btn)
    btn.clicked.connect(lambda: merge_images(PATH_TO_FOLDER))
    # Convert Images
    btn = QPushButton(widget)
    btn.setText("Convert Images")
    calculate_button_position_size(3, 3, btn)
    btn.clicked.connect(lambda: convert_images(PATH_TO_FOLDER))

    # Restart
    btn_res = QPushButton(widget)
    btn_res.setText("Restart")
    calculate_button_position_size(4, 1, btn_res)
    btn_res.clicked.connect(restart)
    # Quit
    btn_quit = QPushButton(widget)
    btn_quit.setText("Quit")
    calculate_button_position_size(4, 2, btn_quit)
    btn_quit.clicked.connect(quit_clicked)

    widget.show()
    sys.exit(app.exec_())
