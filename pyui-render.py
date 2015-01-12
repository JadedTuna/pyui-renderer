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
top: {y}px;
left: {x}px;
width: {w}px;
height: {h}px;
background-color: {background_color};
border-color: {border_color};
color: {tint_color};
">
<div class="View-name">{name}</div><br />
<span class="View-name-border" style="
width: {w}px;
"></span>
</div>
"""

template_Label = """
<span class="Label" style="
top: {y}px;
left: {x}px;
width: {w}px;
height: {h}px;
border-color: {border_color};
color: {text_color};
font-size: {font_size}px;
font-family: {font_name};
alignment: {alignment};
">{text}</span>
"""

template_TextField = """
<div class="TextField" style="
top: {y}px;
left: {x}px;
" ><input class="TextField" style="
width: {w}px;
height: {h}px;
border-color: {border_color};
color: {text_color};
font-size: {font_size}px;
font-family: {font_name};
alignment: {alignment};
border-width: {border_width}px;
border-style: solid;
border-radius: {corner_radius}px;
padding: 0 5px 0 5px;
" placeholder="{placeholder}" value="{text}"></div>
"""

pattern = "RGBA\(([\d.]+),([\d.]+),([\d.]+),([\d.]+)\)"
document = StringIO()

pad_top = 30
defaults = {
    "font_name":   "Helvetica",
    "font_size":   17,
    "text":        "",
    "placeholder": ""
}

def convert(attrs, *labels):
    for label in labels:
        r, g, b, a = re.findall(pattern, attrs[label])[0]
        r = float(r) * 255
        g = float(g) * 255
        b = float(b) * 255
        a = float(a)

        attrs[label] = "rgba(%d, %d, %d, %f)" % (r, g, b, a)

def parse_frame(strframe):
    data = json.loads(strframe.replace("{", "[").replace("}", "]"))

    frame = {
        'x': data[0][0],
        'y': data[0][1],
        'w': data[1][0],
        'h': data[1][1]
    }
    
    return frame

# Rendering functions

def render_View(**attrs):
    convert(attrs, 'background_color', 'border_color', 'tint_color')

    document.write(template_View.format(**attrs))

def render_Label(**attrs):
    convert(attrs, 'text_color', 'border_color')
    attrs['y'] += pad_top

    document.write(template_Label.format(**attrs))

def render_TextField(**attrs):
    convert(attrs, 'border_color', 'text_color')
    attrs['y'] += pad_top

    document.write(template_TextField.format(**attrs))


def render(json):
    view = json[0] # This renderer supports just one view for now
    attrs = view["attributes"]
    frame = parse_frame(view["frame"])
    for (key, value) in frame.items():
        attrs[key] = value

    render_View(**attrs)

    for element in view["nodes"]:
        attrs = element["attributes"]
        frame = parse_frame(element["frame"])
        for (key, value) in frame.items():
            attrs[key] = value

        for (key, value) in defaults.items():
            if not key in attrs.keys():
                attrs[key] = value

        if element["class"] == "Label":
            render_Label(**attrs)

        elif element["class"] == "TextField":
            render_TextField(**attrs)

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
