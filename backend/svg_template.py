import svgwrite
from lxml import etree
import os

def create_svg_template(output_filename):
    width = 500
    height = 500
    background_color = "#f0f0f0"
    image_size = 40
    text_font = "HEEBO"
    text_size = 16
    padding = 20
    text_image_spacing = 10  # רווח בין תמונה לטקסט

    dwg = svgwrite.Drawing(output_filename, size=(f"{width}px", f"{height}px"), profile='tiny')
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=background_color))

    # קבוצה ראשונה
    group1_y = (height / 2) - (image_size + text_size + text_image_spacing + padding)
    image1_x = (width - image_size) / 2
    dwg.add(dwg.image(href="image1.png", insert=(image1_x, group1_y), size=(f"{image_size}px", f"{image_size}px"), id="image1"))

    text1_y = group1_y + image_size + text_image_spacing
    text1 = dwg.text("טקסט 1", insert=(width / 2, text1_y),
                     font_family=text_font, font_size=f"{text_size}px", text_anchor="middle", id="text1")
    dwg.add(text1)

    # קבוצה שנייה
    group2_y = (height / 2) + padding
    dwg.add(dwg.image(href="image2.png", insert=(image1_x, group2_y), size=(f"{image_size}px", f"{image_size}px"), id="image2"))

    text2_y = group2_y + image_size + text_image_spacing
    text2 = dwg.text("טקסט 2", insert=(width / 2, text2_y),
                     font_family=text_font, font_size=f"{text_size}px", text_anchor="middle", id="text2")
    dwg.add(text2)

    dwg.save()

create_svg_template("output.svg")

def insert_text_into_svg(svg_filename, text_to_insert, placeholder_id):
    tree = etree.parse(svg_filename)
    root = tree.getroot()

    placeholder = root.find(f".//*[@id='{placeholder_id}']")
    if placeholder is not None:
        placeholder.text = text_to_insert

    tree.write(svg_filename)

def insert_image_into_svg(svg_filename, image_filename, placeholder_id):
    tree = etree.parse(svg_filename)
    root = tree.getroot()

    placeholder = root.find(f".//*[@id='{placeholder_id}']")
    if placeholder is not None:
        placeholder.set("{http://www.w3.org/1999/xlink}href", image_filename)

    tree.write(svg_filename)