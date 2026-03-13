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
# DYNAMIC FONT LOADER
# =============================
def get_font(size):
    # Try the uploaded Roboto font first
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
RIBBON_COLOR = (31, 42, 68, 240) # Slightly darker for better readability
TEXT_COLOR = (246, 215, 118)

# =============================
# AUTO-ADJUSTING RIBBON LOGIC
# =============================

def draw_smart_ribbon(draw, text, y, base_font_size, img_width, scale, side="left"):
    # Constraints
    max_ribbon_width = int(img_width * 0.46) # Ribbons can't take more than 46% of width
    padding_side = int(35 * scale)
    ribbon_height = int(75 * scale)
    cut = int(35 * scale)
    
    # Dynamic Font Scaling for long text
    current_font_size = base_font_size
    font = get_font(current_font_size)
    text_w = draw.textlength(text, font=font)
    
    # If text is too long, shrink font until it fits
    while text_w + (padding_side * 2) > max_ribbon_width and current_font_size > int(20 * scale):
        current_font_size -= 2
        font = get_font(current_font_size)
        text_w = draw.textlength(text, font=font)

    ribbon_width = int(text_w + padding_side * 2)

    if side == "left":
        points = [(0, y), (ribbon_width, y), (ribbon_width + cut, y + ribbon_height / 2), (ribbon_width, y + ribbon_height), (0, y + ribbon_height)]
        draw.polygon(points, fill=RIBBON_COLOR)
        draw.text((padding_side, y + ribbon_height / 2), text, font=font, fill=TEXT_COLOR, anchor="lm")
    else:
        start_x = img_width - ribbon_width
        points = [(start_x, y), (img_width, y), (img_width, y + ribbon_height), (start_x, y + ribbon_height), (start_x - cut, y + ribbon_height / 2)]
        draw.polygon(points, fill=RIBBON_COLOR)
        draw.text((img_width - padding_side, y + ribbon_height / 2), text, font=font, fill=TEXT_COLOR, anchor="rm")

@app.route("/")
def home():
    return "Festify Smart Generator Running"

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

        # LOGO PANEL (ORIGINAL)
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

        # TEXT ARRANGEMENT
        # y1 = top row, y2 = bottom row
        y1 = height - int(210 * scale)
        y2 = height - int(115 * scale)

        base_font_size = int(48 * scale)

        # Draw left and right ribbons with auto-shrink font logic
        if company:
            draw_smart_ribbon(draw, company, y1, base_font_size, width, scale, "left")
        if mobile:
            draw_smart_ribbon(draw, mobile, y1, base_font_size, width, scale, "right")
        if website:
            draw_smart_ribbon(draw, website, y2, base_font_size, width, scale, "left")
        if address:
            draw_smart_ribbon(draw, address, y2, base_font_size, width, scale, "right")

        img_io = io.BytesIO()
        bg.convert("RGB").save(img_io, "PNG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
