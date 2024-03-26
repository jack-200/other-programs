import hashlib
import io
import os
import sys

import numpy
import pypdf
from PIL import ExifTags, Image
from PyQt5.QtWidgets import (QApplication, QFormLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSizePolicy,
                             QSpacerItem, QVBoxLayout, QWidget, )
from pdf2image import convert_from_path

PATH_TO_FOLDER = r""
POPPLER_PATH = r""


def merge_pdfs(directory_path):
    """Merges all the PDF files into a single resulting PDF file."""
    file_paths = index_directory(directory_path, "pdf")

    pdf_merger = pypdf.PdfMerger()
    for pdf_file in file_paths:
        pdf_merger.append(pdf_file)

    result_file_name = f"{directory_path}\\!{get_file_name(file_paths[0])}"  # "!{first PDF}"

    pdf_merger.write(f"{result_file_name}")
    pdf_merger.close()
    print(f"\nMerge PDF Result: {result_file_name}")


def stitch_pdfs(path):
    """Stiches all pages of a PDF into one, creating two versions: one with vertical stitching, another with horizontal."""
    for file_name in index_directory(path, "pdf"):
        pdf_file = pypdf.PdfReader(open(file_name, "rb"))

        if len(pdf_file.pages) < 2:
            print(f"Skipped {file_name}: Cannot stitch file containing less than two pages.")
            continue

        max_page_width = max_page_height = total_pages_width = total_pages_height = 0
        pages_data = []
        for pdf_page in pdf_file.pages:  # calculate result page dimensions
            pages_data.append(pdf_page)
            width, height = pdf_page.mediabox.width, pdf_page.mediabox.height
            total_pages_width += width
            total_pages_height += height
            max_page_width = max(max_page_width, width)
            max_page_height = max(max_page_height, height)

        base_pdf_path_and_name = strip_ext(file_name)

        new_page = pypdf.PageObject.create_blank_page(width=max_page_width, height=total_pages_height)
        for index, pdf_page in enumerate(pages_data):
            new_page.merge_page(pdf_page, expand=True)
            if index != len(pages_data) - 1:
                new_page.add_transformation(pypdf.Transformation().translate(ty=pdf_page.mediabox.height))
        output = pypdf.PdfWriter()
        output.add_page(new_page)
        output.write(open(f"{base_pdf_path_and_name} !vertical.pdf", "wb"))

        new_page = pypdf.PageObject.create_blank_page(width=total_pages_width, height=max_page_height)
        for index, pdf_page in enumerate(pages_data[::-1]):
            new_page.merge_page(pdf_page, expand=True)
            if index != len(pages_data) - 1:
                new_page.add_transformation(pypdf.Transformation().translate(tx=pdf_page.mediabox.width))
        output = pypdf.PdfWriter()
        output.add_page(new_page)
        output.write(open(f"{base_pdf_path_and_name} !horizontal.pdf", "wb"))


def resave_files(path, sanitize=False):
    """Resave PDFs and images, stripping metadata and potentially reducing size."""
    # NOTE: To remove all PDF metadata, comment out the "NameObject("/Producer"):" line in pypdf\_writer.py
    results = ""
    for file_path in index_directory(path, ["jpeg", "jpg", "pdf", "png"]):
        org_size = os.path.getsize(file_path) / 1024

        if file_path.lower().endswith("pdf"):
            with open(file_path, "rb") as pdf:
                org = io.BytesIO(pdf.read())
            reader = pypdf.PdfReader(org)
            writer = pypdf.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            os.chmod(file_path, 0o777)
            os.remove(file_path)
            if sanitize:
                file_path = get_folder_path(file_path) + "document.pdf"
            with open(file_path, "wb") as pdf:
                writer.write(pdf)
        else:
            img = Image.open(file_path)
            img_without_metadata = Image.new(img.mode, img.size)
            img_without_metadata.putdata(list(img.getdata()))
            os.chmod(file_path, 0o777)
            os.remove(file_path)
            if sanitize:
                file_path = get_folder_path(file_path) + "image." + get_file_type(file_path)
            img_without_metadata.save(file_path)

        new_size = os.path.getsize(file_path) / 1024
        pct_chg = f"{round(((new_size - org_size) / org_size) * 100, 1)}%"
        results += file_path + " "
        results += f"{round(org_size, 1)} KB to {round(new_size, 1)} KB ({pct_chg})\n"

    label.setText(results)
    print(results)


def encrypt_pdf(path):
    """Encrypts all PDF files using user-inputted key."""
    encryption_key = retrieve_input_text()
    if not encryption_key:
        return
    for file_path in index_directory(path, "pdf"):
        with open(file_path, "rb") as input_file:
            pdf_reader = pypdf.PdfReader(input_file)
            encrypted_pdf = pypdf.PdfWriter()
            encrypted_pdf.append_pages_from_reader(pdf_reader)
            encrypted_pdf.encrypt(user_password=encryption_key)
        with open(f"{strip_ext(file_path)}_encrypted.pdf", "wb") as output_file:
            encrypted_pdf.write(output_file)


def save_page_range(path, start_page, end_page):
    """Saves a range of pages from each PDF file. Formats: '9-99' for pages 9 to 99, '-99' for 1 to 99, '99-' for 99 onwards, '99' for page 99 only."""
    range_input = retrieve_input_text()
    if not range_input:
        return
    range_input = range_input.split("-")
    print(range_input)
    if len(range_input) > 1:
        if (range_input[0] and int(range_input[0]) >= 0 and range_input[1] and int(range_input[1]) > 0):  # 9-99
            start_page = range_input[0]
            end_page = range_input[1]
        elif range_input[0] == "":  # -99
            start_page = 0
            end_page = range_input[1]
        elif range_input[1] == "":  # 99-
            start_page = range_input[0]
            end_page = -1
    else:  # 99
        start_page = end_page = range_input[0]

    for file_path in index_directory(path, "pdf"):
        if end_page == -1:
            with open(file_path, "rb") as f:
                end_page = pypdf.PdfReader(f)
                end_page = len(end_page.pages)
        start_page = int(start_page)
        end_page = int(end_page)
        writer = pypdf.PdfWriter()
        reader = pypdf.PdfReader(file_path)
        for page in range(start_page - 1, end_page):
            writer.add_page(reader.pages[page])
        with open(f"{path}\\{start_page}-{end_page} {get_file_name(file_path)}", "wb") as output_pdf:
            writer.write(output_pdf)


def pdf_to_image(path):
    """Converts PDF pages to individual PNG files."""
    file_paths = index_directory(path, "pdf")
    for file in file_paths:
        pdf_pages = convert_from_path(file, dpi=300, poppler_path=POPPLER_PATH)
        for page_num, pdf_page in enumerate(pdf_pages):
            pdf_page.save(f"{strip_ext(file)} {page_num}.png")  # append " {page_num}" to file name


def image_to_pdf(path):
    """Converts PNG and JPG files to individual PDFs."""
    for file_path in index_directory(path, file_types=["png", "jpg"]):
        img = Image.open(file_path)
        img.save(f"{strip_ext(file_path)}.pdf", "PDF", resolution=img.width / 850 * 100)


def sanitize(path):
    """Strips metadata and sets a generic name."""
    resave_files(path, True)


def crop_images(path):
    """Crops images based on predefined dimensions."""
    file_paths = index_directory(path, file_types=["png", "jpg"])
    crop_configs = {  # image cropping is handled case-by-casely
        (1280, 1080): [(0, 0, 1280, 720)], (2560, 720): [(0, 0, 1280, 720), (1280, 0, 2560, 720)],
        (3200, 1080): [(0, 0, 1920, 1080), (1920, 0, 3200, 1080)], }

    for file_path in file_paths:
        original_image = Image.open(file_path)
        crop_areas = crop_configs.get(original_image.size)
        if crop_areas is None:
            print(f"Configuration for {file_path} not set ({original_image.size})")
            continue

        for index, crop_area in enumerate(crop_areas, 1):
            cropped_image = original_image.crop(box=crop_area)
            cropped_image.save(f"{strip_ext(file_path)} !CROPPED {index}.{get_file_type(file_path)}")
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
    """Converts existing image files to a duplicate PNG or JPG format."""
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
        img.save(rf"{strip_ext(file_path)}.ico", sizes=[(256, 256), (128, 128)])


def print_metadata(path):
    """Prints out the metadata for all image and PDF files."""
    metadata_output = ""
    file_paths = index_directory(path, file_types=["jpeg", "jpg", "pdf", "png"])

    for index, file_path in enumerate(file_paths):
        metadata_output += echo_content(f"\n{index + 1}. {file_path}\n")

        if file_path.endswith((".png", ".jpg", ".jpeg")):
            img = Image.open(file_path)
            metadata_output += echo_content(
                f"\tWidth, Height, Size, Mode = ({img.width}, {img.height}) {img.format} {img.mode}\n")
            exif_data = img.getexif()

            for tag_id in exif_data:
                tag_name = str(ExifTags.TAGS.get(tag_id, tag_id))
                spaces = 25 - len(tag_name)
                metadata_output += echo_content(f"\t{tag_name + ' ' * spaces}: {exif_data.get(tag_id)}\n")

        elif file_path.endswith(".pdf"):
            with open(file_path, "rb") as f:
                pdf_reader = pypdf.PdfReader(f)
                metadata = pdf_reader.metadata
                if metadata:
                    for metadata_key in metadata:
                        metadata_output += echo_content(f"{metadata_key}: {metadata[metadata_key]}\n")
                else:
                    metadata_output += echo_content("No Metadata\n")

    label.setText(metadata_output)


def duplicate_detector(directory_path):
    """Scans a directory and identifies any duplicate files using MD5 hashing."""
    file_hashes = {}
    duplicates = []

    for root, subdirs, files in os.walk(directory_path):
        for filename in files:
            full_file_path = os.path.join(root, filename)

            with open(full_file_path, "rb") as file:
                file_content_hash = hashlib.md5(file.read()).hexdigest()

            if file_content_hash in file_hashes:
                duplicates.append((file_hashes[file_content_hash], full_file_path))
            else:
                file_hashes[file_content_hash] = full_file_path

    result_msg = ("Duplicate files found:\n" if any(duplicates) else "No duplicate files found.")
    for original, duplicate in duplicates:
        result_msg += f"\nOriginal: {original}\nDuplicate: {duplicate}\n"

    label.setText(result_msg)


def restart():
    """Restarts the program as a quick way to apply any code changes and detach from using files."""
    print(restart.__name__)
    python = sys.executable
    os.execl(python, python, *sys.argv)


def quit_clicked():
    """Quit button exits the program."""
    quit_box = QMessageBox()
    quit_box.setWindowTitle("Quit")
    quit_box.setText("Are you sure you want to quit?")
    quit_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    quit_box.setDefaultButton(QMessageBox.No)
    response = quit_box.exec_()

    if response == QMessageBox.Yes:
        sys.exit()


def index_directory(path, file_types):
    """Get the list of file names in the target directory"""
    if type(file_types) == list:  # convert file_types into a list
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


def echo_content(content):
    """Print the content and return it as a string"""
    print(content, end="")
    return content


def get_folder_path(path):
    """Get the file location from the path"""
    return os.path.dirname(path)


def get_file_name(path):
    """Get the file name including the extension from the path"""
    return os.path.basename(path)


def strip_ext(fname):
    """Strip the extension from the file name"""
    return os.path.splitext(fname)[0]


def get_file_type(path):
    """Get the file type from the path"""
    return path.split(".")[-1]


def retrieve_input_text():
    """Retrieve the text from the input box"""
    try:
        global input_text
        text_value = input_text
        return str(text_value)
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
    widget.setWindowTitle("PDF and Image Tool")

    # row 1
    program_button("Merge PDFs", 1, 1, lambda: merge_pdfs(PATH_TO_FOLDER))
    program_button("Stitch PDFs", 1, 2, lambda: stitch_pdfs(PATH_TO_FOLDER))
    program_button("Resave Files", 1, 3, lambda: resave_files(PATH_TO_FOLDER))
    program_button("Encrypt PDF", 1, 4, lambda: encrypt_pdf(PATH_TO_FOLDER))
    program_button("Save Page Range", 1, 5, lambda: save_page_range(PATH_TO_FOLDER, 0, 0))

    # row 2
    program_button("PDF to Image", 2, 1, lambda: pdf_to_image(PATH_TO_FOLDER))
    program_button("Image to PDF", 2, 2, lambda: image_to_pdf(PATH_TO_FOLDER))
    program_button("Sanitize", 2, 3, lambda: sanitize(PATH_TO_FOLDER))
    global input_text
    input_box(rowSpacing, colSpacing, buttonWidth, buttonHeight, colSpacingActual)

    # row 3
    program_button("Crop Images", 3, 1, lambda: crop_images(PATH_TO_FOLDER))
    program_button("Merge Images", 3, 2, lambda: merge_images(PATH_TO_FOLDER))
    program_button("Convert Images", 3, 3, lambda: convert_images(PATH_TO_FOLDER))
    program_button("Image to ICO", 3, 4, lambda: img_to_ico(PATH_TO_FOLDER))
    program_button("Print Metadata", 3, 5, lambda: print_metadata(PATH_TO_FOLDER))

    # row 4
    program_button("Duplicate Detector", 4, 1, lambda: duplicate_detector(PATH_TO_FOLDER))
    program_button("Restart", 4, 2, restart)
    program_button("Quit", 4, 3, quit_clicked)

    # bottom text
    layout = QVBoxLayout(widget)
    label = QLabel("Program Idle")
    spacer = QSpacerItem(10, 4 * rowSpacing, QSizePolicy.Minimum, QSizePolicy.Fixed)
    layout.addSpacerItem(spacer)
    layout.addWidget(label)
    label.move(0, 500)

    widget.show()
    app.exec_()
