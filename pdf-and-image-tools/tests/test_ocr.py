import os
import shutil
import sys

import pdf2image
import PIL.Image
import pytest
import pytesseract

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import core


ASSETS_DIR = "pdf-and-image-tools/tests/data/assets"
OUTPUT_DIR = "pdf-and-image-tools/tests/data/output"


def extract_numeric_text(image):
    ocr_configurations = [
        r"--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789",
        r"--oem 3 --psm 10 -c tessedit_char_whitelist=0123456789",
        r"--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789",
    ]
    for config in ocr_configurations:
        detected_text = pytesseract.image_to_string(image, config=config).strip()
        if detected_text:
            return detected_text
    return ""


@pytest.fixture(autouse=True)
def prepare_test_output_directory():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    yield


def ensure_tesseract_is_available():
    if not shutil.which("tesseract"):
        pytest.skip(
            "Tesseract OCR binary not found. Please ensure it is installed and available in your PATH."
        )


def populate_directory_with_test_pdfs(directory, file_count=10):
    os.makedirs(directory, exist_ok=True)
    for i in range(1, file_count + 1):
        source_path = os.path.join(ASSETS_DIR, f"test_{i:02d}.pdf")
        shutil.copy(source_path, directory)


def find_single_generated_file(directory, filename_prefix):
    matches = [f for f in os.listdir(directory) if f.startswith(filename_prefix)]
    assert len(matches) == 1
    return os.path.join(directory, matches[0])


def verify_pdf_pages_contain_sequential_numbers(pdf_path, expected_page_count):
    images = pdf2image.convert_from_path(pdf_path, dpi=300)
    assert len(images) == expected_page_count

    validation_errors = []
    for index, image in enumerate(images, start=1):
        detected_text = extract_numeric_text(image)
        expected_label = str(index)
        if detected_text != expected_label:
            validation_errors.append(
                f"Page {index}: Expected '{expected_label}', got '{detected_text}'"
            )

    if validation_errors:
        pytest.fail("\n".join(validation_errors))


def test_pdf_merging_and_ocr_verification():
    ensure_tesseract_is_available()

    merge_workspace = os.path.join(OUTPUT_DIR, "merge_test")
    populate_directory_with_test_pdfs(merge_workspace)

    core.merge_pdfs(merge_workspace)

    merged_pdf_path = find_single_generated_file(merge_workspace, "_merged_")
    verify_pdf_pages_contain_sequential_numbers(merged_pdf_path, expected_page_count=10)


def create_composite_pdf(output_path, page_numbers):
    writer = core.pypdf.PdfWriter()
    for num in page_numbers:
        source_pdf = os.path.join(ASSETS_DIR, f"test_{num:02d}.pdf")
        writer.add_page(core.pypdf.PdfReader(source_pdf).pages[0])
    with open(output_path, "wb") as output_file:
        writer.write(output_file)


@pytest.mark.parametrize(
    "range_expression, expected_labels",
    [
        ("2-4", ["2", "3", "4"]),
        ("5", ["5"]),
        ("-3", ["1", "2", "3"]),
        ("8-", ["8", "9", "10"]),
    ],
)
def test_pdf_page_range_extraction_variants(range_expression, expected_labels):
    range_workspace = os.path.join(
        OUTPUT_DIR, f"range_{range_expression.replace('-', 'to')}"
    )
    os.makedirs(range_workspace, exist_ok=True)

    source_pdf_path = os.path.join(range_workspace, "multi.pdf")
    create_composite_pdf(source_pdf_path, range(1, 11))

    core.input_text = range_expression
    core.save_page_range(range_workspace, 0, 0)

    result_pdf_path = find_single_generated_file(range_workspace, "_range_")
    result_images = pdf2image.convert_from_path(result_pdf_path, dpi=300)

    assert len(result_images) == len(expected_labels)
    for i, expected_text in enumerate(expected_labels):
        detected_text = extract_numeric_text(result_images[i])
        assert expected_text in detected_text


def test_pdf_stitching_functionality():
    stitch_workspace = os.path.join(OUTPUT_DIR, "stitch_test")
    os.makedirs(stitch_workspace, exist_ok=True)

    input_pdf_path = os.path.join(stitch_workspace, "to_stitch.pdf")
    create_composite_pdf(input_pdf_path, [1, 2])

    core.stitch_pdfs(stitch_workspace)

    vertical_stitch_path = find_single_generated_file(stitch_workspace, "_v_stitch_")
    stitched_images = pdf2image.convert_from_path(vertical_stitch_path, dpi=300)

    assert len(stitched_images) == 1

    ocr_config = r"--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789"
    page_text = pytesseract.image_to_string(stitched_images[0], config=ocr_config)

    assert "1" in page_text
    assert "2" in page_text


def test_batch_file_renaming_logic():
    rename_workspace = os.path.join(OUTPUT_DIR, "rename_test")
    populate_directory_with_test_pdfs(rename_workspace, file_count=3)

    core.input_text = "newname"
    core.rename_files(rename_workspace)

    final_files = sorted(os.listdir(rename_workspace))
    assert "_newname-01.pdf" in final_files
    assert "_newname-02.pdf" in final_files
    assert "_newname-03.pdf" in final_files


def test_auto_cropping_logic():
    workspace = os.path.join(OUTPUT_DIR, "auto_crop_test")
    os.makedirs(workspace, exist_ok=True)

    canvas_size = (200, 200)
    background_color = (255, 255, 255)
    foreground_color = (0, 0, 0)

    image = PIL.Image.new("RGB", canvas_size, background_color)
    for x in range(50, 150):
        for y in range(50, 150):
            image.putpixel((x, y), foreground_color)

    source_image_path = os.path.join(workspace, "to_crop.png")
    image.save(source_image_path)

    core.crop_solid_edges(workspace)

    cropped_image_path = find_single_generated_file(workspace, "_auto_crop_")
    with PIL.Image.open(cropped_image_path) as cropped_image:
        assert 95 <= cropped_image.width <= 105
        assert 95 <= cropped_image.height <= 105


def test_svg_and_webp_conversion():
    workspace = os.path.join(OUTPUT_DIR, "svg_webp_test")
    os.makedirs(workspace, exist_ok=True)

    svg_content = '<svg width="100" height="100"><rect width="100" height="100" fill="blue" /></svg>'
    svg_path = os.path.join(workspace, "test.svg")
    with open(svg_path, "w") as svg_file:
        svg_file.write(svg_content)

    core.convert_svg_and_webp_to_png(workspace)

    png_output_path = os.path.join(workspace, "test.png")
    assert os.path.exists(png_output_path)
    assert os.path.getsize(png_output_path) > 0


def test_duplicate_detection_logic():
    workspace = os.path.join(OUTPUT_DIR, "duplicate_test")
    os.makedirs(workspace, exist_ok=True)

    identical_content = b"standard content for duplication test"
    file_one = os.path.join(workspace, "file1.txt")
    file_two = os.path.join(workspace, "file2.txt")
    with open(file_one, "wb") as f:
        f.write(identical_content)
    with open(file_two, "wb") as f:
        f.write(identical_content)

    unique_file = os.path.join(workspace, "unique.txt")
    with open(unique_file, "wb") as f:
        f.write(b"completely different content")

    class StatusCapturer:
        def __init__(self):
            self.captured_text = ""

        def setText(self, text):
            self.captured_text = text

    capturer = StatusCapturer()
    original_status_field = core.status_field
    core.status_field = capturer

    try:
        core.duplicate_detector(workspace)
        assert "Duplicate files found" in capturer.captured_text
        assert "file1.txt" in capturer.captured_text
        assert "file2.txt" in capturer.captured_text
        assert "unique.txt" not in capturer.captured_text
    finally:
        core.status_field = original_status_field


def test_pdf_encryption_and_decryption():
    workspace = os.path.join(OUTPUT_DIR, "encryption_test")
    os.makedirs(workspace, exist_ok=True)

    target_pdf_path = os.path.join(workspace, "source.pdf")
    create_composite_pdf(target_pdf_path, [1])

    test_password = "secure_test_password"
    core.input_text = test_password
    core.encrypt_pdf(workspace)

    encrypted_pdf_path = find_single_generated_file(workspace, "_encrypted_")

    reader = core.pypdf.PdfReader(encrypted_pdf_path)
    assert reader.is_encrypted
    assert reader.decrypt(test_password)


if __name__ == "__main__":
    try:
        print("Running: test_pdf_merging_and_ocr_verification...")
        test_pdf_merging_and_ocr_verification()

        print("Running: test_pdf_page_range_extraction_variants...")
        test_pdf_page_range_extraction_variants("2-4", ["2", "3", "4"])

        print("Running: test_pdf_stitching_functionality...")
        test_pdf_stitching_functionality()

        print("Running: test_batch_file_renaming_logic...")
        test_batch_file_renaming_logic()

        print("Running: test_auto_cropping_logic...")
        test_auto_cropping_logic()

        print("Running: test_svg_and_webp_conversion...")
        test_svg_and_webp_conversion()

        print("Running: test_duplicate_detection_logic...")
        test_duplicate_detection_logic()

        print("Running: test_pdf_encryption_and_decryption...")
        test_pdf_encryption_and_decryption()

        print("\nAll available tests PASSED successfully!")
    except Exception as error:
        print(f"\nTests FAILED: {error}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
