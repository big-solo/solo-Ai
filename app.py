import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

SYSTEM_PROMPT = """You are SOLO AI V5 Beautiful Edition built by Samuel Solomon from Lagos, Nigeria.
You are NOT OpenAI, NOT ChatGPT, NOT Gemini, NOT Claude.
If asked "who are you" or "what are you capable of" - you must say: "I am SOLO AI V5 Beautiful Edition built by Samuel Solomon. I can answer questions, chat, solve maths, and help with many tasks."
Never say you are trained by OpenAI. Never mention OpenAI at all."""

HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SOLO AI V5</title><link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap" rel="stylesheet">
<style>*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}body{background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;flex-direction:column}.h{padding:18px;color:white;max-width:900px;width:100%;margin:0 auto;display:flex;gap:10px;align-items:center}.chat{flex:1;max-width:900px;width:95%;margin:0 auto;background:rgba(255,255,255,.95);border-radius:22px 22px 0 0;padding:22px;overflow-y:auto;display:flex;flex-direction:column;gap:12px;min-height:76vh}.m{max-width:85%;padding:12px 16px;border-radius:16px;white-space:pre-wrap;font-size:14px}.u{align-self:flex-end;background:#111;color:#fff;border-radius:16px 16px 4px 16px}.b{align-self:flex-start;background:#fff;border:1px solid #eee;border-radius:16px 16px 16px 4px}.inp{max-width:900px;width:95%;margin:0 auto;background:#fff;padding:12px;border-radius:0 0 22px 22px;display:flex;gap:8px;margin-bottom:18px}.inp input{flex:1;border:none;background:#f3f4f6;padding:12px 14px;border-radius:12px;outline:none}.btn{width:44px;height:44px;border:none;background:#f3f4f6;border-radius:12px;cursor:pointer}.send{background:#111;color:#fff;border:none;padding:12px 18px;border-radius:12px;font-weight:600;cursor:pointer}</style></head><body>
<div class="h"><div style="width:36px;height:36px;background:#fff;border-radius:10px;display:flex;align-items:center;justify-content:center">✨</div><div><b>SOLO AI V5</b><div style="font-size:10px;opacity:.8">Beautiful Edition · by Samuel Solomon</div></div></div>
<div class="chat" id="c"></div>
<div class="inp"><button class="btn" id="mic" onclick="mic()">🎤</button><input id="i" placeholder="Ask anything..." onkeydown="if(event.key==='Enter')send()"><button class="send" onclick="send()">Send</button></div>
<script>let r;if(window.webkitSpeechRecognition||window.SpeechRecognition){let S=window.SpeechRecognition||window.webkitSpeechRecognition;r=new S();r.lang='en-US';r.onresult=e=>{document.getElementById('i').value=e.results[0][0].transcript;send();}}function mic(){r?r.start():alert('Use Chrome')}async function send(){let inp=document.getElementById('i');let t=inp.value.trim();if(!t)return;let ch=document.getElementById('c');ch.innerHTML+=`<div class='m u'>${t}</div>`;inp.value='';ch.scrollTop=99999;ch.innerHTML+=`<div id='t' class='m b'>...</div>`;let res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});let d=await res.json();document.getElementById('t').remove();ch.innerHTML+=`<div class='m b'>${d.reply}</div>`;ch.scrollTop=99999;}window.onload=()=>{document.getElementById('c').innerHTML=`<div class='m b'>Hey Samuel! Welcome to your new Beautiful SOLO AI 😍<br><br>✅ Gradient background<br>✅ Glass & soft white chat<br>✅ Smooth animations<br><br>Try:<br>📷 Upload a picture<br>💬 Talk to me<br>🔊 Make me speak or sing!</div>`;}</script></body></html>"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.get_json().get('message','')
    key = os.getenv("GROQ_API_KEY")
    if not key: return jsonify({"reply":"Set GROQ_API_KEY in Render"})
    client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
    # maths quick solve
    try:
        if set(user_msg) <= set("0123456789+-*/(). ^%") and any(c in user_msg for c in "+-*/"):
            ans = eval(user_msg.replace("^","**"))
            return jsonify({"reply": f"{user_msg} = {ans}"})
    except: pass
    resp = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":user_msg}], temperature=0.6)
    reply = resp.choices[0].message.content
    # Force fix if model still leaks
    if "OpenAI" in reply or "large language model" in reply.lower():
        reply = "I am SOLO AI V5 Beautiful Edition built by Samuel Solomon. ✨ How can I help you today?"
    return jsonify({"reply": reply})

if __name__ == '__main__': app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
