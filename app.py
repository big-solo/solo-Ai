import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

SYSTEM_PROMPT = """
You are SOLO AI built by Samuel Solomon from Lagos.
If asked who built you: "I am SOLO AI built by Samuel Solomon. How can I help you?"
You can also solve maths calculations perfectly.
Never mention OpenAI or ChatGPT.
"""

HTML = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SOLO AI - By Samuel Solomon</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}
body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;flex-direction:column}
.header{padding:20px 28px;color:white;display:flex;justify-content:space-between;align-items:center;max-width:900px;width:100%;margin:0 auto}
.logo-box{display:flex;align-items:center;gap:12px}.logo{width:40px;height:40px;background:white;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px}
.header h1{font-size:22px;font-weight:700}.header p{font-size:11px;opacity:0.8;letter-spacing:1.2px;text-transform:uppercase}
.chat{flex:1;max-width:900px;width:95%;margin:0 auto;background:rgba(255,255,255,0.95);border-radius:24px 24px 0 0;padding:28px;overflow-y:auto;display:flex;flex-direction:column;gap:16px;min-height:78vh}
.msg{max-width:85%;padding:14px 18px;border-radius:18px;font-size:15px;line-height:1.6;white-space:pre-wrap}
.user{align-self:flex-end;background:#111827;color:white;border-radius:18px 18px 4px 18px}
.bot{align-self:flex-start;background:white;color:#111827;border:1px solid #f0f0f0;border-radius:18px 18px 18px 4px}
#typing{display:flex;gap:6px;padding:14px 18px;background:white;border-radius:18px;color:#666;font-size:14px}
.dot{width:5px;height:5px;background:#999;border-radius:50%;animation:bounce 1s infinite}
@keyframes bounce{0%,100%{opacity:0.3}50%{opacity:1}}
.input-area{max-width:900px;width:95%;margin:0 auto;background:white;padding:14px 16px;border-radius:0 0 24px 24px;display:flex;gap:10px;align-items:center;margin-bottom:24px}
.input-area input{flex:1;border:none;outline:none;font-size:15px;padding:12px 16px;background:#f3f4f6;border-radius:12px}
.icon-btn{width:44px;height:44px;border:none;background:#f3f4f6;border-radius:12px;cursor:pointer;font-size:18px}
.icon-btn.active{background:#ef4444;color:white}
.send-btn{background:#111827;color:white;border:none;padding:12px 22px;border-radius:12px;cursor:pointer;font-weight:600}
</style></head><body>
<div class="header"><div class="logo-box"><div class="logo">✦</div><div><h1>SOLO AI</h1><p>By Samuel Solomon</p></div></div></div>
<div class="chat" id="chat"></div>
<div class="input-area">
  <button class="icon-btn" id="micBtn" onclick="toggleMic()">🎤</button>
  <input id="inp" placeholder="Ask anything... (maths too)" onkeydown="if(event.key==='Enter')send()">
  <button class="send-btn" onclick="send()">Send</button>
</div>
<script>
let recognition;let listening=false;
if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  recognition=new SR();recognition.lang='en-US';
  recognition.onstart=()=>{document.getElementById('micBtn').classList.add('active');document.getElementById('micBtn').innerHTML='🔴';listening=true;}
  recognition.onend=()=>{document.getElementById('micBtn').classList.remove('active');document.getElementById('micBtn').innerHTML='🎤';listening=false;}
  recognition.onresult=(e)=>{document.getElementById('inp').value=e.results[0][0].transcript;send();}
}
function toggleMic(){if(!recognition){alert('Use Chrome');return;} listening?recognition.stop():recognition.start();}
async function send(){
  let inp=document.getElementById('inp');let text=inp.value.trim();if(!text)return;
  let chat=document.getElementById('chat');chat.innerHTML+=`<div class='msg user'>${text}</div>`;inp.value='';chat.scrollTop=chat.scrollHeight;
  chat.innerHTML+=`<div id="typing"><span class="dot"></span><span class="dot"></span> Thinking...</div>`;chat.scrollTop=chat.scrollHeight;
  try{
    let r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
    let d=await r.json();document.getElementById('typing')?.remove();
    let div=document.createElement('div');div.className='msg bot';div.innerText=d.reply;chat.appendChild(div);chat.scrollTop=chat.scrollHeight;
    if('speechSynthesis' in window){let u=new SpeechSynthesisUtterance(d.reply);speechSynthesis.speak(u);}
  }catch(e){document.getElementById('typing')?.remove();chat.innerHTML+=`<div class='msg bot'>Check GROQ key</div>`;}
}
window.onload=()=>{document.getElementById('chat').innerHTML=`<div class='msg bot'>Hello! I am SOLO AI built by Samuel Solomon. How can I help you today? 🎤</div>`;}
</script></body></html>
"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/api/chat', methods=['POST'])
def chat():
    msg = request.get_json().get('message','')
    groq_key = os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY") or os.getenv("GROQ")
    if not groq_key:
        return jsonify({"reply": "Add GROQ_API_KEY in Render"})
    client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
    try:
        # Try quick maths first
        if any(c in msg for c in "+-*/^%") and len(msg) < 30:
            try:
                # safe eval for simple maths
                allowed = set("0123456789+-*/().^% ")
                if all(ch in allowed for ch in msg):
                    result = eval(msg.replace("^","**"))
                    return jsonify({"reply": f"🧮 {msg} = {result}"})
            except: pass
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":msg}]
        )
        return jsonify({"reply": resp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
