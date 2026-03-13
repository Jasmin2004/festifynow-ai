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
# SERVER-SAFE FONT LOADER
# =============================
def get_font(size):
    # Railway/Linux standard font paths
    paths = [
        "DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "arial.ttf"
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()

# =============================
# COLORS
# =============================
RIBBON_COLOR = (31, 42, 68, 235)
TEXT_COLOR = (246, 215, 118)

# =============================
# RIBBON DRAWING (SCALED)
# =============================
def draw_left_ribbon(draw, text, y, font, scale):
    padding = int(40 * scale)
    ribbon_h = int(80 * scale)
    cut = int(40 * scale)
    
    # Get exact text width
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    ribbon_w = int(tw + padding * 2 + 30 * scale)

    points = [(0, y), (ribbon_w, y), (ribbon_w + cut, y + ribbon_h / 2), (ribbon_w, y + ribbon_h), (0, y + ribbon_h)]
    draw.polygon(points, fill=RIBBON_COLOR)
    # Using 'lm' (Left-Middle) anchor for vertical centering
    draw.text((padding, y + ribbon_h / 2), text, font=font, fill=TEXT_COLOR, anchor="lm")

def draw_right_ribbon(draw, text, y, font, img_w, scale):
    padding = int(40 * scale)
    ribbon_h = int(80 * scale)
    cut = int(40 * scale)
    
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    ribbon_w = int(tw + padding * 2 + 30 * scale)
    start_x = img_w - ribbon_w

    points = [(start_x, y), (img_w, y), (img_w, y + ribbon_h), (start_x, y + ribbon_h), (start_x - cut, y + ribbon_h / 2)]
    draw.polygon(points, fill=RIBBON_COLOR)
    # Using 'rm' (Right-Middle) anchor
    draw.text((img_w - padding, y + ribbon_h / 2), text, font=font, fill=TEXT_COLOR, anchor="rm")

@app.route("/")
def home():
    return "Poster Server Active"

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
            return jsonify({"error": "Template not found"}), 500

        bg = Image.open(bg_path).convert("RGBA")
        W, H = bg.size
        draw = ImageDraw.Draw(bg)

        # SCALE CALCULATION (Crucial for Server)
        # We assume 1000px is the base.
        scale = W / 1000

        # Logo Logic
        if logo_file:
            logo = Image.open(logo_file).convert("RGBA")
            p_w, p_h = int(W * 0.16), int(H * 0.11)
            logo.thumbnail((p_w * 0.8, p_h * 0.8), Image.Resampling.LANCZOS)
            draw.rounded_rectangle([0, 0, p_w, p_h], radius=int(20*scale), fill=(255, 255, 255, 255))
            bg.paste(logo, ((p_w - logo.size[0]) // 2, (p_h - logo.size[1]) // 2), logo)

        # FONT SIZES (Proportional to ribbon height)
        # If ribbon is 80px, font should be ~45-50px
        font_size = int(48 * scale)
        active_font = get_font(font_size)

        # Positions relative to bottom
        y1 = H - int(200 * scale)
        y2 = H - int(100 * scale)

        if company: draw_left_ribbon(draw, company, y1, active_font, scale)
        if mobile:  draw_right_ribbon(draw, mobile, y1, active_font, W, scale)
        if website: draw_left_ribbon(draw, website, y2, active_font, scale)
        if address: draw_right_ribbon(draw, address, y2, active_font, W, scale)

        img_io = io.BytesIO()
        bg.convert("RGB").save(img_io, "PNG")
        img_io.seek(0)
        return send_file(img_io, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
