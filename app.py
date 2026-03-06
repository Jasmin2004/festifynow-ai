from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io
import os

app = Flask(__name__)
CORS(app)

# =============================

# FESTIVAL TEMPLATE IMAGES

# =============================

FESTIVAL_IMAGES = {

```
"Guru Purnima": "templates_images/guru_purnima.png",
"Nag Panchami": "templates_images/nag_panchami.png",
"Independence Day": "templates_images/independence_day.png",
"Raksha Bandhan": "templates_images/raksha_bandhan.png",
"Krishna Janmashtami": "templates_images/krishna_janmashtami.png",
"Ganesh Chaturthi": "templates_images/ganesh_chaturthi.png",
"Ganesh Visarjan": "templates_images/ganesh_visarjan.png",
"Gandhi Jayanti": "templates_images/gandhi_jayanti.png",
"Navratri": "templates_images/navratri.png",
"Durga Puja": "templates_images/durga_puja.png",
"Dussehra": "templates_images/dussehra.png",
"Dhanteras": "templates_images/dhanteras.png",
"Diwali": "templates_images/diwali.png",
"Govardhan Puja": "templates_images/govardhan_puja.png",
"Bhai Dooj": "templates_images/bhai_dooj.png",
"Children's Day": "templates_images/childrens_day.png",
"Tulsi Vivah": "templates_images/tulsi_vivah.png",
"Makar Sankranti": "templates_images/makar_sankranti.png",
"Maha Shivratri": "templates_images/maha_shivratri.png",
"Holi": "templates_images/holi.png"
```

}

# =============================

# FONT LOADER

# =============================

def get_font(size):

```
bold = "C:/Windows/Fonts/arialbd.ttf"
normal = "C:/Windows/Fonts/arial.ttf"

if os.path.exists(bold):
    return ImageFont.truetype(bold, size)

elif os.path.exists(normal):
    return ImageFont.truetype(normal, size)

else:
    return ImageFont.load_default()
```

# =============================

# COLORS

# =============================

RIBBON_COLOR = (31,42,68,230)
TEXT_COLOR = (246,215,118)

# =============================

# LEFT RIBBON

# =============================

def draw_left_ribbon(draw, text, y, font):

```
padding = 25
ribbon_height = 70
cut = 35

text_width = draw.textlength(text, font=font)

ribbon_width = int(text_width + padding*2 + 40)

points = [
    (0,y),
    (ribbon_width,y),
    (ribbon_width+cut,y+ribbon_height/2),
    (ribbon_width,y+ribbon_height),
    (0,y+ribbon_height)
]

draw.polygon(points, fill=RIBBON_COLOR)

draw.text(
    (padding,y+ribbon_height/2),
    text,
    font=font,
    fill=TEXT_COLOR,
    anchor="lm"
)
```

# =============================

# RIGHT RIBBON

# =============================

def draw_right_ribbon(draw,text,y,font,img_width):

```
padding = 25
ribbon_height = 70
cut = 35

text_width = draw.textlength(text,font=font)

ribbon_width = int(text_width + padding*2 + 40)

start_x = img_width - ribbon_width

points = [
    (start_x,y),
    (img_width,y),
    (img_width,y+ribbon_height),
    (start_x,y+ribbon_height),
    (start_x-cut,y+ribbon_height/2)
]

draw.polygon(points, fill=RIBBON_COLOR)

draw.text(
    (img_width-padding,y+ribbon_height/2),
    text,
    font=font,
    fill=TEXT_COLOR,
    anchor="rm"
)
```

@app.route("/")
def home():
return "Festify Poster Server Running"

@app.route("/generate-poster", methods=["POST"])
def generate_poster():

```
try:

    company = request.form.get("company") or ""
    mobile = request.form.get("mobile") or ""
    website = request.form.get("website") or ""
    address = request.form.get("address") or ""
    festival = request.form.get("festival") or "Diwali"

    logo_file = request.files.get("logo")

    bg_path = FESTIVAL_IMAGES.get(festival, "templates_images/diwali.png")

    if not os.path.exists(bg_path):
        return jsonify({"error":"Template missing"}),500

    bg = Image.open(bg_path).convert("RGBA")

    width,height = bg.size
    draw = ImageDraw.Draw(bg)

    # =============================
    # LOGO PANEL
    # =============================
    if logo_file:

        logo = Image.open(logo_file).convert("RGBA")

        panel_width = int(width * 0.16)
        panel_height = int(height * 0.11)

        padding = int(panel_width * 0.10)

        max_logo_w = panel_width - padding*2
        max_logo_h = panel_height - padding*2

        ratio = min(max_logo_w/logo.width, max_logo_h/logo.height)

        new_w = int(logo.width * ratio)
        new_h = int(logo.height * ratio)

        logo = logo.resize((new_w,new_h), Image.LANCZOS)

        radius = int(panel_height * 0.40)

        draw.rectangle(
            [0,0,panel_width-radius,panel_height],
            fill=(255,255,255,240)
        )

        draw.rectangle(
            [0,0,panel_width,panel_height-radius],
            fill=(255,255,255,240)
        )

        draw.pieslice(
            [
                panel_width-radius*2,
                panel_height-radius*2,
                panel_width,
                panel_height
            ],
            0,90,
            fill=(255,255,255,240)
        )

        logo_x = (panel_width - new_w)//2
        logo_y = (panel_height - new_h)//2

        bg.paste(logo,(logo_x,logo_y),logo)

    # =============================
    # TEXT POSITIONS
    # =============================
    bottom_y1 = height - 150
    bottom_y2 = height - 75

    # =============================
    # BIG FONT SIZES
    # =============================
    company_font = get_font(60)
    mobile_font = get_font(58)
    website_font = get_font(56)
    address_font = get_font(58)

    if company:
        draw_left_ribbon(draw,company,bottom_y1,company_font)

    if mobile:
        draw_right_ribbon(draw,mobile,bottom_y1,mobile_font,width)

    if website:
        draw_left_ribbon(draw,website,bottom_y2,website_font)

    if address:
        draw_right_ribbon(draw,address,bottom_y2,address_font,width)

    img_io = io.BytesIO()

    bg.convert("RGB").save(img_io,"PNG")
    img_io.seek(0)

    return send_file(img_io,mimetype="image/png")

except Exception as e:
    print("ERROR:",str(e))
    return jsonify({"error":str(e)}),500
```

if **name** == "**main**":

```
app.run(host="0.0.0.0",port=5000,debug=True)
```

