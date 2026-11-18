import os
import itertools
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

# دیاریکردنی ڕێڕەوی سەرەکی پڕۆژەکە بۆ ئەوەی index.html بە تنهایی بخوێنرێتەوە
app = Flask(__name__, template_folder='.', static_folder='.')

# کۆکردنەوەی کلیلەکان بە شێوازێکی پارێزراو
api_list = []

# زیادکردنی کلیلەکانی Gemini ئەگەر هەبن
for i in range(1, 11):
    key = os.getenv(f"GEMINI_KEY_{i}")
    if key:
        api_list.append({"type": "gemini", "key": key})

# زیادکردنی کلیلەکانی Groq ئەگەر هەبن
for i in range(1, 10):
    key = os.getenv(f"GROQ_KEY_{i}")
    if key:
        api_list.append({"type": "groq", "key": key})

# زیادکردنی کلیلەکانی OpenRouter ئەگەر هەبن
for i in range(1, 11):
    key = os.getenv(f"OPENROUTER_KEY_{i}")
    if key:
        api_list.append({"type": "openrouter", "key": key})

# کلیلی Cohere
cohere_key = os.getenv("COHERE_KEY")
if cohere_key:
    api_list.append({"type": "cohere", "key": cohere_key})

# ئەگەر هیچ کلیلێک نەدۆزرایەوە
if api_list:
    massive_api_pool = itertools.cycle(api_list)
else:
    massive_api_pool = None

def call_luma_factory(prompt):
    if not massive_api_pool:
        return "❌ هیچ کلیلێکی API لە سێرڤەردا نەدۆزراوەتەوە! تکایە سەیری Variables بکە."
        
    total_attempts = len(api_list) if api_list else 10
    for _ in range(total_attempts):
        item = next(massive_api_pool)
        provider = item["type"]
        key = item["key"]
        
        try:
            if provider == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                if res.status_code == 200:
                    return res.json()['candidates'][0]['content']['parts'][0]['text']
                    
            elif provider == "groq":
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {key}"}
                payload = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}]}
                res = requests.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    return res.json()['choices'][0]['message']['content']

            elif provider == "openrouter":
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {"Authorization": f"Bearer {key}"}
                payload = {"model": "deepseek/deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
                res = requests.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    return res.json()['choices'][0]['message']['content']

            elif provider == "cohere":
                url = "https://api.cohere.ai/v1/generate"
                headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
                payload = {"model": "command", "prompt": prompt, "max_tokens": 300}
                res = requests.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    return res.json()['generations'][0]['text']
        except Exception:
            continue
            
    return "❌ هەموو کلیلەکانی کارگە سەرقاڵن یان کێشەیان هەیە، تکایە کەمێک چاوەڕێ بکە!"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    ai_response = call_luma_factory(user_message)
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
