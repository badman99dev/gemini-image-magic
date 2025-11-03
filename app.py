import os
import google.generativeai as genai
from flask import Flask, request, render_template
import base64
from PIL import Image
import io

# Flask ऐप शुरू करो
app = Flask(__name__)

# अपनी API Key को Environment Variable से लो
# Render पर यह ऑटोमेटिकली सेट हो जाएगी
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # यह एरर लोकल टेस्टिंग के लिए है, Render पर key मौजूद होगी
        print("Warning: GEMINI_API_KEY environment variable not set. App might not work.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"API Key configuration error: {e}")

# हमारा मेन वेब पेज, जो index.html को दिखाएगा
@app.route('/')
def index():
    return render_template('index.html')

# इमेज बनाने वाला फंक्शन (जब यूजर "Generate Image" पर क्लिक करेगा)
@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        prompt = request.form['prompt']
        
        # हम 'gemini-1.5-flash-latest' का इस्तेमाल कर रहे हैं, जो तेज़ है
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # AI को प्रॉम्प्ट भेजो (यहाँ से mime_type हटा दिया गया है)
        response = model.generate_content(prompt)
        
        # AI से मिली इमेज को HTML में दिखाने के लिए Base64 में बदलो
        image_data = response.parts[0].inline_data.data
        img_base64 = base64.b64encode(image_data).decode('utf-8')

        # पेज को दोबारा दिखाओ, लेकिन इस बार इमेज के साथ
        return render_template('index.html', generated_image=img_base64, prompt=prompt)
    except Exception as e:
        # अगर कोई एरर आए, तो उसे पेज पर दिखाओ
        error_message = f"Image generation failed: {e}"
        print(error_message) # सर्वर लॉग में भी एरर प्रिंट करो
        return render_template('index.html', error=error_message)

# इमेज एडिट करने वाला फंक्शन (जब यूजर "Edit Image" पर क्लिक करेगा)
@app.route('/edit', methods=['POST'])
def edit_image():
    try:
        edit_prompt = request.form['edit_prompt']
        image_file = request.files.get('image_file')

        if not image_file:
            return render_template('index.html', error="No image file uploaded.")

        # अपलोड की गई इमेज को PIL फॉर्मेट में खोलो
        img = Image.open(image_file.stream)
        
        # एडिटिंग के लिए 'pro' मॉडल बेहतर है
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # AI को टेक्स्ट (प्रॉम्प्ट) और इमेज दोनों एक साथ भेजो
        response = model.generate_content([edit_prompt, img])
        
        # जवाब में मिली इमेज को Base64 में बदलो
        image_data = response.parts[0].inline_data.data
        img_base64 = base64.b64encode(image_data).decode('utf-8')

        # पेज को दोबारा दिखाओ, लेकिन इस बार एडिट की हुई इमेज के साथ
        return render_template('index.html', edited_image=img_base64, edit_prompt=edit_prompt)
    except Exception as e:
        # अगर कोई एरर आए, तो उसे पेज पर दिखाओ
        error_message = f"Image editing failed: {e}"
        print(error_message) # सर्वर लॉग में भी एरर प्रिंट करो
        return render_template('index.html', error=error_message)

# यह सुनिश्चित करता है कि सर्वर सही तरीके से चले
if __name__ == '__main__':
    # Render.com इस हिस्से का इस्तेमाल नहीं करता, यह सिर्फ लोकल टेस्टिंग के लिए है
    # Render सीधे 'gunicorn app:app' कमांड का इस्तेमाल करता है
    app.run(debug=True)
