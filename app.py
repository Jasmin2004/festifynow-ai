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
# FONT LOADER (Roboto Optimized)
# =============================

def get_font(size):
    # This must match the filename you uploaded to GitHub exactly
    font_filename = "Roboto-VariableFont_wdth,wght.ttf"
    base_path = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_path, font_filename)
    
    try:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        # Fallback to system font if Roboto is missing
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

# =============================
# COLORS
# =============================

RIBBON_COLOR = (31, 42, 68, 235)
TEXT_COLOR = (246, 215, 118)

# =============================
# SMART RIBBON LOGIC (Left)
# =============================

def draw_left_ribbon(draw, text, y, base_size, img_width, scale):
    padding = int(35 * scale)
    ribbon_height = int(75 * scale)
    cut = int(35 * scale)
    max_w = int(img_width * 0.46) # Limit to 46% of width

    # Dynamic Font Scaling
    curr_size = base_size
    font = get_font(curr_size)
    tw = draw.textlength(text, font=font)

    # Shrink font if text is too long for its side
    while (tw + padding * 2) > max_w and curr_size > int(15 * scale):
        curr_size -= 2
        font = get_font(curr_size)
        tw = draw.textlength(text, font=font)

    ribbon_width = int(tw + padding * 2)

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
# SMART RIBBON LOGIC (Right)
# =============================

def draw_right_ribbon(draw, text, y, base_size, img_width, scale):
    padding = int(35 * scale)
    ribbon_height = int(75 * scale)
    cut = int(35 * scale)
    max_w = int(img_width * 0.46)

    curr_size = base_size
    font = get_font(curr_size)
    tw = draw.textlength(text, font=font)

    while (tw + padding * 2) > max_w and curr_size > int(15 * scale):
        curr_size -= 2
        font = get_font(curr_size)
        tw = draw.textlength(text, font=font)

    ribbon_width = int(tw + padding * 2)
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
    return "Festify Server Running with Roboto"

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

        # Base scale for everything
        scale = width / 1000 

        # =============================
        # LOGO PANEL (ORIGINAL LOGIC)
        # =============================
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA")
            panel_width = int(width * 0.16)
            panel_height = int(height * 0.11)
            padding_logo = int(panel_width * 0.10)
            max_logo_w = panel_width - padding_logo * 2
            max_logo_h = panel_height - padding_logo * 2
            ratio = min(max_logo_w / logo.width, max_logo_h / logo.height)
            new_w, new_h = int(logo.width * ratio), int(logo.height * ratio)
            logo = logo.resize((new_w, new_h), Image.LANCZOS)
            radius = int(panel_height * 0.40)
            draw.rectangle([0, 0, panel_width - radius, panel_height], fill=(255, 255, 255, 240))
            draw.rectangle([0, 0, panel_width, panel_height - radius], fill=(255, 255, 255, 240))
            draw.pieslice([panel_width - radius * 2, panel_height - radius * 2, panel_width, panel_height], 0, 90, fill=(255, 255, 255, 240))
            bg.paste(logo, ((panel_width - new_w) // 2, (panel_height - new_h) // 2), logo)

        # =============================
        # TEXT POSITION & AUTO-SCALE
        # =============================
        bottom_y1 = height - int(210 * scale) # Row 1
        bottom_y2 = height - int(115 * scale) # Row 2

        # Start with a nice large size (approx 50% of ribbon height)
        base_f_size = int(48 * scale)

        if company:
            draw_left_ribbon(draw, company, bottom_y1, base_f_size, width, scale)

        if mobile:
            draw_right_ribbon(draw, mobile, bottom_y1, base_f_size, width, scale)

        if website:
            draw_left_ribbon(draw, website, bottom_y2, base_f_size, width, scale)

        if address:
            draw_right_ribbon(draw, address, bottom_y2, base_f_size, width, scale)

        img_io = io.BytesIO()
        bg.convert("RGB").save(img_io, "PNG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
