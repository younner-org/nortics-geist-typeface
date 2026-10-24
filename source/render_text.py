import sys, os
import uharfbuzz as hb
import freetype
from PIL import Image

FL = freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_NO_AUTOHINT


def shape(path, text, features=None):
    blob = hb.Blob.from_file_path(path)
    face = hb.Face(blob)
    font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {})
    names = [font.glyph_to_string(i.codepoint) for i in buf.glyph_infos]
    return buf, names, face.upem


def render(path, lines, size=64, out=None, bg=(0, 0, 0), fg=(255, 255, 255), pad=30, track=0):
    ft = freetype.Face(path)
    ft.set_pixel_sizes(0, size)
    rows = []
    for text in lines:
        buf, names, upem = shape(path, text)
        k = size / upem
        w = (sum(p.x_advance for p in buf.glyph_positions) - track * len(buf.glyph_infos)) * k
        rows.append((buf, w))
    W = int(max(w for _, w in rows) + 2 * pad)
    H = int(len(rows) * size * 1.35 + 2 * pad)
    img = Image.new("RGB", (W, H), bg)
    for r, (buf, w) in enumerate(rows):
        pen = pad
        base = pad + size * 0.95 + r * size * 1.35
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            ft.load_glyph(info.codepoint, FL)
            g = ft.glyph
            b = g.bitmap
            if b.width and b.rows:
                tile = Image.frombytes("L", (b.width, b.rows), bytes(b.buffer))
                x = int(pen + pos.x_offset * size / upem + g.bitmap_left)
                y = int(base - pos.y_offset * size / upem - g.bitmap_top)
                img.paste(Image.new("RGB", tile.size, fg), (x, y), tile)
            pen += (pos.x_advance - track) * size / upem
    if out:
        img.save(out)
    return img


if __name__ == "__main__":
    path = os.path.expanduser(sys.argv[2])
    render(path, sys.argv[3].split("|"), int(sys.argv[4]) if len(sys.argv) > 4 else 64, sys.argv[1])
    print("saved", sys.argv[1])
