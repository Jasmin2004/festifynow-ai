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

# ==========================================
# FIXED FONT LOADER (Uses Linux System Fonts)
# ==========================================
def get_font(size):
    # Railway Linux standard font paths
    linux_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "DejaVuSans-Bold.ttf"
    ]
    
    for path in linux_fonts:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
                
    return ImageFont.load_default()

RIBBON_COLOR = (31, 42, 68, 230)
TEXT_COLOR = (246, 215, 118)

# ==========================================
# RIBBON DRAWING FUNCTIONS
# ==========================================
def draw_left_ribbon(draw, text, y, font, scale):
    padding_side = int(30 * scale)
    ribbon_height = int(70 * scale) 
    cut = int(35 * scale)

    text_width = draw.textlength(text, font=font)
    ribbon_width = int(text_width + padding_side * 2)

    points = [(0, y), (ribbon_width, y), (ribbon_width + cut, y + ribbon_height / 2), (ribbon_width, y + ribbon_height), (0, y + ribbon_height)]
    draw.polygon(points, fill=RIBBON_COLOR)
    draw.text((padding_side, y + ribbon_height / 2), text, font=font, fill=TEXT_COLOR, anchor="lm")

def draw_right_ribbon(draw, text, y, font, img_width, scale):
    padding_side = int(30 * scale)
    ribbon_height = int(70 * scale) 
    cut = int(35 * scale)

    text_width = draw.textlength(text, font=font)
    ribbon_width = int(text_width + padding_side * 2)
    start_x = img_width - ribbon_width

    points = [(start_x, y), (img_width, y), (img_width, y + ribbon_height), (start_x, y + ribbon_height), (start_x - cut, y + ribbon_height / 2)]
    draw.polygon(points, fill=RIBBON_COLOR)
    draw.text((img_width - padding_side, y + ribbon_height / 2), text, font=font, fill=TEXT_COLOR, anchor="rm")

@app.route("/")
def home():
    return "Festify Server Running"

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

        # Base scale
        scale = width / 1000 

        # =============================
        # LOGO PANEL (ORIGINAL LOGIC)
        # =============================
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA")
            panel_width = int(width * 0.16)
            panel_height = int(height * 0.11)
            p_pad = int(panel_width * 0.10)
            max_logo_w = panel_width - p_pad * 2
            max_logo_h = panel_height - p_pad * 2
            ratio = min(max_logo_w / logo.width, max_logo_h / logo.height)
            new_w, new_h = int(logo.width * ratio), int(logo.height * ratio)
            logo = logo.resize((new_w, new_h), Image.LANCZOS)
            radius = int(panel_height * 0.40)
            draw.rectangle([0, 0, panel_width - radius, panel_height], fill=(255, 255, 255, 240))
            draw.rectangle([0, 0, panel_width, panel_height - radius], fill=(255, 255, 255, 240))
            draw.pieslice([panel_width - radius * 2, panel_height - radius * 2, panel_width, panel_height], 0, 90, fill=(255, 255, 255, 240))
            bg.paste(logo, ((panel_width - new_w) // 2, (panel_height - new_h) // 2), logo)

        # =============================
        # TEXT POSITION & SIZE FIX
        # =============================
        bottom_y1 = height - int(200 * scale) 
        bottom_y2 = height - int(100 * scale) 

        # Font size calculation
        font_size = int(48 * scale)
        active_font = get_font(font_size)

        if company:
            draw_left_ribbon(draw, company, bottom_y1, active_font, scale)
        if mobile:
            draw_right_ribbon(draw, mobile, bottom_y1, active_font, width, scale)
        if website:
            draw_left_ribbon(draw, website, bottom_y2, active_font, scale)
        if address:
            # FIXED: Changed address_font to active_font
            draw_right_ribbon(draw, address, bottom_y2, active_font, width, scale)

        img_io = io.BytesIO()
        bg.convert("RGB").save(img_io, "PNG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
