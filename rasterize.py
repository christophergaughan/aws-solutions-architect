from pdf2image import convert_from_path
import img2pdf
import os

original_pdf = "20230408_flattened.pdf"
output_images = convert_from_path(original_pdf, dpi=300)  # each page as a PIL image

# Save each page as a PNG
image_files = []
for i, page_image in enumerate(output_images):
    page_filename = f"page_{i}.png"
    page_image.save(page_filename, "PNG")
    image_files.append(page_filename)

# Combine images back into a single PDF
rasterized_pdf = "20230408_rasterized.pdf"
with open(rasterized_pdf, "wb") as f:
    f.write(img2pdf.convert(image_files))

# Clean up image files if you want
for img in image_files:
    os.remove(img)

