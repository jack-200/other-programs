import io
import os
import sys

import numpy
import pypdf
from pdf2image import convert_from_path
from PIL import ExifTags, Image
from PyQt5.QtWidgets import (QApplication, QFormLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSizePolicy,
                             QSpacerItem, QVBoxLayout, QWidget, )

PATH_TO_FOLDER = r""
POPPLER_PATH = r""


def merge_pdfs(path):
    """Merges all the PDF files into a single resulting PDF"""
    file_paths = index_directory(path, "pdf")
    merger = pypdf.PdfMerger()
    for pdf in file_paths:
        merger.append(pdf)
    result_name = f"{path}\\!{_break_path(file_paths[0])[2]}"  # "! {first PDF}" as result name

    merger.write(f"{result_name}")
    merger.close()
    print(f"\nMerge PDF Result: {result_name}")


def stitch_pdfs(path):
    """Stitches all the PDF pages of a single PDF file into a single page. For each PDF file, there will be two
    resulting versions - one with the pages stitched vertically and another with the pages stitched horizontally.
    """
    for file_name in index_directory(path, "pdf"):
        pdf_file = pypdf.PdfReader(open(file_name, "rb"))
        if len(pdf_file.pages) < 2:
            print(f"Skipped {file_name}: Too little pages")
            continue
        max_width = max_height = total_width = total_height = 0
        pages_data = []
        for count in range(len(pdf_file.pages)):  # gather page dimension info
            pdf_page = pdf_file.pages[count]
            pages_data.append(pdf_page)
            width, height = pdf_page.mediabox.width, pdf_page.mediabox.height
            total_width += width
            total_height += height
            if width > max_width:
                max_width = width
            if height > max_height:
                max_height = height

        result_name_pt1 = f"{'.'.join(file_name.split('.')[:-1])}"

        new_page = pypdf.PageObject.create_blank_page(width=max_width, height=total_height)
        for index, pdf_page in enumerate(pages_data):
            new_page.merge_page(pdf_page, expand=True)
            if index != len(pages_data) - 1:
                new_page.add_transformation(pypdf.Transformation().translate(ty=pdf_page.mediabox.height))
        output = pypdf.PdfWriter()
        output.add_page(new_page)
        output.write(open(f"{result_name_pt1} !vertical.pdf", "wb"))

        new_page = pypdf.PageObject.create_blank_page(width=total_width, height=max_height)
        for index, pdf_page in enumerate(pages_data[::-1]):
            new_page.merge_page(pdf_page, expand=True)
            if index != len(pages_data) - 1:
                new_page.add_transformation(pypdf.Transformation().translate(tx=pdf_page.mediabox.width))
        output = pypdf.PdfWriter()
        output.add_page(new_page)
        output.write(open(f"{result_name_pt1} !horizontal.pdf", "wb"))


def resave_files(path):
    """Resave all the PDF and image files to strip metadata and potentially reduce file size"""
    # in pypdf\_writer.py: "NameObject("/Producer"):" line must be commented out to have no PDF metadata
    results = ""
    for file_path in index_directory(path, ["jpeg", "jpg", "pdf", "png"]):
        org_size = os.path.getsize(file_path) / 1024
        if file_path.endswith("pdf"):
            with open(file_path, "rb") as pdf:
                org = io.BytesIO(pdf.read())
            reader = pypdf.PdfReader(org)
            writer = pypdf.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            os.remove(file_path)
            with open(file_path, "wb") as pdf:
                writer.write(pdf)
        else:
            img = Image.open(file_path)
            img_without_metadata = Image.new(img.mode, img.size)
            img_without_metadata.putdata(list(img.getdata()))
            img_without_metadata.save(file_path)
        new_size = os.path.getsize(file_path) / 1024
        pct_chg = f"{round(((new_size - org_size) / org_size) * 100, 1)}%"
        results += file_path + " "
        results += f"{round(org_size, 1)} KB to {round(new_size, 1)} KB ({pct_chg})\n"

    label.setText(results)
    print(results)


def encrypt_pdf(path):
    """Encrypts all PDF files using user-inputted key"""
    input_text = _get_input()
    if not input_text:
        return
    for file_path in index_directory(path, "pdf"):
        with open(file_path, "rb") as f:
            pdf_reader = pypdf.PdfReader(f)
            pdf = pypdf.PdfWriter()
            pdf.append_pages_from_reader(pdf_reader)
            pdf.encrypt(user_password=input_text)
        with open(f"{path}\\!encrypted {_break_path(file_path)[2]}", "wb") as f2:
            pdf.write(f2)


def save_page_range(path, first_page, last_page):
    """Saves the user-specified page range from each PDF file. 9-99 saves pages 9 to 99. -99 saves pages 1 to 99. 99-
    saves pages 99 and those succeeding. 99 saves page 99."""
    input_text = _get_input()
    if not input_text:
        return
    input_text = input_text.split("-")
    print(input_text)
    if len(input_text) > 1:
        if input_text[0] and int(input_text[0]) >= 0 and input_text[1] and int(input_text[1]) > 0:  # 9-99
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
            with open(file_path, "rb") as f:
                last_page = pypdf.PdfReader(f)
                last_page = len(last_page.pages)
        first_page = int(first_page)
        last_page = int(last_page)
        merger = pypdf.PdfMerger()
        merger.append(file_path, pages=(first_page - 1, last_page))
        merger.write(f"{path}\\{first_page}-{last_page} {_break_path(file_path)[2]}")
        merger.close()


def pdf_to_image(path):
    """Converts each PDF page to a separate PNG file"""
    file_paths = index_directory(path, "pdf")
    for file in file_paths:
        pdf_pages = convert_from_path(file, dpi=300, poppler_path=POPPLER_PATH)
        for page_num, pdf_page in enumerate(pdf_pages):
            pdf_page.save(f"{'.'.join(file.split('.')[:-1])} {page_num}.png")  # append " {page_num}" to file name


def image_to_pdf(path):
    """Converts all PNG and JPG files to separate PDF files"""
    for file_path in index_directory(path, file_types=["png", "jpg"]):
        img = Image.open(file_path)
        img.save(f"{_break_path(file_path)[1]}.pdf", "PDF", resolution=img.width / 850 * 100)


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
    file_paths = index_directory(path, file_types=["png", "jpg"])
    i_right = None
    for file_path in file_paths:  # image cropping is handled on a case-by-case basis
        img_orig = Image.open(file_path)
        if img_orig.size == (1280, 1080):
            i_left = img_orig.crop(box=(0, 0, 1280, 720))  # left, upper, right, and lower coord
        elif img_orig.size == (2560, 720):
            i_left = img_orig.crop(box=(0, 0, 1280, 720))
            i_right = img_orig.crop(box=(1280, 0, 2560, 720))
        elif img_orig.size == (3200, 1080):
            i_left = img_orig.crop(box=(0, 0, 1920, 1080))
            i_right = img_orig.crop(box=(1920, 0, 3200, 1080))
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
    file_paths = index_directory(path, file_types=["jpeg", "jpg", "png"])
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
    imgs_comb = numpy.vstack((numpy.asarray([i for i in v_scaled_imgs], dtype=object)))
    imgs_comb = Image.fromarray(imgs_comb)
    imgs_comb.save(f"{path}\\!vertical.png")
    imgs_comb.convert("RGB").save(f"{path}\\!vertical.jpg")  # discard the Alpha channel for JPG

    # merge horizontally: scale all images to the largest height value
    h_scaled_imgs = []
    for img in imgs:
        scale_factor = max_height / img.height
        h_scaled_imgs.append(img.resize((round(scale_factor * img.width), max_height)))

    # use hstack to combine images horizontally
    imgs_comb = numpy.hstack((numpy.asarray([i for i in h_scaled_imgs], dtype=object)))
    imgs_comb = Image.fromarray(imgs_comb)
    imgs_comb.save(f"{path}\\!horizontal.png")
    imgs_comb.convert("RGB").save(f"{path}\\!horizontal.jpg")


def convert_images(path):
    """Converts existing image files to a duplicate PNG or JPG format"""
    file_paths = index_directory(path, file_types=["png", "jpg"])
    for file_path in file_paths:
        file_type = file_path.split(".")[-1].lower()
        if "png" == file_type:
            Image.open(file_path).convert("RGB").save(f"{file_path[:-4]}.jpg")
        elif "jpg" == file_type:
            Image.open(file_path).save(f"{file_path[:-4]}.png")


def img_to_ico(path):
    """Converts image files to ICO format"""
    for file_path in index_directory(path, file_types=["png", "jpg"]):
        img = Image.open(file_path)
        img.save(rf"{_break_path(file_path)[1]}.ico", sizes=[(256, 256), (128, 128)])


def print_metadata(path):
    """prints out the metadata of all image and PDF files"""
    to_label = ""
    f_paths = index_directory(path, file_types=["jpeg", "jpg", "pdf", "png"])
    for i, f_path in enumerate(f_paths):
        to_label += _print_to_label(f"\n{i + 1}. {f_path}\n")
        if f_path.endswith((".png", ".jpg", ".jpeg")):
            img = Image.open(f_path)
            to_label += _print_to_label(
                f"\tWidth, Height, Size, Mode = ({img.width}, {img.height}) {img.format} {img.mode}\n")
            exif_data = img.getexif()
            for tag_id in exif_data:
                tag_name = str(ExifTags.TAGS.get(tag_id, tag_id))
                spaces = 25 - len(tag_name)
                to_label += _print_to_label(f"\t{tag_name + ' ' * spaces}: {exif_data.get(tag_id)}\n")
        elif f_path.endswith(".pdf"):
            with open(f_path, "rb") as f:
                pdf = pypdf.PdfReader(f)
                info = pdf.metadata
                if info:
                    for info_i in info:
                        to_label += _print_to_label(f"{info_i}: {info[info_i]}\n")
                else:
                    to_label += _print_to_label("No Metadata")
    label.setText(to_label)


def _print_to_label(content):
    print(content, end="")
    return content


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
        return str(text)
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
                  5 * rowSpacing - rowSpacingActual)  # ints define how many rows/col to scale window to
    widget.setWindowTitle("PDF and Image Tools")

    # row 1
    program_button("Merge PDFs", 1, 1, lambda: merge_pdfs(PATH_TO_FOLDER))
    program_button("Stitch PDFs", 1, 2, lambda: stitch_pdfs(PATH_TO_FOLDER))
    program_button("Resave Files", 1, 3, lambda: resave_files(PATH_TO_FOLDER))
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
    program_button("Print Metadata", 3, 5, lambda: print_metadata(PATH_TO_FOLDER))

    # row 4
    program_button("Restart", 4, 1, restart)
    program_button("Quit", 4, 2, quit_clicked)

    # bottom text
    layout = QVBoxLayout(widget)
    label = QLabel("Program Idle")
    spacer = QSpacerItem(10, 4 * rowSpacing, QSizePolicy.Minimum, QSizePolicy.Fixed)
    layout.addSpacerItem(spacer)
    layout.addWidget(label)
    label.move(0, 500)

    widget.show()
    app.exec_()
