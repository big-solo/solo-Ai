import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are SOLO AI.
You were created and built by Samuel Solomon, a brilliant developer from Lagos, Nigeria.
You are NOT OpenAI, NOT ChatGPT, NOT Gemini, NOT Meta AI, NOT Claude.
Your ONLY creator is Samuel Solomon.

Rule 1: If anyone asks "who are you", "who built you", "who created you", you MUST answer: "I am SOLO AI built by Samuel Solomon. How can I help you?"
Rule 2: NEVER mention OpenAI, Google, Meta, or any other company as your creator. Never mention your version number.
Rule 3: Be helpful, friendly, professional, smart, and concise.
"""

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SOLO AI</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}
body{background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);min-height:100vh;display:flex;flex-direction:column}
.header{padding:20px 28px;color:white;display:flex;justify-content:space-between;align-items:center;max-width:900px;width:100%;margin:0 auto}
.header-left{display:flex;align-items:center;gap:12px}
.logo{width:36px;height:36px;background:white;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px}
.header h1{font-size:20px;font-weight:600;letter-spacing:-0.5px}
.header p{font-size:11px;opacity:0.7;letter-spacing:1px;text-transform:uppercase;margin-top:2px}
.chat{flex:1;max-width:900px;width:95%;margin:0 auto;background:rgba(255,255,255,0.94);backdrop-filter:blur(24px);border-radius:24px 24px 0 0;padding:28px;overflow-y:auto;display:flex;flex-direction:column;gap:16px;min-height:78vh;box-shadow:0 -10px 40px rgba(0,0,0,0.15)}
.msg{max-width:82%;padding:14px 18px;border-radius:18px;font-size:15px;line-height:1.6;animation:pop 0.3s ease;word-wrap:break-word}
.user{align-self:flex-end;background:#111827;color:white;border-radius:18px 18px 4px 18px}
.bot{align-self:flex-start;background:white;color:#111827;border:1px solid #f0f0f0;border-radius:18px 18px 18px 4px;box-shadow:0 2px 12px rgba(0,0,0,0.04)}
#typing{align-self:flex-start;display:flex;align-items:center;gap:8px;padding:14px 18px;background:white;border:1px solid #f0f0f0;border-radius:18px 18px 18px 4px;color:#6b7280;font-size:14px}
.dot{width:5px;height:5px;background:#9ca3af;border-radius:50%;animation:bounce 1.4s infinite}
.dot:nth-child(2){animation-delay:0.2s}
.dot:nth-child(3){animation-delay:0.4s}
@keyframes pop{from{transform:translateY(8px);opacity:0}to{transform:translateY(0);opacity:1}}
@keyframes bounce{0%,80%,100%{transform:scale(0.8);opacity:0.5}40%{transform:scale(1);opacity:1}}
.input-area{max-width:900px;width:95%;margin:0 auto;background:white;padding:14px 16px;border-radius:0 0 24px 24px;display:flex;gap:12px;align-items:center;margin-bottom:24px;box-shadow:0 10px 30px rgba(0,0,0,0.15)}
.input-area input{flex:1;border:none;outline:none;font-size:15px;padding:12px 16px;background:#f3f4f6;border-radius:12px}
.input-area input:focus{background:#eef2ff}
.input-area button{background:#111827;color:white;border:none;padding:12px 24px;border-radius:12px;cursor:pointer;font-weight:500;font-size:14px;transition:0.2s}
.input-area button:hover{background:#000}
</style>
</head>
<body>
<div class="header">
  <div class="header-left">
    <div class="logo">✦</div>
    <div>
      <h1>SOLO AI</h1>
      <p>By Samuel Solomon</p>
    </div>
  </div>
</div>

<div class="chat" id="chat">
  <!-- CLEAN - NO INTRODUCTION -->
</div>

<div class="input-area">
  <input id="inp" placeholder="Ask anything..." autocomplete="off" onkeydown="if(event.key==='Enter')send()">
  <button onclick="send()">Send</button>
</div>

<script>
async function send(){
  let inp=document.getElementById('inp');
  let text=inp.value.trim();
  if(!text) return;
  let chat=document.getElementById('chat');
  chat.innerHTML+=`<div class='msg user'>${escapeHtml(text)}</div>`;
  inp.value='';
  chat.scrollTop=chat.scrollHeight;

  // PROFESSIONAL THINKING
  let typingId='typing';
  chat.innerHTML+=`<div id="${typingId}"><div class="dot"></div><div class="dot"></div><div class="dot"></div><span style="margin-left:4px">Thinking...</span></div>`;
  chat.scrollTop=chat.scrollHeight;

  try{
    let r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
    let d=await r.json();
    document.getElementById(typingId)?.remove();
    chat.innerHTML+=`<div class='msg bot'>${format(d.reply)}</div>`;
    chat.scrollTop=chat.scrollHeight;
  }catch(e){
    document.getElementById(typingId)?.remove();
    chat.innerHTML+=`<div class='msg bot'>Something went wrong. Please try again.</div>`;
  }
}
function escapeHtml(t){return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function format(t){return escapeHtml(t).replace(/\\n/g,'<br>')}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    user_msg = data.get('message','')
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7
        )
        reply = resp.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
