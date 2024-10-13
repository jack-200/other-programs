import collections
import hashlib
import io
import os
import sys

try:
    import cairosvg
except (ModuleNotFoundError, OSError) as e:
    print("Package CairoSVG is not installed. Cannot convert SVG files to PNG.")
    is_cairosvg_installed = False

try:
    import img2pdf
except (ModuleNotFoundError) as e:
    print("Package img2pdf is not installed. Cannot enhance contrast of PDFs.")
    is_img2pdf_installed = False

import numpy
import pypdf
from PIL import ExifTags, Image, ImageEnhance
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QFormLayout, QTextEdit, QLineEdit, QMessageBox, QPushButton, 
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget, QGroupBox, QLabel, QGridLayout
)
from pdf2image import convert_from_path

PATH_TO_FOLDER = r""
POPPLER_PATH = r""

def ensure_folder(source_path):
    # Set default path if not specified and create folder if it doesn't exist
    if source_path == "":
        source_path = os.path.join(os.path.expanduser("~"), "Downloads", "PDF-IMG")
        print(f"Path to folder not specified. Using default path: {source_path}")

    if not os.path.exists(source_path):
        os.makedirs(source_path)
        print(f"Folder created at: {source_path}")

    return source_path


def merge_pdfs(dir_path):
    """Combines all PDFs in the directory into one PDF file."""

    # Get all PDF files, and append them to the merger
    merger = pypdf.PdfMerger()
    pdf_files = index_directory(dir_path, "pdf")
    for pdf_file in pdf_files:
        merger.append(pdf_file)

    # Define result file name, write the merged PDFs to it, close the merger, and update status
    result_pdf_path = f"{dir_path}\\!merged_{get_file_name(pdf_files[0])}"
    merger.write(result_pdf_path)
    merger.close()
    statusField.setText(f"\nMerge PDF Result: {result_pdf_path}")


def stitch_pdfs(dir_path):
    """Stitches all PDF pages into one, creating vertical and horizontal versions."""

    # Iterate over all PDF files in the directory
    for file_name in index_directory(dir_path, "pdf"):
        pdf_file = pypdf.PdfReader(open(file_name, "rb"))

        # Skip files with less than two pages
        if len(pdf_file.pages) < 2:
            print(f"Skipped {file_name}: Cannot stitch file containing less than two pages.")
            continue

        # Initialize variables for page dimensions
        max_width = max_height = total_width = total_height = 0
        pages = []

        # Calculate result page dimensions
        for page in pdf_file.pages:
            pages.append(page)
            width, height = page.mediabox.width, page.mediabox.height
            total_width += width
            total_height += height
            max_width = max(max_width, width)
            max_height = max(max_height, height)

        base_path_and_name = strip_ext(file_name)

        # Create and write vertical stitched PDF
        vertical_pdf = pypdf.PageObject.create_blank_page(width=max_width, height=total_height)
        for i, page in enumerate(pages):
            vertical_pdf.merge_page(page, expand=True)
            if i != len(pages) - 1:
                vertical_pdf.add_transformation(pypdf.Transformation().translate(ty=page.mediabox.height))
        output = pypdf.PdfWriter()
        output.add_page(vertical_pdf)
        output.write(open(f"{base_path_and_name}_vertical.pdf", "wb"))

        # Create and write horizontal stitched PDF
        horizontal_pdf = pypdf.PageObject.create_blank_page(width=total_width, height=max_height)
        for i, page in enumerate(pages[::-1]):
            horizontal_pdf.merge_page(page, expand=True)
            if i != len(pages) - 1:
                horizontal_pdf.add_transformation(pypdf.Transformation().translate(tx=page.mediabox.width))
        output = pypdf.PdfWriter()
        output.add_page(horizontal_pdf)
        output.write(open(f"{base_path_and_name}_horizontal.pdf", "wb"))


def encrypt_pdf(dir_path):
    """Encrypts PDFs in the directory with the user-provided key."""

    # Retrieve encryption key and validate
    encryption_key = get_input()
    if not encryption_key: return

    # Process each PDF file in the directory
    for pdf_path in index_directory(dir_path, "pdf"):
        # Read and encrypt the PDF, then write to a new file
        with open(pdf_path, "rb") as pdf_file, pypdf.PdfReader(pdf_file) as reader:
            writer = pypdf.PdfWriter()
            writer.append_pages_from_reader(reader)
            writer.encrypt(user_password=encryption_key)

            with open(f"{strip_ext(pdf_path)}_encrypted.pdf", "wb") as encrypted_pdf:
                writer.write(encrypted_pdf)


def save_page_range(path, start_page, end_page):
    """Saves a range of pages from each PDF file. Formats: '9-99' for pages 9 to 99, '-99' for 1 to 99, '99-' for 99 onwards, '99' for page 99 only."""
    range_input = get_input()
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


def resave_files(path, sanitize=False):
    """Resave PDFs and images, stripping metadata and potentially reducing size."""
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
                file_path = os.path.join(get_folder_path(file_path), "document.pdf")

            # Clear the metadata
            writer._info = pypdf.generic.DictionaryObject()

            with open(file_path, "wb") as pdf:
                writer.write(pdf)
        else:
            img = Image.open(file_path)
            img_without_metadata = img.copy()
            os.chmod(file_path, 0o777)
            os.remove(file_path)
            if sanitize:
                file_path = (get_folder_path(file_path) + r"\image." + get_file_type(file_path))
            img_without_metadata.save(file_path)

        new_size = os.path.getsize(file_path) / 1024
        pct_chg = f"{round(((new_size - org_size) / org_size) * 100, 1)}%"
        results += file_path + " "
        results += f"{round(org_size, 1)} KB to {round(new_size, 1)} KB ({pct_chg})\n"

    statusField.setText(results)
    print(results)


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


def input_box(row_spacing, col_spacing, button_width, button_height, col_spacing_actual):
    """The content of the input box will be used in certain functions"""

    def update_input_text(text):
        global input_text
        input_text = text

    box = QLineEdit(widget)
    box.textChanged.connect(update_input_text)
    x = (3 - 1) * col_spacing
    y = (2 - 1) * row_spacing
    box.move(x, y)
    box.resize(button_width * 2 + col_spacing_actual, button_height)
    labels = QFormLayout()
    labels.addRow("Input Box: ", box)
    box.show()


def sanitize(path):
    """Strips metadata and sets a generic file name."""
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
        statusField.setText("Failed to merge images: need more than one image to merge")
        return

    imgs = []
    total_width = total_height = max_width = max_height = 0

    # Load images, calculate total and max dimensions
    for file_path in file_paths:
        img = Image.open(file_path)
        imgs.append(img)
        width, height = img.size
        total_width += width
        total_height += height
        max_width = max(max_width, width)
        max_height = max(max_height, height)

    # Convert images to RGB and then to arrays for stacking
    v_scaled_imgs = [numpy.array(img.convert('RGB').resize((max_width, round(max_width / img.width * img.height)))) for
                     img in imgs]
    h_scaled_imgs = [numpy.array(img.convert('RGB').resize((round(max_height / img.height * img.width), max_height)))
                     for img in imgs]

    # Combine images vertically and horizontally, then save
    v_imgs_comb = numpy.vstack(v_scaled_imgs)
    Image.fromarray(v_imgs_comb).save(f"{path}\\!vertical.png")
    Image.fromarray(v_imgs_comb).convert("RGB").save(f"{path}\\!vertical.jpg")

    h_imgs_comb = numpy.hstack(h_scaled_imgs)
    Image.fromarray(h_imgs_comb).save(f"{path}\\!horizontal.png")
    Image.fromarray(h_imgs_comb).convert("RGB").save(f"{path}\\!horizontal.jpg")


def convert_between_png_jpg(directory):
    """Converts existing image files to a duplicate PNG or JPG format."""
    for image_path in get_all_images(directory):
        file_type = get_file_type(image_path)
        new_file_path = strip_ext(image_path)
        if file_type == "png":
            Image.open(image_path).convert("RGB").save(f"{new_file_path}.jpg")
        else:
            Image.open(image_path).save(f"{new_file_path}.png")


def img_to_ico(path):
    """Converts image files to ICO format"""
    for file_path in get_all_images(path):
        img = Image.open(file_path)
        img.save(f"{strip_ext(file_path)}.ico")


def print_info(directory):
    """Prints out the size and metadata for all image and PDF files."""
    output = ""
    files = index_directory(directory, file_types=["jpeg", "jpg", "pdf", "png"])

    for index, path in enumerate(files):
        size = os.path.getsize(path)
        formatted_size = "{:,}".format(size)

        # Determine file size in bytes, KB, or MB
        if size < 1024 * 1024:  # Less than 1 MB
            size_str = f"{formatted_size} bytes ({size / 1024:.2f} KB)"
        else:
            size_str = f"{formatted_size} bytes ({size / (1024 * 1024):.2f} MB)"

        output += f"\n{index + 1}. {path}\n\tFile Size: {size_str}"

        # Handle image files: get size, mode, format, and EXIF data
        if path.endswith((".png", ".jpg", ".jpeg")):
            img = Image.open(path)
            output += f"\tWidth, Height, Mode = ({img.width}, {img.height}, {img.mode}) {img.format}\n"
            for tag_id, value in img.getexif().items():
                tag = str(ExifTags.TAGS.get(tag_id, tag_id))
                output += f"\t{tag.ljust(25)}: {value}\n"

        # Handle PDF files: get and output metadata
        elif path.endswith(".pdf"):
            with open(path, "rb") as f:
                pdf = pypdf.PdfReader(f)
                metadata = pdf.metadata or {}
                for key, value in metadata.items():
                    output += f"\t{key}: {value}\n"

    statusField.setText(output.lstrip('\n'))


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

    statusField.setText(result_msg)


def get_image_colors(directory_path):
    """Get the average color and most common colors of all images in the directory."""

    # Initialize results
    results = []

    # Open image and get colors
    for full_file_path in index_directory(directory_path, file_types=["jpeg", "jpg", "png"]):
        img = Image.open(full_file_path)
        if img.mode == 'RGBA':
            colors = [pixel[:3] for pixel in img.getdata() if pixel[3] == 255]
        else:
            colors = [pixel[:3] for pixel in img.getdata()]

        # Calculate average color and convert to hex
        avg_color = numpy.mean(colors, axis=0)
        avg_color_hex = "#%02x%02x%02x" % (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))

        # Get most common colors and convert to hex
        color_counter = collections.Counter(colors)
        common_colors = color_counter.most_common(3)
        common_colors_hex = [(("#%02x%02x%02x" % (color[0][0], color[0][1], color[0][2])), color[1]) for color in
                             common_colors]

        # Format results and add to the list
        avg_color_str = f"Average color: {avg_color_hex}"
        common_colors_str = "\n".join([f"Color: {color[0]}, Frequency: {color[1]}" for color in common_colors_hex])
        results.append(f"Filename: {full_file_path}\n" + avg_color_str + "\n" + common_colors_str)

    # Set the text field with all results
    statusField.setText("\n\n".join(results))


def crop_by_90(directory_path):
    """Crops images by 90% of their dimensions, removing the outer parts of the image."""
    for full_file_path in index_directory(directory_path, file_types=["jpeg", "jpg", "png"]):
        img = Image.open(full_file_path)
        width, height = img.size
        new_width = round(width * 0.9)
        new_height = round(height * 0.9)
        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2
        img_cropped = img.crop((left, top, right, bottom))
        img_cropped.save(f"{strip_ext(full_file_path)} !CROPPED 90.{get_file_type(full_file_path)}")


def convert_svg_and_webp_to_png(directory_path):
    """Converts SVG and WEBP files to PNG format."""
    for full_file_path in index_directory(directory_path, file_types=["svg", "webp"]):
        output_path = f"{strip_ext(full_file_path)}.png"

        if full_file_path.endswith('.svg'):
            if not is_cairosvg_installed:
                print("Package CairoSVG is not installed. Cannot convert SVG files to PNG.")
                continue
            cairosvg.svg2png(url=full_file_path, write_to=output_path)
            print(f"Converted {full_file_path} from SVG to PNG.")
        elif full_file_path.endswith('.webp'):
            img = Image.open(full_file_path)
            img.save(output_path, "PNG")
            print(f"Converted {full_file_path} from WEBP to PNG.")


def enhance_contrast(dir_path):
    """Enhance the contrast of a PDF by 25%."""
    if not is_img2pdf_installed:
        print("Package img2pdf is not installed. Cannot enhance contrast of PDFs.")
        return

    # Get all PDF paths and initialize enhanced images list
    pdf_paths = index_directory(dir_path, "pdf")

    for path in pdf_paths:
        enhanced_images = []

        # Convert PDF to images and enhance contrast
        for image in convert_from_path(path, poppler_path=POPPLER_PATH):
            enhanced_image = ImageEnhance.Contrast(image).enhance(1.25)

            # Save the enhanced image in JPEG format to a BytesIO object
            byte_io = io.BytesIO()
            enhanced_image.save(byte_io, format='JPEG')
            enhanced_images.append(byte_io.getvalue())

        # Define output path, convert enhanced images back to PDF and save
        output_path = f"{strip_ext(path)}_inc_contrast.pdf"
        with open(output_path, "wb") as file:
            file.write(img2pdf.convert(enhanced_images))

        print(f"Contrast enhanced PDF saved to: {output_path}")


def rename_files(directory_path):
    """Rename all files in a directory with a specified base name and sequential numbering."""
    new_name = get_input()
    if not new_name:
        return

    # Get all files in the directory
    file_paths = index_directory(directory_path)

    # Rename files
    for index, file_path in enumerate(file_paths):
        new_file_path = f"{directory_path}\\{new_name}-{index + 1}.{get_file_type(file_path)}"
        os.rename(file_path, new_file_path)

    print(f"Files renamed to {new_name}-1, {new_name}-2, etc.")


def restart_program():
    """Restarts the program to apply code changes and detach from file usage."""

    # Get the current Python executable and restart the program with the same arguments
    python_executable = sys.executable
    os.execl(python_executable, python_executable, *sys.argv)


def quit():
    """Handle quit button click event."""
    confirmation_dialog = QMessageBox()
    confirmation_dialog.setWindowTitle("Quit")
    confirmation_dialog.setText("Are you sure you want to quit?")
    confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    confirmation_dialog.setDefaultButton(QMessageBox.No)

    if confirmation_dialog.exec_() == QMessageBox.Yes:
        sys.exit()


def index_directory(path, file_types=None):
    """Get the list of file names in the target directory. Defaults to all file types if none specified."""
    if file_types is None or file_types == '*':  # No filtering by file type
        file_types_filter = False
    else:
        if type(file_types) == list:  # convert file_types into a list
            file_types = [f".{i.lower()}" for i in file_types]
        else:
            file_types = [f".{file_types.lower()}"]
        file_types_filter = True

    file_paths = []
    for subdir, dirs, files in os.walk(path):
        for file in files:
            if file_types_filter:
                file_type = f".{file.split('.')[-1].lower()}"
                if file_type in file_types:  # filter by file type
                    file_paths.append(os.path.join(subdir, file))
            else:
                file_paths.append(os.path.join(subdir, file))  # Add all files if no file type filtering

    print(f"\n{path}: {len(file_paths)} file(s)")
    if file_types_filter:
        print(f"Filtered by file type {file_types}")
    for count, file_name in enumerate(file_paths):
        print(f"{count + 1}. {file_name}")
    return file_paths


def get_all_images(directory_path):
    """Get all image files in the directory and its subdirectories."""
    image_extensions = (".png", ".jpg", ".jpeg")
    image_files = [os.path.join(root, file) for root, _, files in os.walk(directory_path) for file in files if
                   os.path.splitext(file)[1].lower() in image_extensions]
    return image_files


def create_button(label, row, col, action, button_type):
    """Create a button with specified label, position, size, action, and color based on button type."""
    global colors_codes

    # Determine button background color based on its type
    bg_color = colors_codes.get(button_type, "#aaaaaa")

    # Create button, set text, connect action, and style with CSS
    button = QPushButton(widget)
    button.setText(label)
    button.clicked.connect(action)
    button.setStyleSheet(f"background-color: {bg_color}; color: black;")

    # Position, size, and display the button
    button.move((col - 1) * col_spacing, (row - 1) * row_spacing)
    button.setFixedSize(btn_width, btn_height)
    button.show()


def create_key(widget, key_row, key_col):
    # Define constants and initialize variables
    global colors_codes
    key_width, key_height = 150, 70
    row, col = 0, 0

    # Setup group box with grid layout
    groupBox = QGroupBox("Color Key", widget)
    groupBox.move(round((key_col - 1) * col_spacing), round((key_row - 1) * row_spacing * 0.9))
    groupBox.setFixedSize(key_width, key_height)
    grid = QGridLayout()
    groupBox.setLayout(grid)

    # Populate grid with color code labels
    for description, color in colors_codes.items():
        label = QLabel(description)
        label.setStyleSheet(f"background-color: {color}; color: black; font-family: Helvetica; font-size: 10pt;")
        label.setAlignment(Qt.AlignCenter)
        grid.addWidget(label, row, col)
        col = (col + 1) % 2
        if col == 0:
            row += 1

    groupBox.show()


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


def strip_ext(filename):
    """Strip the extension from the file name"""
    return os.path.splitext(filename)[0]


def get_file_type(path):
    """Get the file type from the path"""
    return path.split(".")[-1]


def get_input():
    """Attempt to retrieve the text, return False if not defined"""
    try:
        return str(input_text)
    except NameError:
        return False


if __name__ == "__main__":
    # Setup application and widget
    app = QApplication(sys.argv)
    widget = QWidget()
    widget.setWindowTitle("PDF and Image Tools")

    PATH_TO_FOLDER = ensure_folder(PATH_TO_FOLDER)

    # Define button and spacing dimensions
    btn_width, btn_height = 120, 30
    spacing = 20
    row_spacing = btn_height + spacing
    col_spacing = btn_width + spacing
    colors_codes = {"PDF": "#ffaaaa", "Image": "#aaffaa", "Any": "#aaaaff", "Settings": "#aaaaaa"}

    # Resize widget
    widget.resize(5 * col_spacing - spacing, 8 * row_spacing - spacing)

    # PDF Operations
    create_button("Merge PDFs", 1, 1, lambda: merge_pdfs(PATH_TO_FOLDER), "PDF")
    create_button("Stitch PDFs", 1, 2, lambda: stitch_pdfs(PATH_TO_FOLDER), "PDF")
    create_button("Encrypt PDF", 1, 3, lambda: encrypt_pdf(PATH_TO_FOLDER), "PDF")
    create_button("Save Page Range", 1, 4, lambda: save_page_range(PATH_TO_FOLDER, 0, 0), "PDF")
    create_button("PDF to Image", 2, 1, lambda: pdf_to_image(PATH_TO_FOLDER), "PDF")
    create_button("Enhance Contrast", 2, 2, lambda: enhance_contrast(PATH_TO_FOLDER), "PDF")

    # Image Operations
    create_button("Crop Images", 3, 1, lambda: crop_images(PATH_TO_FOLDER), "Image")
    create_button("Merge Images", 3, 2, lambda: merge_images(PATH_TO_FOLDER), "Image")
    create_button("Convert PNG ↔️ JPG", 3, 3, lambda: convert_between_png_jpg(PATH_TO_FOLDER), "Image")
    create_button("Image to ICO", 3, 4, lambda: img_to_ico(PATH_TO_FOLDER), "Image")
    create_button("Image to PDF", 4, 1, lambda: image_to_pdf(PATH_TO_FOLDER), "Image")
    create_button("Get Image Colors", 4, 2, lambda: get_image_colors(PATH_TO_FOLDER), "Image")
    create_button("Crop by 90%", 4, 3, lambda: crop_by_90(PATH_TO_FOLDER), "Image")
    create_button("SVG WEBP to PNG", 4, 4, lambda: convert_svg_and_webp_to_png(PATH_TO_FOLDER), "Image")

    # General File Operations
    create_button("Resave Files", 1, 5, lambda: resave_files(PATH_TO_FOLDER), "Any")
    create_button("Sanitize", 2, 5, lambda: sanitize(PATH_TO_FOLDER), "Any")
    create_button("Print Info", 3, 5, lambda: print_info(PATH_TO_FOLDER), "Any")
    create_button("Rename Files", 4, 5, lambda: rename_files(PATH_TO_FOLDER), "Any")
    create_button("Duplicate Detector", 5, 5, lambda: duplicate_detector(PATH_TO_FOLDER), "Any")

    # Program Controls
    create_button("Restart", 5, 1, restart_program, "settings")
    create_button("Quit", 5, 2, quit, "settings")
    create_key(widget, 5, 3.5)

    # Setup input box and layout
    input_box(row_spacing, col_spacing, btn_width, btn_height, spacing)
    layout = QVBoxLayout(widget)
    statusField = QTextEdit("Program Idle")
    spacer = QSpacerItem(10, 5 * row_spacing, QSizePolicy.Minimum, QSizePolicy.Fixed)
    layout.addSpacerItem(spacer)
    layout.addWidget(statusField)

    # Show widget and execute application
    widget.show()
    app.exec_()
