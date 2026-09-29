import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
app = Flask(__name__)
SYSTEM_PROMPT = "You are SOLO AI V5 built by Samuel Solomon from Lagos, Nigeria."

HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SOLO AI V5</title><style>
*{margin:0;padding:0;box-sizing:border-box;font-family:sans-serif}
body{background:#f8f7ff;min-height:100vh;display:flex;flex-direction:column}
.chat{flex:1;max-width:900px;width:95%;margin:12px auto;background:white;border-radius:20px;padding:18px;overflow-y:auto;display:flex;flex-direction:column;gap:12px;min-height:75vh;border:1px solid #eee}
.m{max-width:85%;padding:11px 15px;border-radius:18px;white-space:pre-wrap;font-size:14px}
.u{align-self:flex-end;background:#111;color:#fff;border-radius:18px 18px 4px 18px}
.b{align-self:flex-start;background:#f5f5ff;border:1px solid #eee}
.bar-wrap{max-width:900px;width:95%;margin:0 auto 20px;position:relative}
.bar{background:#fff;border-radius:24px;padding:8px 10px;display:flex;align-items:center;gap:8px;box-shadow:0 8px 30px rgba(0,0,0,.12);border:1px solid #eee}
.plus{width:38px;height:38px;border-radius:50%;border:none;background:#f3f4f6;cursor:pointer;font-size:20px}
.inp{flex:1;border:none;background:transparent;padding:10px;outline:none;font-size:15px}
.send{width:38px;height:38px;border-radius:50%;border:none;background:#111;color:#fff;cursor:pointer}
.menu{position:absolute;bottom:60px;left:0;background:#fff;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,.15);padding:8px;width:200px;display:none}
.menu.show{display:block}
.menu button{width:100%;border:none;background:transparent;padding:12px;text-align:left;border-radius:10px;cursor:pointer}
</style></head><body>
<div class="chat" id="c"><div class='m b'>SOLO AI V5 ready.</div></div>
<div class="bar-wrap">
<div class="menu" id="menu">
<input type="file" id="cam" accept="image/*" capture="environment" style="display:none" onchange="picked(this)">
<input type="file" id="img" accept="image/*" style="display:none" onchange="picked(this)">
<input type="file" id="doc" accept=".pdf,.doc,.docx,.txt" style="display:none" onchange="picked(this)">
<button onclick="document.getElementById('cam').click()">📷 Camera</button>
<button onclick="document.getElementById('img').click()">🖼️ Photo</button>
<button onclick="document.getElementById('doc').click()">📄 Document</button>
</div>
<div class="bar"><button class="plus" onclick="document.getElementById('menu').classList.toggle('show')">+</button>
<input class="inp" id="i" placeholder="Message" onkeydown="if(event.key==='Enter')send()">
<button class="send" onclick="send()">↑</button></div></div>
<script>
let attach="";
function picked(inp){let f=inp.files[0];if(!f)return;attach=`[File: ${f.name}]`;let c=document.getElementById('c');c.innerHTML+=`<div class='m u'>📎 ${f.name}</div>`}
async function send(){let inp=document.getElementById('i');let t=inp.value.trim();if(!t&&!attach)return;let c=document.getElementById('c');if(t)c.innerHTML+=`<div class='m u'>${t}</div>`;let full=attach?attach+"\\n"+t:t;inp.value='';attach='';c.innerHTML+=`<div id='tmp' class='m b'>...</div>`;let r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:full})});let d=await r.json();document.getElementById('tmp')?.remove();c.innerHTML+=`<div class='m b'>${d.reply}</div>`;c.scrollTop=99999}
</script></body></html>
"""
@app.route('/')
def home(): return render_template_string(HTML)
@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        msg=request.get_json().get('message','')
        key=os.getenv("GROQ_API_KEY")
        if not key: return jsonify({"reply":"ERROR: GROQ_API_KEY missing"})
        client=OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
        resp=client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":msg}]
        )
        return jsonify({"reply":resp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply":f"ERROR: {str(e)}"})
if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
