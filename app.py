import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
app = Flask(__name__)
SYSTEM_PROMPT = "You are SOLO AI V5 Beautiful Edition built by Samuel Solomon from Lagos, Nigeria."

HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SOLO AI V5</title><link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}
body{background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;flex-direction:column}
.chat{flex:1;max-width:900px;width:95%;margin:12px auto;background:rgba(255,255,255,0.97);border-radius:20px;padding:18px;overflow-y:auto;display:flex;flex-direction:column;gap:12px;min-height:75vh}
.m{max-width:85%;padding:11px 15px;border-radius:18px;white-space:pre-wrap;font-size:14px}
.u{align-self:flex-end;background:#111;color:#fff;border-radius:18px 18px 4px 18px}
.b{align-self:flex-start;background:#f5f5ff;border:1px solid #eee;border-radius:18px 18px 18px 4px}
.bar-wrap{max-width:900px;width:95%;margin:0 auto 20px;position:relative}
.bar{background:#fff;border-radius:24px;padding:8px 10px;display:flex;align-items:center;gap:8px;box-shadow:0 8px 30px rgba(0,0,0,0.12)}
.plus{width:38px;height:38px;border-radius:50%;border:none;background:#f3f4f6;cursor:pointer;font-size:20px;display:flex;align-items:center;justify-content:center}
.inp{flex:1;border:none;background:transparent;padding:10px;outline:none;font-size:15px}
.icon{width:38px;height:38px;border:none;background:transparent;border-radius:50%;cursor:pointer;font-size:18px}
.send{width:38px;height:38px;border-radius:50%;border:none;background:#111;color:#fff;cursor:pointer;font-size:16px}
.menu{position:absolute;bottom:60px;left:0;background:#fff;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,0.15);padding:8px;width:200px;display:none;z-index:10}
.menu.show{display:block}
.menu button{width:100%;border:none;background:transparent;padding:12px 14px;text-align:left;border-radius:10px;cursor:pointer;display:flex;gap:10px;align-items:center;font-size:14px}
.menu button:hover{background:#f3f4f6}
</style></head><body>
<div class="chat" id="c"></div>
<div class="bar-wrap">
  <div class="menu" id="menu">
    <input type="file" id="cam" accept="image/*" capture="environment" style="display:none" onchange="filePicked(this,'camera')">
    <input type="file" id="img" accept="image/*" style="display:none" onchange="filePicked(this,'image')">
    <input type="file" id="doc" accept=".pdf,.doc,.docx,.txt" style="display:none" onchange="filePicked(this,'doc')">
    <button onclick="document.getElementById('cam').click();hide()">📷 Camera</button>
    <button onclick="document.getElementById('img').click();hide()">🖼️ Photo & Video</button>
    <button onclick="document.getElementById('doc').click();hide()">📄 Document</button>
  </div>
  <div class="bar">
    <button class="plus" onclick="toggle()">+</button>
    <input class="inp" id="i" placeholder="Message" onkeydown="if(event.key==='Enter')send()">
    <button class="icon" id="mic" onclick="mic()">🎤</button>
    <button class="send" onclick="send()">↑</button>
  </div>
</div>
<script>
let attach=""; let rec,listening=false;
if(window.SpeechRecognition||window.webkitSpeechRecognition){let SR=window.SpeechRecognition||window.webkitSpeechRecognition;rec=new SR();rec.lang='en-US';rec.onstart=()=>{document.getElementById('mic').innerText='🔴';listening=true;};rec.onend=()=>{document.getElementById('mic').innerText='🎤';listening=false;};rec.onresult=e=>{document.getElementById('i').value=e.results[0][0].transcript;send();}}
function toggle(){document.getElementById('menu').classList.toggle('show')}
function hide(){document.getElementById('menu').classList.remove('show')}
function mic(){if(!rec){alert('Use Chrome');return;} listening?rec.stop():rec.start();}
function filePicked(inp,type){let f=inp.files[0];if(!f)return;let c=document.getElementById('c');if(type!='doc'){let r=new FileReader();r.onload=e=>{c.innerHTML+=`<div class='m u' style='padding:4px'><img src='${e.target.result}' style='max-width:220px;border-radius:12px'></div>`;attach=`[Uploaded ${type}: ${f.name}]`;c.scrollTop=9999;};r.readAsDataURL(f);}else{c.innerHTML+=`<div class='m u'>📄 ${f.name}</div>`;attach=`[Uploaded document: ${f.name}]`;}}
async function send(){let inp=document.getElementById('i');let t=inp.value.trim();if(!t&&!attach)return;let c=document.getElementById('c'); if(t)c.innerHTML+=`<div class='m u'>${t}</div>`;let full=attach?attach+"\\n"+t:t; inp.value='';attach='';c.scrollTop=99999; hide(); c.innerHTML+=`<div id='tmp' class='m b'>...</div>`;c.scrollTop=99999; try{let r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:full})});let d=await r.json();document.getElementById('tmp')?.remove();c.innerHTML+=`<div class='m b'>${d.reply||d.error||'Error'}</div>`;c.scrollTop=99999;}catch(e){document.getElementById('tmp').innerText='Network error: check GROQ key';}}
document.addEventListener('click',e=>{if(!e.target.closest('.bar-wrap'))hide();});
</script></body></html>"""
@app.route('/')
def home(): return render_template_string(HTML)
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        msg=request.get_json().get('message','')
        key=os.getenv("GROQ_API_KEY")
        if not key: return jsonify({"reply": "ERROR: GROQ_API_KEY not set in Render Environment"})
        client=OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
        resp=client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":msg}])
        return jsonify({"reply":resp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"ERROR: {str(e)}"})

if __name__=='__main__': app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
app = Flask(__name__)
SYSTEM_PROMPT = "You are SOLO AI V5 Beautiful Edition built by Samuel Solomon from Lagos, Nigeria."

HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SOLO AI V5</title><link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}
body{background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;display:flex;flex-direction:column}
.chat{flex:1;max-width:900px;width:95%;margin:12px auto;background:rgba(255,255,255,0.97);border-radius:20px;padding:18px;overflow-y:auto;display:flex;flex-direction:column;gap:12px;min-height:75vh}
.m{max-width:85%;padding:11px 15px;border-radius:18px;white-space:pre-wrap;font-size:14px}
.u{align-self:flex-end;background:#111;color:#fff;border-radius:18px 18px 4px 18px}
.b{align-self:flex-start;background:#f5f5ff;border:1px solid #eee;border-radius:18px 18px 18px 4px}
.bar-wrap{max-width:900px;width:95%;margin:0 auto 20px;position:relative}
.bar{background:#fff;border-radius:24px;padding:8px 10px;display:flex;align-items:center;gap:8px;box-shadow:0 8px 30px rgba(0,0,0,0.12)}
.plus{width:38px;height:38px;border-radius:50%;border:none;background:#f3f4f6;cursor:pointer;font-size:20px;display:flex;align-items:center;justify-content:center}
.inp{flex:1;border:none;background:transparent;padding:10px;outline:none;font-size:15px}
.icon{width:38px;height:38px;border:none;background:transparent;border-radius:50%;cursor:pointer;font-size:18px}
.send{width:38px;height:38px;border-radius:50%;border:none;background:#111;color:#fff;cursor:pointer;font-size:16px}
.menu{position:absolute;bottom:60px;left:0;background:#fff;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,0.15);padding:8px;width:200px;display:none;z-index:10}
.menu.show{display:block}
.menu button{width:100%;border:none;background:transparent;padding:12px 14px;text-align:left;border-radius:10px;cursor:pointer;display:flex;gap:10px;align-items:center;font-size:14px}
.menu button:hover{background:#f3f4f6}
</style></head><body>
<div class="chat" id="c"></div>
<div class="bar-wrap">
  <div class="menu" id="menu">
    <input type="file" id="cam" accept="image/*" capture="environment" style="display:none" onchange="filePicked(this,'camera')">
    <input type="file" id="img" accept="image/*" style="display:none" onchange="filePicked(this,'image')">
    <input type="file" id="doc" accept=".pdf,.doc,.docx,.txt" style="display:none" onchange="filePicked(this,'doc')">
    <button onclick="document.getElementById('cam').click();hide()">📷 Camera</button>
    <button onclick="document.getElementById('img').click();hide()">🖼️ Photo & Video</button>
    <button onclick="document.getElementById('doc').click();hide()">📄 Document</button>
  </div>
  <div class="bar">
    <button class="plus" onclick="toggle()">+</button>
    <input class="inp" id="i" placeholder="Message" onkeydown="if(event.key==='Enter')send()">
    <button class="icon" id="mic" onclick="mic()">🎤</button>
    <button class="send" onclick="send()">↑</button>
  </div>
</div>
<script>
let attach=""; let rec,listening=false;
if(window.SpeechRecognition||window.webkitSpeechRecognition){let SR=window.SpeechRecognition||window.webkitSpeechRecognition;rec=new SR();rec.lang='en-US';rec.onstart=()=>{document.getElementById('mic').innerText='🔴';listening=true;};rec.onend=()=>{document.getElementById('mic').innerText='🎤';listening=false;};rec.onresult=e=>{document.getElementById('i').value=e.results[0][0].transcript;send();}}
function toggle(){document.getElementById('menu').classList.toggle('show')}
function hide(){document.getElementById('menu').classList.remove('show')}
function mic(){if(!rec){alert('Use Chrome');return;} listening?rec.stop():rec.start();}
function filePicked(inp,type){let f=inp.files[0];if(!f)return;let c=document.getElementById('c');if(type!='doc'){let r=new FileReader();r.onload=e=>{c.innerHTML+=`<div class='m u' style='padding:4px'><img src='${e.target.result}' style='max-width:220px;border-radius:12px'></div>`;attach=`[Uploaded ${type}: ${f.name}]`;c.scrollTop=9999;};r.readAsDataURL(f);}else{c.innerHTML+=`<div class='m u'>📄 ${f.name}</div>`;attach=`[Uploaded document: ${f.name}]`;}}
async function send(){let inp=document.getElementById('i');let t=inp.value.trim();if(!t&&!attach)return;let c=document.getElementById('c'); if(t)c.innerHTML+=`<div class='m u'>${t}</div>`;let full=attach?attach+"\\n"+t:t; inp.value='';attach='';c.scrollTop=99999; hide(); c.innerHTML+=`<div id='tmp' class='m b'>...</div>`;c.scrollTop=99999; try{let r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:full})});let d=await r.json();document.getElementById('tmp')?.remove();c.innerHTML+=`<div class='m b'>${d.reply||d.error||'Error'}</div>`;c.scrollTop=99999;}catch(e){document.getElementById('tmp').innerText='Network error: check GROQ key';}}
document.addEventListener('click',e=>{if(!e.target.closest('.bar-wrap'))hide();});
</script></body></html>"""
@app.route('/')
def home(): return render_template_string(HTML)
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        msg=request.get_json().get('message','')
        key=os.getenv("GROQ_API_KEY")
        if not key: return jsonify({"reply": "ERROR: GROQ_API_KEY not set in Render Environment"})
        client=OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
        resp=client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":msg}])
        return jsonify({"reply":resp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"ERROR: {str(e)}"})

if __name__=='__main__': app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
