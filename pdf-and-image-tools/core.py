import hashlib
import io
import os
import shutil
import sys

try:
    import cairosvg
except (ModuleNotFoundError, OSError):
    cairosvg = None

try:
    import img2pdf
except ModuleNotFoundError:
    img2pdf = None

import numpy
import pypdf
import PIL.ExifTags
import PIL.Image
import PIL.ImageEnhance
import pdf2image




class DummyStatusField:
    def setText(self, text):
        pass


status_field = DummyStatusField()
input_text = ""


def ensure_folder(source_path):
    if source_path == "":
        source_path = os.path.join(os.path.expanduser("~"), "Downloads", "PDF-IMG")
    if not os.path.exists(source_path):
        os.makedirs(source_path)
    return source_path


def merge_pdfs(dir_path):
    writer = pypdf.PdfWriter()
    pdf_files = index_directory(dir_path, "pdf")
    if not pdf_files:
        if status_field:
            status_field.setText("No PDF files found to merge.")
        return
    for pdf_file in pdf_files:
        reader = pypdf.PdfReader(pdf_file)
        for page in range(len(reader.pages)):
            writer.add_page(reader.pages[page])
    result_pdf_path = os.path.join(dir_path, f"!merged_{get_file_name(pdf_files[0])}")
    with open(result_pdf_path, "wb") as output_pdf:
        writer.write(output_pdf)
    if status_field:
        status_field.setText(f"\nMerge PDF Result: {result_pdf_path}")


def stitch_pdfs(dir_path):
    for file_name in index_directory(dir_path, "pdf"):
        with open(file_name, "rb") as pdf_in:
            pdf_file = pypdf.PdfReader(pdf_in)
            if len(pdf_file.pages) < 2:
                if status_field:
                    status_field.setText(f"Skipping {file_name}: less than 2 pages.")
                continue
            max_width = max_height = total_width = total_height = 0
            pages = []
            for page in pdf_file.pages:
                pages.append(page)
                width, height = page.mediabox.width, page.mediabox.height
                total_width += width
                total_height += height
                max_width = max(max_width, width)
                max_height = max(max_height, height)
            base_path_and_name = strip_ext(file_name)
            vertical_pdf = pypdf.PageObject.create_blank_page(width=max_width, height=total_height)
            for i, page in enumerate(pages):
                vertical_pdf.merge_page(page, expand=True)
                if i != len(pages) - 1:
                    vertical_pdf.add_transformation(pypdf.Transformation().translate(ty=page.mediabox.height))
            output = pypdf.PdfWriter()
            output.add_page(vertical_pdf)
            vertical_path = f"{base_path_and_name}_vertical.pdf"
            with open(vertical_path, "wb") as vertical_out:
                output.write(vertical_out)
            if status_field:
                status_field.setText(f"Created vertical stitched PDF: {vertical_path}")
            horizontal_pdf = pypdf.PageObject.create_blank_page(width=total_width, height=max_height)
            for i, page in enumerate(pages[::-1]):
                horizontal_pdf.merge_page(page, expand=True)
                if i != len(pages) - 1:
                    horizontal_pdf.add_transformation(pypdf.Transformation().translate(tx=page.mediabox.width))
            output = pypdf.PdfWriter()
            output.add_page(horizontal_pdf)
            horizontal_path = f"{base_path_and_name}_horizontal.pdf"
            with open(horizontal_path, "wb") as horizontal_out:
                output.write(horizontal_out)
            if status_field:
                status_field.setText(f"Created horizontal stitched PDF: {horizontal_path}")


def encrypt_pdf(dir_path):
    encryption_key = get_input()
    if not encryption_key:
        if status_field:
            status_field.setText("No encryption key provided.")
        return
    for pdf_path in index_directory(dir_path, "pdf"):
        with open(pdf_path, "rb") as pdf_file:
            reader = pypdf.PdfReader(pdf_file)
            writer = pypdf.PdfWriter()
            writer.append_pages_from_reader(reader)
            writer.encrypt(user_password=encryption_key)
            output_path = f"{strip_ext(pdf_path)}_encrypted.pdf"
            with open(output_path, "wb") as encrypted_pdf:
                writer.write(encrypted_pdf)
            if status_field:
                status_field.setText(f"Encrypted PDF created: {output_path}")


def save_page_range(path, start_page, end_page):
    range_input = get_input()
    if not range_input:
        return
    range_input = range_input.split("-")
    if len(range_input) > 1:
        if range_input[0] and int(range_input[0]) >= 0 and range_input[1] and int(range_input[1]) > 0:
            start_page = range_input[0]
            end_page = range_input[1]
        elif range_input[0] == "":
            start_page = 0
            end_page = range_input[1]
        elif range_input[1] == "":
            start_page = range_input[0]
            end_page = -1
    else:
        start_page = end_page = range_input[0]
    for file_path in index_directory(path, "pdf"):
        total_pages = len(pypdf.PdfReader(file_path).pages)
        if int(start_page) > total_pages:
            continue
        if end_page == -1 or int(end_page) > total_pages:
            with open(file_path, "rb") as f:
                end_page = pypdf.PdfReader(f)
                end_page = len(end_page.pages)
        start_page = int(start_page)
        end_page = int(end_page)
        writer = pypdf.PdfWriter()
        reader = pypdf.PdfReader(file_path)
        for page in range(start_page - 1, end_page):
            writer.add_page(reader.pages[page])
        with open(os.path.join(path, f"{start_page}-{end_page} {get_file_name(file_path)}"), "wb") as output_pdf:
            writer.write(output_pdf)


def resave_files(path, sanitize=False):
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
            os.remove(file_path)
            if sanitize:
                file_path = os.path.join(get_folder_path(file_path), "document.pdf")
            writer._info = pypdf.generic.DictionaryObject()
            with open(file_path, "wb") as pdf:
                writer.write(pdf)
        else:
            with PIL.Image.open(file_path) as img:
                img_without_metadata = img.copy()
            os.remove(file_path)
            if sanitize:
                file_path = os.path.join(get_folder_path(file_path), f"image.{get_file_type(file_path)}")
            img_without_metadata.save(file_path)
        new_size = os.path.getsize(file_path) / 1024
        pct_chg = f"{round(((new_size - org_size) / org_size) * 100, 1)}%"
        results += f"{file_path} {round(org_size, 1)} KB to {round(new_size, 1)} KB ({pct_chg})\n"
    if status_field:
        status_field.setText(results)


def pdf_to_image(path):
    if not shutil.which("pdftoppm"):
        if status_field:
            status_field.setText("Poppler (pdftoppm) not found in PATH.")
        return
    file_paths = index_directory(path, "pdf")
    for file in file_paths:
        pdf_pages = pdf2image.convert_from_path(file)
        for page_num, pdf_page in enumerate(pdf_pages):
            pdf_page.save(f"{strip_ext(file)} {page_num}.png")


def image_to_pdf(path):
    for file_path in index_directory(path, file_types=["png", "jpg"]):
        img = PIL.Image.open(file_path)
        img.save(f"{strip_ext(file_path)}.pdf", "PDF", resolution=img.width / 850 * 100)


def sanitize(path):
    resave_files(path, True)


def crop_images(path):
    file_paths = index_directory(path, file_types=["png", "jpg"])
    crop_configs = {(1280, 1080): [(0, 0, 1280, 720)], (2560, 720): [(0, 0, 1280, 720), (1280, 0, 2560, 720)],
                    (3200, 1080): [(0, 0, 1920, 1080), (1920, 0, 3200, 1080)], }
    for file_path in file_paths:
        original_image = PIL.Image.open(file_path)
        crop_areas = crop_configs.get(original_image.size)
        if crop_areas is None:
            continue
        for index, crop_area in enumerate(crop_areas, 1):
            cropped_image = original_image.crop(box=crop_area)
            cropped_image.save(f"{strip_ext(file_path)} !CROPPED {index}.{get_file_type(file_path)}")


def merge_images(path):
    file_paths = index_directory(path, file_types=["jpeg", "jpg", "png"])
    if len(file_paths) == 1:
        if status_field:
            status_field.setText("Failed to merge images: need more than one image to merge")
        return
    imgs = []
    total_width = total_height = max_width = max_height = 0
    for file_path in file_paths:
        img = PIL.Image.open(file_path)
        imgs.append(img)
        width, height = img.size
        total_width += width
        total_height += height
        max_width = max(max_width, width)
        max_height = max(max_height, height)
    v_scaled_imgs = [numpy.array(img.convert("RGB").resize((max_width, round(max_width / img.width * img.height)))) for
                     img in imgs]
    h_scaled_imgs = [numpy.array(img.convert("RGB").resize((round(max_height / img.height * img.width), max_height)))
                     for img in imgs]
    v_imgs_comb = numpy.vstack(v_scaled_imgs)
    PIL.Image.fromarray(v_imgs_comb).save(os.path.join(path, "!vertical.png"))
    PIL.Image.fromarray(v_imgs_comb).convert("RGB").save(os.path.join(path, "!vertical.jpg"))
    h_imgs_comb = numpy.hstack(h_scaled_imgs)
    PIL.Image.fromarray(h_imgs_comb).save(os.path.join(path, "!horizontal.png"))
    PIL.Image.fromarray(h_imgs_comb).convert("RGB").save(os.path.join(path, "!horizontal.jpg"))


def convert_between_png_jpg(directory):
    for image_path in get_all_images(directory):
        file_type = get_file_type(image_path)
        new_file_path = strip_ext(image_path)
        if file_type == "png":
            PIL.Image.open(image_path).convert("RGB").save(f"{new_file_path}.jpg")
        else:
            PIL.Image.open(image_path).save(f"{new_file_path}.png")


def img_to_ico(path):
    for file_path in get_all_images(path):
        img = PIL.Image.open(file_path)
        img.save(f"{strip_ext(file_path)}.ico")


def print_info(directory):
    output = ""
    files = index_directory(directory, file_types=["jpeg", "jpg", "pdf", "png"])
    for index, path in enumerate(files):
        size = os.path.getsize(path)
        formatted_size = "{:,}".format(size)
        if size < 1024 * 1024:
            size_str = f"{formatted_size} bytes ({size / 1024:.2f} KB)"
        else:
            size_str = f"{formatted_size} bytes ({size / (1024 * 1024):.2f} MB)"
        output += f"\n{index + 1}. {path}\n\tFile Size: {size_str}"
        if path.endswith((".png", ".jpg", ".jpeg")):
            img = PIL.Image.open(path)
            output += f"\tWidth, Height, Mode = ({img.width}, {img.height}, {img.mode}) {img.format}\n"
            for tag_id, value in img.getexif().items():
                tag = str(PIL.ExifTags.TAGS.get(tag_id, tag_id))
                output += f"\t{tag.ljust(25)}: {value}\n"
        elif path.endswith(".pdf"):
            with open(path, "rb") as f:
                pdf = pypdf.PdfReader(f)
                metadata = pdf.metadata or {}
                output += "\n\tMetadata:\n"
                for key, value in metadata.items():
                    output += f"\t{key}: {value}\n"
    if status_field:
        status_field.setText(output.lstrip("\n"))


def duplicate_detector(directory_path):
    file_hashes = {}
    duplicates = []
    for root, _, files in os.walk(directory_path):
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
    if status_field:
        status_field.setText(result_msg)


def get_image_colors(directory_path):
    import collections
    results = []
    for full_file_path in index_directory(directory_path, file_types=["jpeg", "jpg", "png"]):
        img = PIL.Image.open(full_file_path)
        if img.mode == "RGBA":
            colors = [pixel[:3] for pixel in img.getdata() if pixel[3] == 255]
        else:
            colors = [pixel[:3] for pixel in img.getdata()]
        avg_color = numpy.mean(colors, axis=0)
        avg_color_hex = "#%02x%02x%02x" % (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]),)
        color_counter = collections.Counter(colors)
        common_colors = color_counter.most_common(3)
        common_colors_hex = [(("#%02x%02x%02x" % (color[0][0], color[0][1], color[0][2])), color[1]) for color in
                             common_colors]
        avg_color_str = f"Average color: {avg_color_hex}"
        common_colors_str = "\n".join([f"Color: {color[0]}, Frequency: {color[1]}" for color in common_colors_hex])
        results.append(f"Filename: {full_file_path}\n" + avg_color_str + "\n" + common_colors_str)
    if status_field:
        status_field.setText("\n\n".join(results))


def crop_by_90(directory_path):
    for full_file_path in index_directory(directory_path, file_types=["jpeg", "jpg", "png"]):
        img = PIL.Image.open(full_file_path)
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
    for full_file_path in index_directory(directory_path, file_types=["svg", "webp"]):
        output_path = f"{strip_ext(full_file_path)}.png"
        if full_file_path.endswith(".svg"):
            if cairosvg is None:
                continue
            cairosvg.svg2png(url=full_file_path, write_to=output_path)
        elif full_file_path.endswith(".webp"):
            img = PIL.Image.open(full_file_path)
            img.save(output_path, "PNG")


def enhance_contrast(dir_path):
    if img2pdf is None:
        if status_field:
            status_field.setText("img2pdf is not installed.")
        return
    pdf_paths = index_directory(dir_path, "pdf")
    for path in pdf_paths:
        enhanced_images = []
        for image in pdf2image.convert_from_path(path):
            enhanced_image = PIL.ImageEnhance.Contrast(image).enhance(1.25)
            byte_io = io.BytesIO()
            enhanced_image.save(byte_io, format="PNG")
            enhanced_images.append(byte_io.getvalue())
        output_path = f"{strip_ext(path)}_inc_contrast.pdf"
        with open(output_path, "wb") as file:
            file.write(img2pdf.convert(enhanced_images))


def rename_files(dir_path):
    base_name = get_input()
    if not base_name:
        return
    files = index_directory(dir_path)
    total = len(files)
    padding = len(str(total))
    temp_suffix = "_temp"
    temp_files = []
    for i, file in enumerate(files, start=1):
        temp_name = os.path.join(dir_path, f"{temp_suffix}-{i}.{get_file_type(file)}")
        os.rename(file, temp_name)
        temp_files.append(temp_name)
    for i, temp_file in enumerate(temp_files, start=1):
        padded_num = str(i).zfill(padding)
        final_name = os.path.join(dir_path, f"{base_name}-{padded_num}.{get_file_type(temp_file)}")
        os.rename(temp_file, final_name)


def restart_program():
    python_executable = sys.executable
    os.execl(python_executable, python_executable, *sys.argv)


def exit_program():
    sys.exit()


def index_directory(path, file_types=None):
    file_types_filter = False
    file_types_list = []
    if file_types is None or file_types == "*":
        file_types_filter = False
    else:
        file_types_filter = True
        if isinstance(file_types, list):
            file_types_list = [f".{i.lower()}" for i in file_types]
        else:
            file_types_list = [f".{str(file_types).lower()}"]
    file_paths = []
    for subdir, _, files in os.walk(path):
        for file in files:
            if file_types_filter:
                file_type = f".{file.split('.')[-1].lower()}"
                if file_type in file_types_list:
                    file_paths.append(os.path.join(subdir, file))
            else:
                file_paths.append(os.path.join(subdir, file))
    return file_paths


def get_all_images(directory_path):
    image_extensions = (".png", ".jpg", ".jpeg")
    image_files = [os.path.join(root, file) for root, _, files in os.walk(directory_path) for file in files if
                   os.path.splitext(file)[1].lower() in image_extensions]
    return image_files


def get_folder_path(path):
    return os.path.dirname(path)


def get_file_name(path):
    return os.path.basename(path)


def strip_ext(filename):
    return os.path.splitext(filename)[0]


def get_file_type(path):
    return path.split(".")[-1]


def get_input():
    global input_text
    return str(input_text) if input_text else False


def crop_solid_edges(directory_path):
    def is_similar(pixel, ref_pixel, threshold=10):
        return all(abs(a - b) <= threshold for a, b in zip(pixel[:3], ref_pixel[:3]))

    def find_crop_edges(img):
        width, height = img.size
        pixels = img.load()
        top_ref = pixels[0, 0]
        bottom_ref = pixels[0, height - 1]
        left_ref = pixels[0, 0]
        right_ref = pixels[width - 1, 0]

        top = 0
        for t in range(height):
            for x in range(width):
                if not is_similar(pixels[x, t], top_ref):
                    top = t
                    break
            else:
                continue
            break

        bottom = height - 1
        for b in range(height - 1, -1, -1):
            for x in range(width):
                if not is_similar(pixels[x, b], bottom_ref):
                    bottom = b
                    break
            else:
                continue
            break

        left = 0
        for left_x in range(width):
            for y in range(height):
                if not is_similar(pixels[left_x, y], left_ref):
                    left = left_x
                    break
            else:
                continue
            break

        right = width - 1
        for r in range(width - 1, -1, -1):
            for y in range(height):
                if not is_similar(pixels[r, y], right_ref):
                    right = r
                    break
            else:
                continue
            break

        return left, top, right + 1, bottom + 1

    results = []
    for file_path in index_directory(directory_path, file_types=["png", "jpg", "jpeg"]):
        img = PIL.Image.open(file_path).convert("RGB")
        crop_box = find_crop_edges(img)
        cropped = img.crop(crop_box)
        out_path = f"{strip_ext(file_path)}_cropped.{get_file_type(file_path)}"
        cropped.save(out_path)
        results.append(f"Cropped: {out_path}")
    if status_field:
        status_field.setText("\n".join(results))
