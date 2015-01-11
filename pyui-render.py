import re
import wx
import json
try:
    from cStringIO import StringIO
except ImportError:
    from  StringIO import StringIO

template = """
<style>
div.View {
    position: fixed;
    left: 0px;
    top: 0px;
    border-radius: 10px;
}

div.View-name {
    color: #595959;
    text-align: center;
}

span.View-name-border {
    position: fixed;
    top: 30px;
    left: 0px;
    width: 320;
    border-bottom: 1px solid #595959;
}

span.Label {
    position: fixed;
}

div.TextField {
    position: fixed;
}
</style>
<html>
<head></head>
<body>
    %s
</body>
</html>
"""

template_View = """
<div class="View" style="
top: {0}px;
left: {1}px;
width: {2}px;
height: {3}px;
background-color: {4};
border-color: {5};
color: {6};
">
<div class="View-name">{7}</div><br />
<span class="View-name-border"></span>
</div>
"""

template_Label = """
<span class="Label" style="
top: {0}px;
left: {1}px;
width: {2}px;
height: {3}px;
border-color: {4};
color: {5};
font-size: {6}px;
font-family: {7};
alignment: {8};
">{9}</span>
"""

template_TextField = """
<div class="TextField" style="
top: {0}px;
left: {1}px;
" ><input class="TextField" style="
width: {2}px;
height: {3}px;
border-color: {4};
color: {5};
font-size: {6}px;
font-family: {7};
alignment: {8};
border-width: {9}px;
border-style: solid;
border-radius: {10}px;
padding: 0 5px 0 5px;
" placeholder="{11}" value="{12}"></div>
"""

pattern = "RGBA\(([\d.]+),([\d.]+),([\d.]+),([\d.]+)\)"
document = StringIO()

pad_top = 30
defaults = {
    "font_name":   "<system>",
    "font_size":   17,
    "text":        "",
    "placeholder": ""
}

def convert(s):
    r, g, b, a = re.findall(pattern, s)[0]
    r = float(r) * 255
    g = float(g) * 255
    b = float(b) * 255
    a = float(a)

    return "rgba(%d, %d, %d, %f)" % (r, g, b, a)

def parse_frame(strframe):
    data = json.loads(strframe.replace("{", "[").replace("}", "]"))

    frame = [data[0][0], data[0][1], data[1][0], data[1][1]]
    return frame

# Rendering functions

def render_View(name, (y, x, w, h), bg, bc, c):
    bg = convert(bg)
    bc = convert(bc)
    c  = convert(c)
    document.write(template_View.format(x, y, w, h, bg, bc, c, name))

def render_Label(label, (y, x, w, h), font_size, font_name, alignment, c, bc):
    c  = convert(c)
    bc = convert(bc)
    document.write(template_Label.format(pad_top + x, y, w, h,
        bc, c, font_size, font_name, alignment, label))

def render_TextField(default, placeholder, (y, x, w, h),
                     font_size, font_name, alignment, bw, cr,
                     bc, c):
    bc = convert(bc)
    c  = convert(c)
    document.write(template_TextField.format(pad_top + x, y, w, h,
        bc, c, font_size, font_name, alignment,
        bw, cr, placeholder, default))


def render(json):
    view = json[0] # This renderer supports just one view for now
    attrs = view["attributes"]
    frame = parse_frame(view["frame"])
    render_View(
        attrs["name"],
        frame,
        attrs["background_color"],
        attrs["border_color"],
        attrs["tint_color"]
    )
    for element in view["nodes"]:
        frame = parse_frame(element["frame"])
        attrs = element["attributes"]

        for key, value in defaults.items():
            if not key in attrs.keys():
                attrs[key] = value

        if element["class"] == "Label":
            render_Label(
                attrs["text"],
                frame,
                attrs["font_size"] - 3, attrs["font_name"],
                attrs["alignment"], attrs["text_color"],
                attrs["border_color"]
            )
        elif element["class"] == "TextField":
            render_TextField(
                attrs["text"],
                attrs["placeholder"],
                frame,
                attrs["font_size"] - 3, attrs["font_name"],
                attrs["alignment"], attrs["border_width"],
                attrs["corner_radius"], attrs["border_color"],
                attrs["text_color"]
            )
        else:
            print("Unknown (unsupported?) element: `%s'" % element["class"])

    write_html("index.html")


def write_html(filename):
    with open(filename, "wb") as fp:
        fp.write(template % document.getvalue())

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("pyui", help="pyui file to render")
    parser.add_argument("-l", "--launch", help="launch browser")

    args = parser.parse_args()
    import os
    if not os.path.isfile(args.pyui):
        parser.error("failed to open pyui file.")

    with open(args.pyui, "rb") as fp:
        data = json.load(fp)

    render(data)

if __name__ == "__main__":
    main()
