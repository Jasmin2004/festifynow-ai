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
# FONT LOADER
# =============================
def get_font(size):
    font_filename = "Roboto-VariableFont_wdth,wght.ttf"
    base_path = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_path, font_filename)
    try:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()

# =============================
# COLORS
# =============================
RIBBON_COLOR = (31, 42, 68, 255) # Deep Blue
TEXT_COLOR = (246, 215, 118)    # Golden Yellow

# =============================
# PREMIUM RIBBON LOGIC (Matches 2nd Image)
# =============================

def draw_premium_ribbon(draw, text, y, base_size, img_width, scale, side="left"):
    # Constraints
    max_w = int(img_width * 0.48) 
    padding = int(40 * scale)
    ribbon_h = int(90 * scale) # Slightly taller for premium look
    cut = int(45 * scale)      # Deeper cut
    
    # Auto-resize text
    curr_size = base_size
    font = get_font(curr_size)
    tw = draw.textlength(text, font=font)
    
    while (tw + padding * 2 + cut) > max_w and curr_size > int(18 * scale):
        curr_size -= 2
        font = get_font(curr_size)
        tw = draw.textlength(text, font=font)

    ribbon_w = int(tw + padding * 2)

    if side == "left":
        # Ribbon starts at 0, triangle points right
        points = [
            (0, y), 
            (ribbon_w, y), 
            (ribbon_w + cut, y + ribbon_h / 2), 
            (ribbon_w, y + ribbon_h), 
            (0, y + ribbon_h)
        ]
        draw.polygon(points, fill=RIBBON_COLOR)
        draw.text((padding, y + ribbon_h / 2), text, font=font, fill=TEXT_COLOR, anchor="lm")
    else:
        # Ribbon ends at img_width, triangle points left
        start_x = img_width - ribbon_w
        points = [
            (start_x, y), 
            (img_width, y), 
            (img_width, y + ribbon_h), 
            (start_x, y + ribbon_h), 
            (start_x - cut, y + ribbon_h / 2)
        ]
        draw.polygon(points, fill=RIBBON_COLOR)
        draw.text((img_width - padding, y + ribbon_h / 2), text, font=font, fill=TEXT_COLOR, anchor="rm")

@app.route("/")
def home():
    return "Poster Generator Ready"

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
        bg = Image.open(bg_path).convert("RGBA")
        width, height = bg.size
        draw = ImageDraw.Draw(bg)
        scale = width / 1000 

        # =============================
        # LOGO PANEL (AS IS)
        # =============================
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA")
            p_w, p_h = int(width * 0.16), int(height * 0.11)
            p_pad = int(p_w * 0.10)
            ratio = min((p_w - p_pad*2) / logo.width, (p_h - p_pad*2) / logo.height)
            new_w, new_h = int(logo.width * ratio), int(logo.height * ratio)
            logo = logo.resize((new_w, new_h), Image.LANCZOS)
            radius = int(p_h * 0.40)
            draw.rectangle([0, 0, p_w - radius, p_h], fill=(255, 255, 255, 240))
            draw.rectangle([0, 0, p_w, p_h - radius], fill=(255, 255, 255, 240))
            draw.pieslice([p_w - radius * 2, p_h - radius * 2, p_w, p_h], 0, 90, fill=(255, 255, 255, 240))
            bg.paste(logo, ((p_w - new_w) // 2, (p_h - new_h) // 2), logo)

        # =============================
        # TEXT POSITIONING (EXACT MATCH)
        # =============================
        # y1 is the row for Company & Mobile
        # y2 is the row for Website & Address (closer to the bottom)
        y2 = height - int(110 * scale)
        y1 = y2 - int(115 * scale) # Gap between rows

        base_f_size = int(45 * scale)

        if company:
            draw_premium_ribbon(draw, company.upper(), y1, base_f_size, width, scale, "left")
        if mobile:
            draw_premium_ribbon(draw, mobile, y1, base_f_size, width, scale, "right")
        if website:
            draw_premium_ribbon(draw, website.lower(), y2, base_f_size, width, scale, "left")
        if address:
            draw_premium_ribbon(draw, address, y2, base_f_size, width, scale, "right")

        img_io = io.BytesIO()
        bg.convert("RGB").save(img_io, "PNG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
