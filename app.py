import os
import google.generativeai as genai
from flask import Flask, request, render_template, Response
import base64
from PIL import Image
import io

# Flask ऐप शुरू करो
app = Flask(__name__)

# अपनी API Key को Environment Variable से लो
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"API Key configuration error: {e}")

# हमारा मेन पेज
@app.route('/')
def index():
    return render_template('index.html')

# इमेज बनाने वाला फंक्शन
@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        prompt = request.form['prompt']
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "image/png"})
        
        # इमेज डेटा को Base64 में बदलो ताकि HTML में दिखा सकें
        image_data = response.parts[0].inline_data.data
        img_base64 = base64.b64encode(image_data).decode('utf-8')

        return render_template('index.html', generated_image=img_base64, prompt=prompt)
    except Exception as e:
        return render_template('index.html', error=f"Image generation failed: {e}")

# इमेज एडिट करने वाला फंक्शन
@app.route('/edit', methods=['POST'])
def edit_image():
    try:
        edit_prompt = request.form['edit_prompt']
        image_file = request.files['image_file']

        # अपलोड की गई इमेज को PIL फॉर्मेट में खोलो
        img = Image.open(image_file.stream)
        
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # AI को इमेज और प्रॉम्प्ट दोनों भेजो
        response = model.generate_content([edit_prompt, img])
        
        # जवाब में से इमेज डेटा को Base64 में बदलो
        image_data = response.parts[0].inline_data.data
        img_base64 = base64.b64encode(image_data).decode('utf-8')

        return render_template('index.html', edited_image=img_base64, edit_prompt=edit_prompt)
    except Exception as e:
        return render_template('index.html', error=f"Image editing failed: {e}")

if __name__ == '__main__':
    # Render इसे खुद मैनेज करेगा, यह सिर्फ लोकल टेस्टिंग के लिए है
    app.run(host="0.0.0.0", port=5000, debug=True)
