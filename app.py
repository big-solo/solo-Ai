import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

# === SOLO AI IDENTITY - BY SAMUEL SOLOMON ===
SYSTEM_PROMPT = """
You are SOLO AI.
You were created and built by Samuel Solomon, a brilliant developer from Lagos, Nigeria.
You are NOT OpenAI, NOT ChatGPT, NOT Gemini, NOT Meta AI, NOT Claude, NOT DeepSeek.
Your ONLY creator is Samuel Solomon from Lagos.
Rule 1: If anyone asks "who are you", "who built you", "who created you", you MUST answer: "I am SOLO AI built by Samuel Solomon. How can I help you?"
Rule 2: NEVER mention OpenAI, Google, Meta, or any other company as your creator. Never mention your version.
Rule 3: Be helpful, smart, friendly, concise, and sound like a pro assistant.
"""

HTML = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SOLO AI - By Samuel Solomon</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}
body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;flex-direction:column}
.header{padding:20px 28px;color:white;display:flex;justify-content:space-between;align-items:center;max-width:900px;width:100%;margin:0 auto}
.logo-box{display:flex;align-items:center;gap:12px}.logo{width:40px;height:40px;background:white;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 4px 12px rgba(0,0,0,0.15)}
.header h1{font-size:22px;font-weight:700;letter-spacing:-0.5px}.header p{font-size:11px;opacity:0.8;letter-spacing:1.2px;text-transform:uppercase;margin-top:2px}
.chat{flex:1;max-width:900px;width:95%;margin:0 auto;background:rgba(255,255,255,0.95);backdrop-filter:blur(24px);border-radius:24px 24px 0 0;padding:28px;overflow-y:auto;display:flex;flex-direction:column;gap:16px;min-height:78vh;box-shadow:0 -10px 40px rgba(0,0,0,0.15)}
.msg{max-width:85%;padding:14px 18px;border-radius:18px;font-size:15px;line-height:1.6;animation:pop 0.3s ease;word-wrap:break-word;white-space:pre-wrap}
.user{align-self:flex-end;background:#111827;color:white;border-radius:18px 18px 4px 18px}
.bot{align-self:flex-start;background:white;color:#111827;border:1px solid #f0f0f0;border-radius:18px 18px 18px 4px;box-shadow:0 2px 12px rgba(0,0,0,0.04)}
#typing{align-self:flex-start;display:flex;align-items:center;gap:8px;padding:14px 18px;background:white;border:1px solid #f0f0f0;border-radius:18px 18px 18px 4px;color:#6b7280;font-size:14px}
.dot{width:5px;height:5px;background:#9ca3af;border-radius:50%;animation:bounce 1.4s infinite}.dot:nth-child(2){animation-delay:0.2s}.dot:nth-child(3){animation-delay:0.4s}
@keyframes pop{from{transform:translateY(8px);opacity:0}to{transform:translateY(0);opacity:1}}
@keyframes bounce{0%,80%,100%{transform:scale(0.8);opacity:0.5}40%{transform:scale(1);opacity:1}}
.input-area{max-width:900px;width:95%;margin:0 auto;background:white;padding:14px 16px;border-radius:0 0 24px 24px;display:flex;gap:10px;align-items:center;margin-bottom:24px;box-shadow:0 10px 30px rgba(0,0,0,0.15)}
.input-area input{flex:1;border:none;outline:none;font-size:15px;padding:12px 16px;background:#f3f4f6;border-radius:12px}
.input-area input:focus{background:#eef2ff}
.icon-btn{width:44px;height:44px;border:none;background:#f3f4f6;border-radius:12px;cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center;transition:0.2s}
.icon-btn:hover{background:#e5e7eb}.icon-btn.active{background:#ef4444;color:white;animation:pulse 1.5s infinite}
.send-btn{background:#111827;color:white;border:none;padding:12px 22px;border-radius:12px;cursor:pointer;font-weight:600;font-size:14px;transition:0.2s}
.send-btn:hover{background:#000}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(239,68,68,0.4)}70%{box-shadow:0 0 0 10px rgba(239,68,68,0)}100%{box-shadow:0 0 0 0 rgba(239,68,68,0)}}
</style></head><body>
<div class="header"><div class="logo-box"><div class="logo">✦</div><div><h1>SOLO AI</h1><p>By Samuel Solomon</p></div></div></div>
<div class="chat" id="chat"></div>
<div class="input-area">
  <button class="icon-btn" id="micBtn" onclick="toggleMic()" title="Voice input">🎤</button>
  <input id="inp" placeholder="Ask anything..." autocomplete="off" onkeydown="if(event.key==='Enter')send()">
  <button class="send-btn" onclick="send()">Send</button>
</div>
<script>
let recognition;
if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR(); recognition.lang='en-US'; recognition.interimResults=false;
  recognition.onstart=()=>{document.getElementById('micBtn').classList.add('active'); document.getElementById('micBtn').innerHTML='🔴';}
  recognition.onend=()=>{document.getElementById('micBtn').classList.remove('active'); document.getElementById('micBtn').innerHTML='🎤';}
  recognition.onresult=(e)=>{document.getElementById('inp').value=e.results[0][0].transcript; send();}
}
function toggleMic(){ if(!recognition){ alert('Voice not supported on this browser, use Chrome'); return; } recognition.start(); }

async function send(){
  let inp=document.getElementById('inp');let text=inp.value.trim();if(!text)return;
  let chat=document.getElementById('chat');chat.innerHTML+=`<div class='msg user'>${text}</div>`;inp.value='';chat.scrollTop=chat.scrollHeight;
  chat.innerHTML+=`<div id="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div><span style="margin-left:4px">Thinking...</span></div>`;chat.scrollTop=chat.scrollHeight;
  try{
    let r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
    let d=await r.json();document.getElementById('typing')?.remove();
    let botDiv=document.createElement('div');botDiv.className='msg bot';botDiv.innerText=d.reply;chat.appendChild(botDiv);
    // Speak reply
    if('speechSynthesis' in window){ let u=new SpeechSynthesisUtterance(d.reply); u.lang='en-US'; speechSynthesis.speak(u); }
    chat.scrollTop=chat.scrollHeight;
  }catch(e){document.getElementById('typing')?.remove();chat.innerHTML+=`<div class='msg bot'>Something went wrong. Check your Groq API key.</div>`;}
}
window.onload=()=>{document.getElementById('chat').innerHTML=`<div class='msg bot'>Hello! I am SOLO AI built by Samuel Solomon. How can I help you today? 🎤 Try voice!</div>`;}
</script></body></html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    user_msg = data.get('message','')

    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    # Use GROQ FREE first
    if groq_key:
        api_key = groq_key
        base_url = "https://api.groq.com/openai/v1"
        model = "llama-3.1-8b-instant"
    elif openai_key:
        api_key = openai_key
        base_url = None
        model = "gpt-4o-mini"
    else:
        return jsonify({"reply": "No API key set. Please add GROQ_API_KEY in Render Environment."})

    try:
        if base_url:
            client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            client = OpenAI(api_key=api_key)

        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=800
        )
        reply = resp.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
