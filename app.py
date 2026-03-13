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
# FONT LOADER (STRICT FIX)
# =============================
def get_font(size):
    # This must match your GitHub filename EXACTLY
    font_filename = "Roboto-VariableFont_wdth,wght.ttf"
    
    # Check multiple locations
    base_path = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(base_path, font_filename),
        os.path.join(os.getcwd(), font_filename),
        font_filename
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception as e:
                print(f"Error loading font at {path}: {e}")
                continue
    
    # If file not found, use system fallback to avoid tiny text
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

RIBBON_COLOR = (31, 42, 68, 230)
TEXT_COLOR = (246, 215, 118)

# =============================
# RIBBON FUNCTIONS
# =============================
def draw_left_ribbon(draw, text, y, font, scale):
    padding_side = int(35 * scale)
    ribbon_height = int(75 * scale) 
    cut = int(35 * scale)

    text_width = draw.textlength(text, font=font)
    ribbon_width = int(text_width + padding_side * 2)

    points = [(0, y), (ribbon_width, y), (ribbon_width + cut, y + ribbon_height / 2), (ribbon_width, y + ribbon_height), (0, y + ribbon_height)]
    draw.polygon(points, fill=RIBBON_COLOR)
    draw.text((padding_side, y + ribbon_height / 2), text, font=font, fill=TEXT_COLOR, anchor="lm")

def draw_right_ribbon(draw, text, y, font, img_width, scale):
    padding_side = int(35 * scale)
    ribbon_height = int(75 * scale) 
    cut = int(35 * scale)

    text_width = draw.textlength(text, font=font)
    ribbon_width = int(text_width + padding_side * 2)
    start_x = img_width - ribbon_width

    points = [(start_x, y), (img_width, y), (img_width, y + ribbon_height), (start_x, y + ribbon_height), (start_x - cut, y + ribbon_height / 2)]
    draw.polygon(points, fill=RIBBON_COLOR)
    draw.text((img_width - padding_side, y + ribbon_height / 2), text, font=font, fill=TEXT_COLOR, anchor="rm")

@app.route("/")
def home():
    return "Festify Server Active - Font Path Fixed"

@app.route("/check-font")
def check_font():
    font_filename = "Roboto-VariableFont_wdth,wght.ttf"
    return {
        "cwd": os.getcwd(),
        "file_exists_in_cwd": os.path.exists(font_filename),
        "files_present": os.listdir('.')
    }

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

        # TEXT POSITION & SIZE
        # Row 1 (Top)
        bottom_y1 = height - int(220 * scale) 
        # Row 2 (Bottom)
        bottom_y2 = height - int(110 * scale) 

        # SIZE: Increased to 52 for high visibility
        font_size = int(52 * scale)
        active_font = get_font(font_size)

        if company:
            draw_left_ribbon(draw, company, bottom_y1, active_font, scale)
        if mobile:
            draw_right_ribbon(draw, mobile, bottom_y1, active_font, width, scale)
        if website:
            draw_left_ribbon(draw, website, bottom_y2, active_font, scale)
        if address:
            draw_right_ribbon(draw, address, bottom_y2, active_font, width, scale)

        img_io = io.BytesIO()
        bg.convert("RGB").save(img_io, "PNG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
