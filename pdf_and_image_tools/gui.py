import json
import os
import sys

import PyQt5.QtCore
import PyQt5.QtWidgets

import core as c

# Configuration Management
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "pdf_img_tools_settings.json")
widget = None
status_field = None
current_input_value = ""
target_directory = ""

# UI Constants
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 30
SPACING = 20
COL_SPACING = BUTTON_WIDTH + SPACING
ROW_SPACING = BUTTON_HEIGHT + SPACING

COLOR_CODES = {"PDF": "#ffaaaa", "Image": "#aaffaa", "Any": "#aaaaff", "Settings": "#aaaaaa"}


# Input Handling
def get_input():
    global current_input_value
    return str(current_input_value) if current_input_value else False


def input_box(row_spacing, col_spacing, col_spacing_actual):
    global widget, current_input_value

    def update_input_value(text):
        global current_input_value
        current_input_value = text
        c.input_text = text

    box = PyQt5.QtWidgets.QLineEdit(widget)
    box.textChanged.connect(update_input_value)
    x = (3 - 1) * col_spacing
    y = (2 - 1) * row_spacing
    box.move(x, y)
    box.resize(BUTTON_WIDTH * 2 + col_spacing_actual, BUTTON_HEIGHT)
    labels = PyQt5.QtWidgets.QFormLayout()
    labels.addRow("Input Box: ", box)
    box.show()


# UI Element Creation
def create_button(label, row, col, action, button_type):
    global widget
    bg_color = COLOR_CODES.get(button_type, "#aaaaaa")
    button = PyQt5.QtWidgets.QPushButton(widget)
    button.setText(label)
    button.clicked.connect(action)
    button.setStyleSheet(f"background-color: {bg_color}; color: black;")
    button.move((col - 1) * COL_SPACING, (row - 1) * ROW_SPACING)
    button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
    button.show()


def create_color_legend_widget():
    key_widget = PyQt5.QtWidgets.QGroupBox("Color Key")
    layout = PyQt5.QtWidgets.QHBoxLayout()
    for description, color in COLOR_CODES.items():
        label = PyQt5.QtWidgets.QLabel(description)
        label.setStyleSheet(f"background-color: {color}; color: black; font-family: Helvetica; font-size: 10pt;")
        label.setAlignment(PyQt5.QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
    key_widget.setLayout(layout)
    key_widget.setFixedHeight(50)
    key_widget.setFixedWidth(200)
    return key_widget


# Persistent Directory Storage
def load_last_dir():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            data = json.load(f)
            return data.get("last_dir", "")
    return ""


def save_last_dir(path):
    with open(CONFIG_PATH, "w") as f:
        json.dump({"last_dir": path}, f)


# Main Application Setup
def run_app():
    global widget, status_field, current_input_value, target_directory
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    widget = PyQt5.QtWidgets.QWidget()
    widget.setWindowTitle("PDF and Image Tools")

    fixed_width = 5 * COL_SPACING - SPACING
    desired_height = 8 * ROW_SPACING - SPACING
    widget.setMinimumWidth(fixed_width)
    widget.setMaximumWidth(fixed_width)
    widget.setMinimumHeight(desired_height)
    widget.resize(fixed_width, desired_height)

    # PDF Operations
    create_button("Merge PDFs", 1, 1, lambda: c.merge_pdfs(target_directory), "PDF")
    create_button("Stitch PDFs", 1, 2, lambda: c.stitch_pdfs(target_directory), "PDF")
    create_button("Encrypt PDF", 1, 3, lambda: c.encrypt_pdf(target_directory), "PDF")
    create_button("Save Page Range", 1, 4, lambda: c.save_page_range(target_directory, 0, 0), "PDF")
    create_button("PDF to Image", 2, 1, lambda: c.pdf_to_image(target_directory), "PDF")
    create_button("Enhance Contrast", 2, 2, lambda: c.enhance_contrast(target_directory), "PDF")

    # Image Operations
    create_button("Crop Images", 3, 1, lambda: c.crop_images(target_directory), "Image")
    create_button("Merge Images", 3, 2, lambda: c.merge_images(target_directory), "Image")
    create_button("Convert PNG ↔️ JPG", 3, 3, lambda: c.convert_between_png_jpg(target_directory), "Image")
    create_button("Image to ICO", 3, 4, lambda: c.img_to_ico(target_directory), "Image")
    create_button("Image to PDF", 4, 1, lambda: c.image_to_pdf(target_directory), "Image")
    create_button("Get Image Colors", 4, 2, lambda: c.get_image_colors(target_directory), "Image")
    create_button("Crop by 90%", 4, 3, lambda: c.crop_by_90(target_directory), "Image")
    create_button("SVG WEBP to PNG", 4, 4, lambda: c.convert_svg_and_webp_to_png(target_directory), "Image")
    create_button("Crop Solid Edges", 5, 4, lambda: c.crop_solid_edges(target_directory), "Image")

    # General File Operations
    create_button("Resave Files", 1, 5, lambda: c.resave_files(target_directory), "Any")
    create_button("Sanitize", 2, 5, lambda: c.sanitize(target_directory), "Any")
    create_button("Print Info", 3, 5, lambda: c.print_info(target_directory), "Any")
    create_button("Rename Files", 4, 5, lambda: c.rename_files(target_directory), "Any")
    create_button("Duplicate Detector", 5, 5, lambda: c.duplicate_detector(target_directory), "Any")

    # Program Controls
    create_button("Restart", 5, 1, c.restart_program, "Settings")
    create_button("Quit", 5, 2, c.exit_program, "Settings")

    # Input Box and Layout
    input_box(ROW_SPACING, COL_SPACING, SPACING)
    layout = PyQt5.QtWidgets.QVBoxLayout(widget)

    last_dir = load_last_dir()
    target_directory = last_dir if last_dir else c.ensure_folder("")

    status_field = PyQt5.QtWidgets.QTextEdit("Program Idle")
    c.status_field = status_field

    dir_input = PyQt5.QtWidgets.QLineEdit()
    dir_input.setText(target_directory)
    dir_input.setPlaceholderText("Target Directory")
    dir_input.setFixedWidth(300)

    def update_dir(text):
        global target_directory
        target_directory = text
        save_last_dir(text)
        if status_field is not None:
            status_field.setText(f"Target directory changed to: {text}")

    dir_input.textChanged.connect(update_dir)

    color_key_widget = create_color_legend_widget()

    dir_row_layout = PyQt5.QtWidgets.QHBoxLayout()
    dir_row_layout.addWidget(dir_input)
    dir_row_layout.addStretch()
    dir_row_layout.addWidget(color_key_widget)

    spacer = PyQt5.QtWidgets.QSpacerItem(10, 5 * ROW_SPACING, PyQt5.QtWidgets.QSizePolicy.Minimum,
                                         PyQt5.QtWidgets.QSizePolicy.Fixed, )
    layout.addSpacerItem(spacer)
    layout.addWidget(status_field)
    layout.addLayout(dir_row_layout)

    widget.setLayout(layout)
    widget.show()
    app.exec_()
