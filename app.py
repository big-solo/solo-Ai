from flask import Flask, request, jsonify, render_template_string
import os, base64, io, re, requests, traceback, contextlib
from io import StringIO
from groq import Groq
from PIL import Image
import sympy as sp
from sympy import symbols, solve, diff, integrate

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML_PAGE = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Solo AI V4.1 - Builder by Samuel Solomon</title>
<style>
body{font-family:system-ui,sans-serif;background:#0a0a0a;color:#fff;margin:0;display:flex;flex-direction:column;height:100vh}
#header{padding:12px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #222;background:#111;flex-wrap:wrap;gap:8px}
#header b{color:#3b82f6} button{padding:7px 12px;border-radius:20px;border:none;background:#222;color:#fff;margin:2px;cursor:pointer;font-size:13px}
button.active{background:#3b82f6} #chat{flex:1;overflow-y:auto;padding:15px}
.msg{margin:8px 0;padding:12px 16px;border-radius:18px;max-width:92%;white-space:pre-wrap;word-break:break-word;line-height:1.5}
.user{background:#3b82f6;margin-left:auto}.ai{background:#1e1e1e;border:1px solid #2a2a2a}
pre{background:#000;padding:12px;border-radius:10px;overflow:auto;font-size:13px;border:1px solid #333}
code{background:#111;padding:2px 6px;border-radius:6px}
#input-area{display:flex;gap:6px;padding:10px;border-top:1px solid #222;align-items:center;background:#111}
#input{flex:1;padding:13px 16px;border-radius:25px;border:none;background:#222;color:#fff;outline:none;font-size:15px}
.iconBtn{width:42px;height:42px;border-radius:50%;border:none;background:#222;color:#fff;cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center}
#preview{position:fixed;top:0;left:0;right:0;bottom:0;background:#fff;display:none;z-index:99;flex-direction:column}
#preview iframe{flex:1;border:none}
a.dl{background:#22c55e;color:#fff;padding:10px 18px;border-radius:20px;text-decoration:none;display:inline-block;margin:5px 5px 0}
button.pv{background:#3b82f6;color:#fff;padding:10px 18px;border-radius:20px;border:none;margin:5px 5px 5px 0;cursor:pointer}
</style></head>
<body>
<div id="preview"><div style="padding:12px;background:#111;display:flex;justify-content:space-between;align-items:center"><span style="color:#fff;font-weight:bold">🔴 Live Preview - Built by Solo AI</span><button onclick="document.getElementById('preview').style.display='none'" style="background:#ef4444;color:#fff">Close X</button></div><iframe id="frame"></iframe></div>

<div id="header">
<div><b>🤖 SOLO AI V4.1</b> <span style="font-size:11px;opacity:0.6">by Samuel Solomon</span></div>
<div style="display:flex;flex-wrap:wrap">
<button id="chatMode" class="active">💬 Chat</button><button id="codeMode">💻 Build</button><button id="mathMode">📐 Maths</button><button id="examMode">📝 Exam</button><button onclick="if(confirm('Clear chat?')){localStorage.clear();location.reload()}">🗑️</button>
</div>
</div>

<div id="chat"></div>

<div id="input-area">
<label class="iconBtn" title="Upload Image">📷<input id="imgInput" type="file" accept="image/*" hidden></label>
<button id="mic" class="iconBtn" title="Voice">🎙️</button>
<input id="input" placeholder="Build me a... or ask anything"/>
<button id="send" class="iconBtn" style="background:#3b82f6">➤</button>
</div>

<script>
let mode='chat'; let history=JSON.parse(localStorage.getItem('solo_v4_final')||'[]');
const chat=document.getElementById('chat'), input=document.getElementById('input');
function render(){chat.innerHTML=''; if(history.length==0) chat.innerHTML='<div class="msg ai">Welcome to <b>SOLO AI V4.1 - Builder Edition</b> 🔥 by <b>Samuel Solomon</b><br><br>💻 <b>I can BUILD anything:</b><br>• Build me a portfolio website<br>• Build me a restaurant website<br>• Build me a POS system<br>• Build me a todo app with React<br>• Build me a PHP login system<br>• Build me a school website<br><br>📐 <b>Maths:</b> Solve x^2+5x+6=0, differentiate, integrate, simultaneous<br>📝 <b>Exam:</b> Upload exam picture<br><br>Just type what you want to build! 👇</div>'; else history.forEach(m=>chat.innerHTML+=`<div class="msg ${m.role}">${m.text}</div>`); chat.scrollTop=chat.scrollHeight;}
render();
function save(r,t){history.push({role:r,text:t}); localStorage.setItem('solo_v4_final',JSON.stringify(history));}
function setMode(m){mode=m; document.querySelectorAll('#header button').forEach(b=>b.classList.remove('active')); document.getElementById(m+'Mode').classList.add('active'); input.placeholder = m=='code'? 'What should I build? e.g. Build me a restaurant website' : m=='math'? 'Enter any maths: e.g. solve x^2-5x+6=0' : m=='exam'? 'Type question or upload image' : 'Ask anything...';}
document.getElementById('chatMode').onclick=()=>setMode('chat'); document.getElementById('codeMode').onclick=()=>setMode('code'); document.getElementById('mathMode').onclick=()=>setMode('math'); document.getElementById('examMode').onclick=()=>setMode('exam');

async function send(){
 const text=input.value.trim(); if(!text) return; save('user',text); chat.innerHTML+=`<div class="msg user">${escapeHtml(text)}</div>`; input.value=''; const typing=document.createElement('div'); typing.className='msg ai'; typing.id='typing'; typing.innerText='Solo AI is building...'; chat.appendChild(typing); chat.scrollTop=chat.scrollHeight;
 try{
   const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,mode})});
   const data=await res.json(); document.getElementById('typing')?.remove();
   let html = formatReply(data.reply);
   if(data.preview_html){
     const b64 = btoa(unescape(encodeURIComponent(data.preview_html)));
     html+=`<br><br><button class="pv" onclick="showPreview('${b64}')">👁️ Live Preview</button><a class="dl" href="data:text/html;base64,${b64}" download="index.html">⬇️ Download Website</a>`;
   }
   chat.innerHTML+=`<div class="msg ai">${html}</div>`; save('ai',html);
 }catch(e){ document.getElementById('typing')?.remove(); chat.innerHTML+=`<div class="msg ai">❌ Error, try again</div>`;}
 chat.scrollTop=chat.scrollHeight;
}
function escapeHtml(t){return t.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
function formatReply(t){
  let h = escapeHtml(t);
  h = h.replace(/```html([\\s\\S]*?)```/g, (m,c)=>`<pre>${escapeHtml(c)}</pre>`);
  h = h.replace(/```([a-z]*)([\\s\\S]*?)```/g, (m,lang,c)=>`<pre>${escapeHtml(c)}</pre>`);
  h = h.replace(/\\n/g,"<br>");
  return h;
}
function showPreview(b64){ try{ const html=decodeURIComponent(escape(atob(b64))); document.getElementById('frame').srcdoc=html; document.getElementById('preview').style.display='flex'; }catch(e){ alert('Preview error');}}
document.getElementById('send').onclick=send; input.onkeydown=e=>{if(e.key==='Enter') send();};
document.getElementById('imgInput').onchange=e=>{const f=e.target.files[0]; if(!f) return; const r=new FileReader(); r.onload=()=>{save('user','📷 Image uploaded'); chat.innerHTML+=`<div class="msg user">📷 Image uploaded: ${escapeHtml(input.value||'Solve this')}</div>`; const typing=document.createElement('div'); typing.className='msg ai'; typing.id='typing'; typing.innerText='Analyzing image...'; chat.appendChild(typing); fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:input.value||'Solve this image',mode,image:r.result})}).then(res=>res.json()).then(d=>{document.getElementById('typing')?.remove(); const html=formatReply(d.reply)+(d.preview_html?`<br><br><button class="pv" onclick="showPreview('${btoa(unescape(encodeURIComponent(d.preview_html)))}')">👁️ Preview</button>`:'' ); chat.innerHTML+=`<div class="msg ai">${html}</div>`; save('ai',html); chat.scrollTop=chat.scrollHeight;});}; r.readAsDataURL(f);};
let mr,chunks=[]; document.getElementById('mic').onclick=async()=>{try{if(mr&&mr.state==='recording'){mr.stop(); return;} const s=await navigator.mediaDevices.getUserMedia({audio:true}); mr=new MediaRecorder(s); chunks=[]; mr.ondataavailable=e=>chunks.push(e.data); mr.onstop=async()=>{const blob=new Blob(chunks,{type:'audio/webm'}); const fd=new FormData(); fd.append('audio',blob); document.getElementById('mic').innerText='⏳'; const r=await fetch('/api/voice',{method:'POST',body:fd}); const d=await r.json(); document.getElementById('mic').innerText='🎙️'; input.value=d.text; send();}; mr.start(); document.getElementById('mic').innerText='🔴';}catch(e){alert('Mic permission needed')}};
</script></body></html>
"""

def run_python_code(code):
    blocked = ["os.", "subprocess", "shutil", "socket", "open(", "import os", "sys.exit", "__import__"]
    if any(b in code for b in blocked):
        return "❌ Blocked for safety on free hosting."
    out = StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            exec(code, {"__builtins__": __builtins__}, {})
        return out.getvalue() or "✅ Ran with no output"
    except Exception:
        return traceback.format_exc()

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/api/chat", methods=["POST"])
def chat_api():
    data = request.json
    msg = data.get("message","")
    mode = data.get("mode","chat")
    img = data.get("image")

    # Image solving (vision model)
    if img:
        try:
            comp = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role":"user","content":[
                    {"type":"text","text": f"Mode {mode}. Solve this: {msg}. If code, give full code. If website, give full HTML single file."},
                    {"type":"image_url","image_url":{"url":img}}
                ]}]
            )
            reply = comp.choices[0].message.content
            preview = None
            if "```html" in reply:
                try: preview = reply.split("```html")[1].split("```")[0]
                except: pass
            return jsonify({"reply": reply, "preview_html": preview})
        except Exception as e:
            return jsonify({"reply": f"Image error: {str(e)}"})

    # System prompts for each mode
    if mode == "code":
        system = """You are SOLO AI V4.1 Builder by Samuel Solomon - Senior Full-Stack Polyglot Developer.
You can WRITE perfect code in ANY language: HTML, CSS, JavaScript, React, Next.js, PHP, Laravel, Python, Django, Flask, Java, C++, C, C#, Go, Node.js, TypeScript, Flutter, SQL.

RULES:
1. When user says "Build me X website/app", you MUST generate COMPLETE SINGLE-FILE HTML with CSS and JS inside <style> and <script>. Make it BEAUTIFUL, MODERN, RESPONSIVE.
2. Use Tailwind CDN: <script src="https://cdn.tailwindcss.com"></script>
3. Make buttons functional. Add fake data if needed. Make it look like real startup.
4. After code, give 2-line explanation.
5. Always put HTML in ```html code block.
6. For PHP/React/Laravel requests, give FULL code for that stack PLUS a simple HTML version that can be previewed.
7. Never say you can't. You can build ANYTHING.
"""
    elif mode == "math":
        system = """You are SOLO AI Maths Monster by Samuel Solomon. Solve ANY maths: algebra, calculus, quadratic, simultaneous, differentiation, integration, matrices, trigonometry, word problems.
Give step-by-step solution. Give final answer clearly. If possible show working.
Format nicely with LaTeX-like steps."""
    elif mode == "exam":
        system = """You are SOLO AI Exam Solver by Samuel Solomon. Give correct answer, explain why others wrong, give key points to remember for exam."""
    else:
        system = """You are SOLO AI V4.1 by Samuel Solomon. Friendly, helpful, Nigerian vibe. You can chat, build any website/app in any language (HTML, React, PHP, Python, Java, C++ etc), solve any maths, solve exams.
If user asks to build, generate full HTML single-file beautiful site.
Keep answers concise but powerful."""

    try:
        comp = client.chat.completions.create(
            model="llama-3.1-8b-8192",
            messages=[{"role":"system","content":system},{"role":"user","content":msg}],
            temperature=0.3
        )
        reply = comp.choices[0].message.content

        preview_html = None
        if "```html" in reply:
            try:
                preview_html = reply.split("```html")[1].split("```")[0]
            except:
                pass
        elif "<!DOCTYPE html>" in reply and mode == "code":
            preview_html = reply

        return jsonify({"reply": reply, "preview_html": preview_html})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)} - Try again. Check GROQ_API_KEY."})

@app.route("/api/voice", methods=["POST"])
def voice_api():
    try:
        f = request.files.get("audio")
        path = "/tmp/v.webm"
        open(path,"wb").write(f.read())
        with open(path,"rb") as af:
            t = client.audio.transcriptions.create(file=(path, af.read()), model="whisper-large-v3")
        return jsonify({"text": t.text})
    except Exception as e:
        return jsonify({"text": f"Voice error: {e}"})

@app.route("/api/run", methods=["POST"])
def run_api():
    code = request.json.get("code","")
    return jsonify({"output": run_python_code(code)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
