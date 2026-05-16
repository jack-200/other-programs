import os

import img2pdf
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont


def get_ocr_friendly_font(font_size=150):
    fallback_fonts = [
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
        "/System/Library/Fonts/Courier.ttc",
    ]

    for path in fallback_fonts:
        if os.path.exists(path):
            try:
                return PIL.ImageFont.truetype(path, font_size)
            except Exception:
                continue

    return PIL.ImageFont.load_default()


def calculate_centered_text_position(draw, text, font, canvas_width, canvas_height):
    if hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        text_width, text_height = draw.textsize(text, font=font)

    x_coordinate = (canvas_width - text_width) // 2
    y_coordinate = (canvas_height - text_height) // 2
    return (x_coordinate, y_coordinate)


def generate_test_pdfs(
    output_directory="pdf-and-image-tools/tests/data/assets", total_files=10
):
    os.makedirs(output_directory, exist_ok=True)

    canvas_width, canvas_height = 800, 1000
    text_color_black = (0, 0, 0)

    for index in range(1, total_files + 1):
        canvas = PIL.Image.new("RGB", (canvas_width, canvas_height), color="white")
        draw_context = PIL.ImageDraw.Draw(canvas)

        ocr_font = get_ocr_friendly_font()
        label_text = str(index)

        text_position = calculate_centered_text_position(
            draw_context, label_text, ocr_font, canvas_width, canvas_height
        )

        draw_context.text(
            text_position, label_text, fill=text_color_black, font=ocr_font
        )

        temporary_image_path = os.path.join(output_directory, f"temp_asset_{index}.png")
        alphabetical_pdf_path = os.path.join(output_directory, f"test_{index:02d}.pdf")

        canvas.save(temporary_image_path)

        with open(alphabetical_pdf_path, "wb") as pdf_file:
            pdf_file.write(img2pdf.convert(temporary_image_path))

        os.remove(temporary_image_path)

    print(f"Generated {total_files} test PDFs in {output_directory}")


if __name__ == "__main__":
    generate_test_pdfs()
