from PIL import Image, ImageFont, ImageDraw

title_font = ImageFont.truetype('times-new-roman-cyr.ttf', 30)

filename = "result.jpg"


def generate_demotivator_image(original, demotivator):
    my_image = Image.open("sample_demotivator.png")
    image_editable = ImageDraw.Draw(my_image)

    w, h = image_editable.textsize("W" * round(len(demotivator) * 2.5))
    image_editable.text((300 - w / 2, 500 + 3 * (h / 4)), demotivator, (255, 255, 255), font=title_font)

    w, h = image_editable.textsize("W" * round(len(original) * 2.5))
    image_editable.text((300 - w / 2, 300 - (h / 2)), original, (255, 255, 255), font=title_font)

    my_image.save(filename)
    return filename
