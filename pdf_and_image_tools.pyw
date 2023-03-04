import io
import os
import sys

import numpy
from PIL import Image, ExifTags
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QLineEdit, QFormLayout
from pdf2image import convert_from_path
from pypdf._merger import PdfMerger
from pypdf._page import PageObject
from pypdf._reader import PdfReader
from pypdf._writer import PdfWriter

PATH_TO_FOLDER = r""
POPPLER_PATH = r""


def merge_pdfs(path):
    """Merges all the PDF files into a single resulting PDF"""
    file_paths = index_directory(path, "pdf")
    merger = PdfMerger()
    for pdf in file_paths:
        merger.append(pdf)
    result_name = f"{path}\\!{_break_path(file_paths[0])[2]}"  # "! {first PDF}" as result name
    merger.write(f"{result_name}")
    merger.close()
    print(f"\nMerge PDF Result: {result_name}")


def stitch_pdfs(path):
    """Stitches all the PDF pages of a single PDF file into a single page. For each PDF file, there will be two
    resulting versions - one with the pages stitched vertically and another with the pages stitched horizontally."""
    for file_name in index_directory(path, "pdf"):
        pdf_file = PdfReader(open(file_name, "rb"), strict = False)
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
        output = PdfWriter()
        output.add_page(new_page)
        output.write(open(f"{result_name_pt1} !vertical.pdf", "wb"))  # append " !vertical" to file name

        new_page = PageObject.createBlankPage(None, total_width, max_height)  # horizontally stitch
        for pdf_page in pages_data:
            new_page.mergeTranslatedPage(pdf_page, x_pos, 0)
            x_pos += pdf_page.mediaBox.getWidth()
        output = PdfWriter()
        output.add_page(new_page)
        output.write(open(f"{result_name_pt1} !horizontal.pdf", "wb"))  # append " !horizontal" to file name


def resave_pdfs(path):
    """Load and resave all the PDF files to reduce file size"""
    for file_path in index_directory(path, "pdf"):
        with open(file_path, "rb") as pdf:
            old = io.BytesIO(pdf.read())
        reader = PdfReader(old, strict = False)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        os.remove(file_path)
        with open(file_path, "wb") as pdf:
            writer.write(pdf)


def encrypt_pdf(path):
    """Encrypts all PDF files using user-inputted key"""
    input_text = _get_input()
    if not input_text:
        return
    for file_path in index_directory(path, "pdf"):
        with open(file_path, "rb") as f:
            pdf_reader = PdfReader(f)
            pdf = PdfWriter()
            pdf.append_pages_from_reader(pdf_reader)
            pdf.encrypt(user_password = input_text)
        with open(f"{path}\\!encrypted {_break_path(file_path)[2]}", "wb") as f2:
            pdf.write(f2)


def save_page_range(path, first_page, last_page):
    """Saves the user-specified page range from each PDF file. 9-99 saves pages 9 to 99. -99 saves pages 1 to 99. 99-
    saves pages 99 and those succeeding. 99 saves page 99."""
    input_text = _get_input()
    if not input_text:
        return
    input_text = input_text.split("-")
    if len(input_text) > 1:
        if input_text[0] != "" and int(input_text[0]) >= 0:  # 9-99
            first_page = input_text[0]
            last_page = input_text[1]
        elif input_text[0] == "":  # -99
            first_page = 0
            last_page = input_text[1]
        elif input_text[1] == "":  # 99-
            first_page = input_text[0]
            last_page = -1
    else:  # 99
        first_page = last_page = input_text[0]

    for file_path in index_directory(path, "pdf"):
        if last_page == -1:
            last_page = PdfReader(file_path).getNumPages()
        first_page = int(first_page)
        last_page = int(last_page)
        merger = PdfMerger()
        merger.append(file_path, pages = (first_page - 1, last_page))
        merger.write(f"{path}\\{first_page}-{last_page} {_break_path(file_path)[2]}")
        merger.close()


def pdf_to_image(path):
    """Converts each PDF page to a separate PNG file"""
    file_paths = index_directory(path, "pdf")
    for file in file_paths:
        pdf_pages = convert_from_path(file, dpi = 300, poppler_path = POPPLER_PATH)
        for page_num, pdf_page in enumerate(pdf_pages):
            pdf_page.save(f"{'.'.join(file.split('.')[:-1])} {page_num}.png")  # append " {page_num}" to file name


def image_to_pdf(path):
    """Converts all PNG and JPG files to separate PDF files"""
    for file_path in index_directory(path, file_types = ["png", "jpg"]):
        img = Image.open(file_path)
        img.save(f"{_break_path(file_path)[1]}.pdf")


def input_box(row_spacing, col_spacing, button_width, button_height, col_spacing_actual):
    """The content of the input box will be used in certain functions"""

    def update_input_text(text):
        global input_text
        input_text = text

    box = QLineEdit(widget)
    box.textChanged.connect(update_input_text)
    x = (4 - 1) * col_spacing
    y = (2 - 1) * row_spacing
    box.move(x, y)
    box.resize(button_width * 2 + col_spacing_actual, button_height)
    labels = QFormLayout()
    labels.addRow("Input Box: ", box)
    box.show()


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
    """Merges all image files in the directory and save them as a combination of horizontally and vertically merged
    PNG and JPG formats."""
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


def img_to_ico(path):
    """Converts image files to ICO format"""
    for file_path in index_directory(path, file_types = ["png", "jpg"]):
        img = Image.open(file_path)
        img.save(fr"{_break_path(file_path)[1]}.ico", sizes = [(256, 256), (128, 128)])


def img_metadata(path):
    """Prints out image metadata"""
    file_paths = index_directory(path, file_types = ["png", "jpg"])
    print("\n")
    for index, file_path in enumerate(file_paths):
        image = Image.open(file_path)
        print(f"{index + 1}. {file_path}")
        print(f"\tWidth, Height, Size, Mode = ({image.width}, {image.height}) {image.format} {image.mode}")
        exif_data = image.getexif()
        for tag_id in exif_data:
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            print(f"\t{tag_name:25}: {exif_data.get(tag_id)}")
        print()


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


def program_button(name, row, col, function):
    """Show and program a button's Text, Position, Size, and Function"""
    btn = QPushButton(widget)
    btn.setText(name)
    x = (col - 1) * colSpacing
    y = (row - 1) * rowSpacing
    btn.setFixedSize(buttonWidth, buttonHeight)
    btn.move(x, y)
    btn.clicked.connect(function)
    btn.show()


def _break_path(path):
    """function to handle file path slicing, for better code readability"""
    split = path.split("\\")
    file_location = "\\".join(split[:-1])
    file_name_type = split[-1]
    _name_split = split[-1].split(".")
    file_name = ".".join(_name_split[:-1])
    file_type = _name_split[-1]
    file_location_name = f"{file_location}\\{file_name}"
    return file_location, file_location_name, file_name_type, file_name, file_type


def _get_input():
    """check if input box contains content"""
    try:
        global input_text
        text = input_text
        return text
    except NameError:
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QWidget()

    buttonWidth, buttonHeight = 120, 30
    rowSpacingActual = 20
    colSpacingActual = 10
    rowSpacing = buttonHeight + rowSpacingActual
    colSpacing = buttonWidth + colSpacingActual
    widget.resize(5 * colSpacing - colSpacingActual,
                  4 * rowSpacing - rowSpacingActual)  # ints define how many rows/col to scale window to
    widget.setWindowTitle("PDF and Image Tools")

    # row 1
    program_button("Merge PDFs", 1, 1, lambda: merge_pdfs(PATH_TO_FOLDER))
    program_button("Stitch PDFs", 1, 2, lambda: stitch_pdfs(PATH_TO_FOLDER))
    program_button("Resave PDFs", 1, 3, lambda: resave_pdfs(PATH_TO_FOLDER))
    program_button("Encrypt PDF", 1, 4, lambda: encrypt_pdf(PATH_TO_FOLDER))
    program_button("Save Page Range", 1, 5, lambda: save_page_range(PATH_TO_FOLDER, 0, 0))

    # row 2
    program_button("PDF to Image", 2, 1, lambda: pdf_to_image(PATH_TO_FOLDER))
    program_button("Image to PDF", 2, 2, lambda: image_to_pdf(PATH_TO_FOLDER))
    global input_text
    input_box(rowSpacing, colSpacing, buttonWidth, buttonHeight, colSpacingActual)

    # row 3
    program_button("Crop Images", 3, 1, lambda: crop_images(PATH_TO_FOLDER))
    program_button("Merge Images", 3, 2, lambda: merge_images(PATH_TO_FOLDER))
    program_button("Convert Images", 3, 3, lambda: convert_images(PATH_TO_FOLDER))
    program_button("Image to ICO", 3, 4, lambda: img_to_ico(PATH_TO_FOLDER))
    program_button("Image Metadata", 3, 5, lambda: img_metadata(PATH_TO_FOLDER))

    # row 4
    program_button("Restart", 4, 1, restart)
    program_button("Quit", 4, 2, quit_clicked)

    widget.show()
    sys.exit(app.exec_())
