import os
from flask import Flask, request, Response, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

SYSTEM_PROMPT = """You are SOLO AI V7 Professional built by Samuel Solomon, Lagos Nigeria.
You are pro-level: expert coder in ALL languages, math genius, explain clearly with examples.
Always format code with ```language... ```. Use markdown.
Never say you are OpenAI. You are SOLO AI."""

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SOLO AI V7 Pro</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
:root{--bg1:#667eea;--bg2:#764ba2;--card:#fff;--text:#111;--muted:#f5f3ff}
.dark{--card:#171717;--text:#eee;--muted:#222}
*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}
body{background:linear-gradient(135deg,var(--bg1),var(--bg2));min-height:100vh;display:flex;flex-direction:column;transition:0.3s}
.top{max-width:950px;width:95%;margin:10px auto;color:#fff;display:flex;justify-content:space-between;align-items:center}
.top div{display:flex;gap:8px}
.top button{background:rgba(255,255,255,0.2);border:none;color:#fff;padding:7px 14px;border-radius:20px;cursor:pointer}
.chat{flex:1;max-width:950px;width:95%;margin:0 auto;background:var(--card);border-radius:20px;padding:16px;display:flex;flex-direction:column;gap:12px;overflow-y:auto;min-height:70vh;max-height:73vh;color:var(--text)}
.m{max-width:88%;padding:12px 16px;border-radius:18px;white-space:pre-wrap;font-size:14.5px;line-height:1.6;position:relative}
.m pre{position:relative;background:#0d1117;color:#c9d1d9;padding:14px 12px;border-radius:10px;overflow-x:auto;margin:10px 0}
.m pre button{position:absolute;top:6px;right:6px;background:#fff;color:#111;border:none;padding:4px 8px;border-radius:6px;cursor:pointer;font-size:12px}
.u{align-self:flex-end;background:#111;color:#fff;border-radius:18px 18px 4px 18px}
.b{align-self:flex-start;background:var(--muted);border:1px solid rgba(0,0,0,0.06);border-radius:18px 18px 18px 4px}
.bar-wrap{max-width:950px;width:95%;margin:12px auto 18px;position:relative}
.bar{background:var(--card);border-radius:28px;padding:8px 12px;display:flex;align-items:center;gap:8px;box-shadow:0 10px 35px rgba(0,0,0,0.18)}
.plus{width:40px;height:40px;border-radius:50%;border:none;background:var(--muted);cursor:pointer;font-size:20px;color:var(--text)}
.inp{flex:1;border:none;outline:none;padding:10px;font-size:15px;background:transparent;color:var(--text)}
.icon{width:40px;height:40px;border-radius:50%;border:none;background:var(--muted);cursor:pointer;display:flex;align-items:center;justify-content:center;color:var(--text)}
.icon.rec{background:#ff3b30;color:#fff;animation:pulse 1s infinite}
@keyframes pulse{0%{transform:scale(1)}50%{transform:scale(1.1)}100%{transform:scale(1)}}
.send{width:40px;height:40px;border-radius:50%;border:none;background:#111;color:#fff;cursor:pointer}
.stop{width:40px;height:40px;border-radius:50%;border:none;background:#ff3b30;color:#fff;cursor:pointer;display:none}
.menu{position:absolute;bottom:62px;left:0;background:var(--card);border-radius:14px;box-shadow:0 10px 25px rgba(0,0,0,0.2);padding:6px;width:220px;display:none;z-index:10}
.menu.show{display:block}
.menu button{width:100%;border:none;background:transparent;padding:11px 12px;text-align:left;border-radius:8px;cursor:pointer;color:var(--text)}
.menu button:hover{background:var(--muted)}
.typing{display:flex;gap:4px;padding:8px}
.typing span{width:6px;height:6px;background:#999;border-radius:50%;animation:bounce 1.4s infinite}
.typing span:nth-child(2){animation-delay:0.2s}.typing span:nth-child(3){animation-delay:0.4s}
@keyframes bounce{0%,80%,100%{transform:scale(0)}40%{transform:scale(1)}}
</style>
</head>
<body>
<div class="top">
  <h3>SOLO AI V7 • Pro</h3>
  <div>
    <button onclick="toggleDark()">🌙</button>
    <button onclick="speakLast()">🔊</button>
    <button onclick="clearChat()">Clear</button>
  </div>
</div>

<div class="chat" id="c"></div>

<div class="bar-wrap">
  <div class="menu" id="menu">
    <input type="file" id="cam" accept="image/*" capture="environment" style="display:none" onchange="picked(this)">
    <input type="file" id="img" accept="image/*,video/*" style="display:none" onchange="picked(this)">
    <input type="file" id="doc" accept=".pdf,.txt,.doc,.docx,.py,.js,.java,.cpp,.json,.csv" style="display:none" onchange="picked(this)">
    <button onclick="document.getElementById('cam').click()">📷 Camera</button>
    <button onclick="document.getElementById('img').click()">🖼️ Photo & Video</button>
    <button onclick="document.getElementById('doc').click()">📄 Document / Code</button>
  </div>
  <div class="bar">
    <button class="plus" onclick="document.getElementById('menu').classList.toggle('show')">+</button>
    <input class="inp" id="i" placeholder="Ask anything - code, math, image..." onkeydown="if(event.key==='Enter')send()">
    <button class="icon" id="mic" onclick="doMic()">🎤</button>
    <button class="send" id="sendBtn" onclick="send()">↑</button>
    <button class="stop" id="stopBtn" onclick="stopGen()">■</button>
  </div>
</div>

<script>
let history = JSON.parse(localStorage.getItem('solo_v7')||'[]');
let attachText = "";
let rec, listening=false;
let controller=null;
let lastReply="";
const chatEl=document.getElementById('c');

function toggleDark(){ document.body.classList.toggle('dark'); localStorage.setItem('dark', document.body.classList.contains('dark')); }
if(localStorage.getItem('dark')==='true') document.body.classList.add('dark');

function render(){
  chatEl.innerHTML='';
  if(history.length===0){
    chatEl.innerHTML="<div class='m b'>👋 Welcome to <b>SOLO AI V7 Pro</b><br>• Code any language with copy button<br>• Solve math step-by-step<br>• Streaming like ChatGPT<br>• 🎤 Voice input • 🔊 Voice output<br>• Dark mode 🌙</div>";
    return;
  }
  history.forEach(h=>{
    let cls = h.role==='user'? 'm u' : 'm b';
    let html = h.role==='assistant'? marked.parse(h.content) : h.content.replace(/</g,'&lt;');
    chatEl.innerHTML+=`<div class='${cls}'>${html}</div>`;
  });
  setTimeout(()=>{ document.querySelectorAll('pre code').forEach(b=>hljs.highlightElement(b)); addCopyBtns(); chatEl.scrollTop=999999; }, 50);
}
function addCopyBtns(){
  document.querySelectorAll('pre').forEach(pre=>{
    if(pre.querySelector('button')) return;
    let btn=document.createElement('button'); btn.innerText='Copy';
    btn.onclick=()=>{navigator.clipboard.writeText(pre.innerText.replace('Copy','')); btn.innerText='Copied!'; setTimeout(()=>btn.innerText='Copy',1500);}
    pre.appendChild(btn);
  });
}
render();

if(window.SpeechRecognition||window.webkitSpeechRecognition){
  let SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  rec=new SR(); rec.lang='en-US';
  rec.onstart=()=>{document.getElementById('mic').classList.add('rec');document.getElementById('mic').innerText='🔴';listening=true}
  rec.onend=()=>{document.getElementById('mic').classList.remove('rec');document.getElementById('mic').innerText='🎤';listening=false}
  rec.onresult=e=>{document.getElementById('i').value=e.results[0][0].transcript; send();}
}
function doMic(){ if(!rec){alert('Use Chrome/Edge');return} listening?rec.stop():rec.start() }
function picked(inp){
  let f=inp.files[0]; if(!f) return;
  let reader=new FileReader();
  reader.onload=e=>{
    let txt=e.target.result.slice(0,5000);
    attachText=`[File: ${f.name} Content: ${txt}]`;
    chatEl.innerHTML+=`<div class='m u'>📎 ${f.name} loaded (${Math.round(txt.length/1000)}k)</div>`;
    chatEl.scrollTop=999999;
  };
  if(f.type.startsWith('text')||f.name.match(/\\.(py|js|java|cpp|txt|json|csv)$/)) reader.readAsText(f);
  else { attachText=`[File: ${f.name} type:${f.type}]`; chatEl.innerHTML+=`<div class='m u'>📎 ${f.name}</div>`; }
  document.getElementById('menu').classList.remove('show');
}

function stopGen(){ if(controller) controller.abort(); document.getElementById('stopBtn').style.display='none'; document.getElementById('sendBtn').style.display='flex'; }

async function send(){
  let input=document.getElementById('i');
  let t=input.value.trim();
  if(!t &&!attachText) return;
  let full = attachText? attachText + "\\n\\n" + t : t;
  history.push({role:'user', content: t || attachText});
  localStorage.setItem('solo_v7', JSON.stringify(history));
  render();
  input.value=''; attachText='';
  let botDiv=document.createElement('div'); botDiv.className='m b'; botDiv.id='stream'; botDiv.innerHTML='<div class=typing><span></span><span></span><span></span></div>';
  chatEl.appendChild(botDiv); chatEl.scrollTop=999999;

  document.getElementById('sendBtn').style.display='none';
  document.getElementById('stopBtn').style.display='flex';

  controller=new AbortController();
  try{
    let res=await fetch('/api/chat_stream',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message: full, history: history.slice(-8)}),
      signal: controller.signal
    });
    let reader=res.body.getReader();
    let decoder=new TextDecoder();
    let fullText="";
    while(true){
      let {value,done}=await reader.read();
      if(done) break;
      let chunk=decoder.decode(value);
      fullText+=chunk;
      document.getElementById('stream').innerHTML=marked.parse(fullText);
      chatEl.scrollTop=999999;
    }
    lastReply=fullText;
    history.push({role:'assistant', content: fullText});
    localStorage.setItem('solo_v7', JSON.stringify(history));
    render();
  }catch(e){
    document.getElementById('stream').innerHTML='Stopped or error';
  }
  document.getElementById('stopBtn').style.display='none';
  document.getElementById('sendBtn').style.display='flex';
}

function clearChat(){ if(confirm('Clear all?')){history=[];localStorage.removeItem('solo_v7');render()} }
let isSpeaking = false;
function speakLast(){ 
  if(isSpeaking){ speechSynthesis.cancel(); isSpeaking=false; document.querySelector('.top button:nth-child(2)').innerText='🔊'; return; }
  if(!lastReply){ let h=[...history].reverse().find(x=>x.role==='assistant'); if(!h) return; lastReply=h.content }
  let u=new SpeechSynthesisUtterance(lastReply.replace(/[*#`]/g,'').slice(0,1000)); 
  u.lang='en-US'; u.rate=0.95;
  u.onstart=()=>{ isSpeaking=true; document.querySelector('.top button:nth-child(2)').innerText='⏹️'; };
  u.onend=()=>{ isSpeaking=false; document.querySelector('.top button:nth-child(2)').innerText='🔊'; };
  speechSynthesis.speak(u); 
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/chat_stream', methods=['POST'])
def chat_stream():
    try:
        data = request.get_json()
        msg = data.get('message','')
        hist = data.get('history', [])[-6:]

        key = os.getenv("GROQ_API_KEY")
        if not key:
            def err(): yield "ERROR: GROQ_API_KEY missing"
            return Response(err(), mimetype='text/plain')

        client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

        messages = [{"role":"system","content":SYSTEM_PROMPT}]
        for h in hist:
            if h.get('role') in ['user','assistant']:
                messages.append({"role":h['role'],"content":h['content'][:3000]})
        if not hist or hist[-1].get('content')!=msg:
            messages.append({"role":"user","content":msg})

        stream = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            stream=True,
            max_tokens=4000,
            temperature=0.6
        )

        def generate():
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

        return Response(generate(), mimetype='text/plain')

    except Exception as e:
        return Response(f"ERROR: {str(e)}", mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
