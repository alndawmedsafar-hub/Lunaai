import os
import itertools
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# بارکردنی زانیارییەکان لە فایلی .env
load_dotenv()

app = Flask(__name__)

# کارگەی کلیلەکانی LumaAI بە شێوازێکی دینامیکی
massive_api_pool = itertools.cycle([
    # 1. کلیلەکانی Gemini (١٠ کلیل)
    {"type": "gemini", "key": os.getenv("GEMINI_KEY_1", "")},
    {"type": "gemini", "key": os.getenv("GEMINI_KEY_2", "")},
    {"type": "gemini", "key": os.getenv("GEMINI_KEY_3", "")},
    {"type": "gemini", "key": os.getenv("GEMINI_KEY_4", "")},
    {"type": "gemini", "key": os.getenv("GEMINI_KEY_5", "")},
    {"type": "gemini", "key": os.getenv("GEMINI_KEY_6", "")},
    {"type": "gemini", "key": os.getenv("GEMINI_KEY_7", "")},
    {"type": "gemini", "key": os.getenv("GEMINI_KEY_8", "")},
    {"type": "gemini", "key": os.getenv("GEMINI_KEY_9", "")},
    {"type": "gemini", "key": os.getenv("GEMINI_KEY_10", "")},
    
    # 2. کلیلەکانی Groq (٩ کلیل)
    {"type": "groq", "key": os.getenv("GROQ_KEY_1", "")},
    {"type": "groq", "key": os.getenv("GROQ_KEY_2", "")},
    {"type": "groq", "key": os.getenv("GROQ_KEY_3", "")},
    {"type": "groq", "key": os.getenv("GROQ_KEY_4", "")},
    {"type": "groq", "key": os.getenv("GROQ_KEY_5", "")},
    {"type": "groq", "key": os.getenv("GROQ_KEY_6", "")},
    {"type": "groq", "key": os.getenv("GROQ_KEY_7", "")},
    {"type": "groq", "key": os.getenv("GROQ_KEY_8", "")},
    {"type": "groq", "key": os.getenv("GROQ_KEY_9", "")},

    # 3. کلیلەکانی OpenRouter (١٠ کلیل)
    {"type": "openrouter", "key": os.getenv("OPENROUTER_KEY_1", "")},
    {"type": "openrouter", "key": os.getenv("OPENROUTER_KEY_2", "")},
    {"type": "openrouter", "key": os.getenv("OPENROUTER_KEY_3", "")},
    {"type": "openrouter", "key": os.getenv("OPENROUTER_KEY_4", "")},
    {"type": "openrouter", "key": os.getenv("OPENROUTER_KEY_5", "")},
    {"type": "openrouter", "key": os.getenv("OPENROUTER_KEY_6", "")},
    {"type": "openrouter", "key": os.getenv("OPENROUTER_KEY_7", "")},
    {"type": "openrouter", "key": os.getenv("OPENROUTER_KEY_8", "")},
    {"type": "openrouter", "key": os.getenv("OPENROUTER_KEY_9", "")},
    {"type": "openrouter", "key": os.getenv("OPENROUTER_KEY_10", "")},

    # 4. کلیلی Cohere
    {"type": "cohere", "key": os.getenv("COHERE_KEY", "")}
])

def call_luma_factory(prompt):
    total_attempts = 30
    for _ in range(total_attempts):
        item = next(massive_api_pool)
        provider = item["type"]
        key = item["key"]
        
        if not key:
            continue
            
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
