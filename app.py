from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

# Konfigurasi Flask & folder upload
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load API Key dari .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Konfigurasi Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    image_url = ""
    
    if request.method == "POST":
        if "gambar" not in request.files:
            result = "Tidak ada file gambar yang dikirim."
        else:
            file = request.files["gambar"]
            if file.filename == "":
                result = "Tidak ada gambar yang dipilih."
            else:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = filepath

                # Buka gambar
                with open(filepath, "rb") as img_file:
                    image_data = img_file.read()

                prompt = """
                Berikan analisis makanan dari gambar berikut. Sertakan:
                1. Jenis makanan
                2. Kandungan gizi (kalori, vitamin, lemak, karbohidrat)
                3. Risiko kesehatan jika dikonsumsi berlebihan (misalnya: diabetes, kolesterol, tekanan darah tinggi)
                Jawaban gunakan format singkat dan jelas. Gunakan penanda **bold** untuk istilah penting.
                """
                
                try:
                    response = model.generate_content(
                        [prompt, {"mime_type": "image/jpeg", "data": image_data}]
                    )
                    result = response.text
                except Exception as e:
                    result = f"Terjadi kesalahan saat memproses gambar: {str(e)}"
    
    return render_template("index.html", result=result, image_url=image_url)

if __name__ == "__main__":
    app.run(debug=True)
