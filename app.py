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
}

# =============================
# FONT LOADER (Improved for Server)
# =============================

def get_font(size):
    # Standard Linux paths for fonts often found on Railway/Ubuntu
    font_paths = [
        "DejaVuSans-Bold.ttf", 
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    # If no system font found, try to load from local directory if you uploaded one
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

# =============================
# COLORS
# =============================

RIBBON_COLOR = (31, 42, 68, 230)
TEXT_COLOR = (246, 215, 118)

# =============================
# LEFT RIBBON (Scaled)
# =============================

def draw_left_ribbon(draw, text, y, font, scale_factor):
    padding = int(30 * scale_factor)
    ribbon_height = int(80 * scale_factor)
    cut = int(40 * scale_factor)

    # Use textbbox for precise measurement on server
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    ribbon_width = int(text_width + padding * 2 + (50 * scale_factor))

    points = [
        (0, y),
        (ribbon_width, y),
        (ribbon_width + cut, y + ribbon_height / 2),
        (ribbon_width, y + ribbon_height),
        (0, y + ribbon_height)
    ]

    draw.polygon(points, fill=RIBBON_COLOR)
    draw.text((padding, y + ribbon_height / 2), text, font=font, fill=TEXT_COLOR, anchor="lm")

# =============================
# RIGHT RIBBON (Scaled)
# =============================

def draw_right_ribbon(draw, text, y, font, img_width, scale_factor):
    padding = int(30 * scale_factor)
    ribbon_height = int(80 * scale_factor)
    cut = int(40 * scale_factor)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    ribbon_width = int(text_width + padding * 2 + (50 * scale_factor))

    start_x = img_width - ribbon_width

    points = [
        (start_x, y),
        (img_width, y),
        (img_width, y + ribbon_height),
        (start_x, y + ribbon_height),
        (start_x - cut, y + ribbon_height / 2)
    ]

    draw.polygon(points, fill=RIBBON_COLOR)
    draw.text((img_width - padding, y + ribbon_height / 2), text, font=font, fill=TEXT_COLOR, anchor="rm")

# =============================
# HOME ROUTE
# =============================

@app.route("/")
def home():
    return "Festify Poster Server Running"

# =============================
# POSTER GENERATOR
# =============================

@app.route("/generate-poster", methods=["POST"])
def generate_poster():
    try:
        company = request.form.get("company", "")
        mobile = request.form.get("mobile", "")
        website = request.form.get("website", "")
        address = request.form.get("address", "")
        festival = request.form.get("festival", "Diwali")
        logo_file = request.files.get("logo")

        bg_path = FESTIVAL_IMAGES.get(festival)
        if not bg_path or not os.path.exists(bg_path):
            return jsonify({"error": "Template missing"}), 500

        bg = Image.open(bg_path).convert("RGBA")
        width, height = bg.size
        draw = ImageDraw.Draw(bg)

        # SCALE FACTOR: Adjusts everything based on image resolution
        # Assumes base design was made for ~1000px height
        scale = height / 1000

        # =============================
        # LOGO PANEL
        # =============================
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA")
            panel_width = int(width * 0.16)
            panel_height = int(height * 0.11)
            padding = int(panel_width * 0.10)
            max_logo_w = panel_width - padding * 2
            max_logo_h = panel_height - padding * 2

            ratio = min(max_logo_w / logo.width, max_logo_h / logo.height)
            new_w, new_h = int(logo.width * ratio), int(logo.height * ratio)
            logo = logo.resize((new_w, new_h), Image.Resampling.LANCZOS)

            radius = int(panel_height * 0.40)
            draw.rectangle([0, 0, panel_width - radius, panel_height], fill=(255, 255, 255, 240))
            draw.rectangle([0, 0, panel_width, panel_height - radius], fill=(255, 255, 255, 240))
            draw.pieslice([panel_width - radius * 2, panel_height - radius * 2, panel_width, panel_height], 0, 90, fill=(255, 255, 255, 240))

            bg.paste(logo, ((panel_width - new_w) // 2, (panel_height - new_h) // 2), logo)

        # =============================
        # TEXT POSITION & SIZE FIX
        # =============================
        bottom_y1 = height - int(180 * scale)
        bottom_y2 = height - int(90 * scale)

        # IMPORTANT: Font size must be proportional to the 80px ribbon height
        # 45 is roughly 55% of 80, which looks balanced.
        font_size = int(45 * scale)

        company_font = get_font(font_size)
        mobile_font = get_font(font_size)
        website_font = get_font(font_size)
        address_font = get_font(font_size)

        if company:
            draw_left_ribbon(draw, company, bottom_y1, company_font, scale)
        if mobile:
            draw_right_ribbon(draw, mobile, bottom_y1, mobile_font, width, scale)
        if website:
            draw_left_ribbon(draw, website, bottom_y2, website_font, scale)
        if address:
            draw_right_ribbon(draw, address, bottom_y2, address_font, width, scale)

        img_io = io.BytesIO()
        bg.convert("RGB").save(img_io, "PNG")
        img_io.seek(0)

        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
