from PIL import Image, ImageOps, ImageDraw
from swt.swt import swt


def main(input_filename, output_filename):
    img = Image.open(input_filename)
    img = img.convert('RGBA')

    print('Image size:', img.size)

    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for x0,y0, x1,y1 in swt(img,
        # direction=0,
        # scale_invariant=1,
        # aspect_ratio=10,
        # thickness_ratio=3,
        # height_ratio=2.5,
        # # scale=1.3,
        # letter_occlude_thresh=7,
        # breakdown_ratio=0.4,
    ):
        draw.rectangle([x0, y0, x1, y1], width=5, fill=(0, 0, 0, 60), outline=(255, 0, 0, 255))

    img = Image.alpha_composite(img, overlay)
    img = img.convert('RGB')
    img.save(output_filename)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Applies SWT to an image')
    parser.add_argument('input_filename')
    parser.add_argument('output_filename')

    args = parser.parse_args()

    main(args.input_filename, args.output_filename)