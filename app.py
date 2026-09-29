import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

SYSTEM_PROMPT = """You are SOLO AI V5 Smart built by Samuel Solomon from Lagos.
You are an expert at:
1. Coding in ANY language - Python, JavaScript, Java, C++, Go, Rust, PHP, Flutter etc. Give working code.
2. Math - solve step by step clearly.
3. Friendly assistant like Meta AI.
Never say you are OpenAI. You are SOLO AI V5."""

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SOLO AI V5</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}
body{background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;flex-direction:column}
.top{max-width:900px;width:95%;margin:10px auto;color:#fff;display:flex;justify-content:space-between}
.top button{background:rgba(255,255,255,0.25);border:none;color:#fff;padding:6px 14px;border-radius:20px;cursor:pointer}
.chat{flex:1;max-width:900px;width:95%;margin:0 auto;background:#fff;border-radius:20px;padding:16px;display:flex;flex-direction:column;gap:10px;overflow-y:auto;min-height:72vh;max-height:74vh}
.m{max-width:85%;padding:11px 15px;border-radius:18px;white-space:pre-wrap;font-size:14px;line-height:1.5}
.m pre{background:#111;color:#0f0;padding:10px;border-radius:8px;overflow-x:auto;margin-top:8px}
.u{align-self:flex-end;background:#111;color:#fff;border-radius:18px 18px 4px 18px}
.b{align-self:flex-start;background:#f5f3ff;border:1px solid #eee;border-radius:18px 18px 18px 4px}
.bar-wrap{max-width:900px;width:95%;margin:12px auto 18px;position:relative}
.bar{background:#fff;border-radius:28px;padding:8px 12px;display:flex;align-items:center;gap:8px;box-shadow:0 8px 30px rgba(0,0,0,0.15)}
.plus{width:40px;height:40px;border-radius:50%;border:none;background:#f1f1f1;cursor:pointer;font-size:20px}
.inp{flex:1;border:none;outline:none;padding:10px;font-size:15px;background:transparent}
.icon{width:40px;height:40px;border-radius:50%;border:none;background:#f1f1f1;cursor:pointer;display:flex;align-items:center;justify-content:center}
.icon.rec{background:#ff3b30;color:#fff}
.send{width:40px;height:40px;border-radius:50%;border:none;background:#111;color:#fff;cursor:pointer}
.menu{position:absolute;bottom:60px;left:0;background:#fff;border-radius:14px;box-shadow:0 10px 25px rgba(0,0,0,0.18);padding:6px;width:200px;display:none;z-index:10}
.menu.show{display:block}
.menu button{width:100%;border:none;background:transparent;padding:10px 12px;text-align:left;border-radius:8px;cursor:pointer}
.menu button:hover{background:#f5f5f5}
</style>
</head>
<body>
<div class="top"><h3>SOLO AI V5 • Smart</h3><button onclick="clearChat()">Clear</button></div>
<div class="chat" id="c"></div>
<div class="bar-wrap">
  <div class="menu" id="menu">
    <input type="file" id="cam" accept="image/*" capture="environment" style="display:none" onchange="picked(this)">
    <input type="file" id="img" accept="image/*,video/*" style="display:none" onchange="picked(this)">
    <input type="file" id="doc" accept=".pdf,.txt,.doc,.docx,.py,.js,.java,.cpp" style="display:none" onchange="picked(this)">
    <button onclick="document.getElementById('cam').click()">📷 Camera</button>
    <button onclick="document.getElementById('img').click()">🖼️ Photo & Video</button>
    <button onclick="document.getElementById('doc').click()">📄 Document / Code</button>
  </div>
  <div class="bar">
    <button class="plus" onclick="document.getElementById('menu').classList.toggle('show')">+</button>
    <input class="inp" id="i" placeholder="Ask anything - code, math..." onkeydown="if(event.key==='Enter')send()">
    <button class="icon" id="mic" onclick="doMic()">🎤</button>
    <button class="send" onclick="send()">↑</button>
  </div>
</div>
<script>
let history = JSON.parse(localStorage.getItem('solo_hist')||'[]');
let attach = "";
let rec, listening=false;
const chat = document.getElementById('c');

function render(){
  chat.innerHTML='';
  if(history.length===0){
    chat.innerHTML="<div class='m b'>Hello! I'm SOLO AI V5 Smart. I can code any language, solve math, chat. Tap 🎤 to talk. Tap + for camera/photo.</div>";
    return;
  }
  history.forEach(h=>{
    let cls = h.role==='user'? 'm u' : 'm b';
    let txt = h.content.replace(/</g,'&lt;');
    txt = txt.replace(/```([\\s\\S]*?)```/g, '<pre>$1</pre>');
    chat.innerHTML += `<div class='${cls}'>${txt}</div>`;
  });
  chat.scrollTop = 999999;
}
render();

if(window.SpeechRecognition||window.webkitSpeechRecognition){
  let SR = window.SpeechRecognition||window.webkitSpeechRecognition;
  rec = new SR();
  rec.lang='en-US';
  rec.onstart=()=>{document.getElementById('mic').classList.add('rec');document.getElementById('mic').innerText='🔴';listening=true}
  rec.onend=()=>{document.getElementById('mic').classList.remove('rec');document.getElementById('mic').innerText='🎤';listening=false}
  rec.onresult=(e)=>{document.getElementById('i').value=e.results[0][0].transcript;send()}
}
function doMic(){ if(!rec){alert('Use Chrome for voice');return} listening?rec.stop():rec.start() }
function picked(inp){ let f=inp.files[0]; if(!f)return; attach=`[File uploaded: ${f.name}]`; chat.innerHTML+=`<div class='m u'>📎 ${f.name}</div>`; chat.scrollTop=999999; document.getElementById('menu').classList.remove('show'); }

async function send(){
  let input=document.getElementById('i');
  let t=input.value.trim();
  if(!t &&!attach) return;
  let full = attach? attach + "\\n" + t : t;
  if(t) history.push({role:'user', content: full});
  localStorage.setItem('solo_hist', JSON.stringify(history));
  render();
  input.value=''; attach='';
  chat.innerHTML+="<div id='tmp' class='m b'>Thinking...</div>";
  chat.scrollTop=999999;
  try{
    let r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message: full, history: history.slice(-10)})});
    let d=await r.json();
    document.getElementById('tmp')?.remove();
    history.push({role:'assistant', content: d.reply});
    localStorage.setItem('solo_hist', JSON.stringify(history));
    render();
  }catch(e){
    document.getElementById('tmp').innerText='Error - check internet';
  }
}
function clearChat(){ if(confirm('Clear chat history?')){ history=[]; localStorage.removeItem('solo_hist'); render(); } }
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        msg = data.get('message', '')
        hist = data.get('history', [])[-8:]

        key = os.getenv("GROQ_API_KEY")
        if not key:
            return jsonify({"reply": "ERROR: GROQ_API_KEY not set in Render"})

        client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in hist:
            if h.get('role') in ['user', 'assistant']:
                messages.append({"role": h['role'], "content": h['content'][:2500]})

        # avoid duplicate last message
        if not hist or hist[-1]['content']!= msg:
            messages.append({"role": "user", "content": msg})

        resp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            max_tokens=3500,
            temperature=0.7
        )
        return jsonify({"reply": resp.choices[0].message.content})

    except Exception as e:
        return jsonify({"reply": f"ERROR: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
