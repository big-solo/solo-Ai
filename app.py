import os, base64
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>SOLO AI V5 - Beautiful</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}
body{
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height:100vh;
  display:flex;
  flex-direction:column;
}
.header{
  max-width:950px;width:100%;margin:auto;
  padding:20px;display:flex;justify-content:space-between;align-items:center;
  color:white;
}
.header h2{font-size:26px;font-weight:600;letter-spacing:-0.5px}
.header span{background:rgba(255,255,255,0.2);padding:6px 12px;border-radius:20px;font-size:12px;backdrop-filter:blur(10px)}
#chat{
  max-width:950px;width:100%;margin:auto;flex:1;
  height:70vh;overflow-y:auto;padding:20px;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(20px);
  border-radius:24px 24px 0 0;
  box-shadow: 0 -10px 40px rgba(0,0,0,0.2);
}
.msg{
  padding:14px 18px;border-radius:20px;margin:12px 0;max-width:80%;
  line-height:1.5;white-space:pre-wrap;animation:pop 0.3s ease;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
@keyframes pop{from{transform:translateY(10px);opacity:0}to{transform:translateY(0);opacity:1}}
.user{
  background: linear-gradient(135deg,#667eea,#764ba2);
  color:white;margin-left:auto;
  border-bottom-right-radius:6px;
}
.bot{
  background:white;color:#222;
  border:1px solid #eee;
  margin-right:auto;
  border-bottom-left-radius:6px;
}
.input-area{
  max-width:950px;width:100%;margin:0 auto;
  background: rgba(255,255,255,0.95);
  padding:12px 16px;border-radius:0 0 24px 24px;
  display:flex;gap:10px;align-items:center;
  border-top:1px solid #eee;
}
input[type=text]{
  flex:1;padding:16px 20px;border-radius:30px;
  border:1px solid #e5e7eb;background:#f9fafb;
  color:#111;outline:none;font-size:15px;
  transition:0.2s;
}
input[type=text]:focus{background:white;border-color:#667eea;box-shadow:0 0 0 3px rgba(102,126,234,0.15)}
.icon-btn{
  width:48px;height:48px;border-radius:50%;border:none;
  background:#f3f4f6;color:#444;font-size:20px;cursor:pointer;
  transition:0.2s;display:flex;align-items:center;justify-content:center
}
.icon-btn:hover{transform:scale(1.05)}
.send-btn{background:linear-gradient(135deg,#667eea,#764ba2)!important;color:white!important}
.preview{max-width:220px;border-radius:16px;margin-top:8px;box-shadow:0 4px 15px rgba(0,0,0,0.1)}
#typing{color:#764ba2;font-style:italic}
</style>
</head>
<body>
<div class="header">
  <div><h2>✨ SOLO AI V5</h2><div style="font-size:13px;opacity:0.8">Beautiful Edition • by Samuel Solomon</div></div>
  <span>● LIVE & BEAUTIFUL</span>
</div>
<div id="chat">
  <div class='msg bot'>Hey Samuel! Welcome to your new <b>Beautiful SOLO AI</b> 😍<br><br>Look at this design — no more boring black!<br>✅ Gradient background<br>✅ Glass & soft white chat<br>✅ Smooth animations<br><br>Try:<br>📸 Upload a picture<br>🎤 Talk to me<br>🔊 Make me speak or sing!</div>
</div>
<div class="input-area">
<label class="icon-btn" style="cursor:pointer">📸<input type="file" id="imgInput" accept="image/*" style="display:none" onchange="handleImage(event)"></label>
<button class="icon-btn" onclick="startVoice()" id="micBtn">🎤</button>
<input type="text" id="inp" placeholder="Ask something beautiful..." onkeydown="if(event.key==='Enter')send()">
<button class="icon-btn" onclick="speakLast()" title="Speak">🔊</button>
<button class="icon-btn send-btn" onclick="send()">➤</button>
</div>
<script>
let lastBotReply = "";
let selectedImageBase64 = null;
function handleImage(e){
  const file = e.target.files[0]; if(!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => {
    selectedImageBase64 = ev.target.result.split(',')[1];
    document.getElementById('chat').innerHTML += `<div class='msg user'><img src='${ev.target.result}' class='preview'><br>Explain this image beautifully</div>`;
    send(true);
  }; reader.readAsDataURL(file);
}
async function send(isImage=false){
  let inp = document.getElementById('inp');
  let text = inp.value.trim();
  if(!text &&!isImage) return;
  if(text &&!isImage){ document.getElementById('chat').innerHTML += `<div class='msg user'>${text}</div>`; }
  inp.value = '';
  const chat = document.getElementById('chat'); chat.scrollTop = chat.scrollHeight;
  let payload = {message: text || "What do you see in this image?"};
  if(selectedImageBase64){ payload.image = selectedImageBase64; selectedImageBase64 = null; document.getElementById('imgInput').value=''; }
  chat.innerHTML += `<div class='msg bot' id='typing'>✨ SOLO is thinking...</div>`;
  try{
    let r = await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    let d = await r.json();
    document.getElementById('typing').remove();
    lastBotReply = d.reply || d.error;
    chat.innerHTML += `<div class='msg bot'>${lastBotReply}</div>`;
    chat.scrollTop = chat.scrollHeight;
  }catch(e){ document.getElementById('typing').remove(); chat.innerHTML += `<div class='msg bot'>Error: ${e}</div>`; }
}
function startVoice(){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR){ alert("Use Chrome for voice"); return; }
  let rec = new SR(); rec.lang = 'en-US'; rec.start();
  document.getElementById('micBtn').innerText = '🔴';
  rec.onresult = (e) => { document.getElementById('inp').value = e.results[0][0].transcript; send(); };
  rec.onend = () => { document.getElementById('micBtn').innerText = '🎤'; };
}
function speakLast(){
  if(!lastBotReply){ alert("No reply yet"); return; }
  const utter = new SpeechSynthesisUtterance(lastBotReply);
  utter.rate = 0.95; utter.pitch = 1.1;
  speechSynthesis.cancel(); speechSynthesis.speak(utter);
}
</script>
</body>
</html>
"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/api/chat", methods=["POST"])
def chat():
    if not client: return jsonify({"reply": "GROQ_API_KEY missing on Render"}), 500
    data = request.json
    user_msg = data.get("message","")
    image_b64 = data.get("image")
    system_prompt = "You are SOLO AI V5 Beautiful Edition, created by Samuel Solomon. NOT ChatGPT. You are SOLO AI. Be beautiful, helpful, and modern. If asked who you are, say: I am SOLO AI V5 Beautiful Edition built by Samuel Solomon."
    try:
        if image_b64:
            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role":"system","content": system_prompt},
                    {"role":"user","content": [
                        {"type":"text","text": user_msg},
                        {"type":"image_url","image_url":{"url": f"data:image/jpeg;base64,{image_b64}"}}
                    ]}
                ], max_tokens=1200
            )
        else:
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role":"system","content": system_prompt},{"role":"user","content": user_msg}],
                max_tokens=1200, temperature=0.7
            )
        return jsonify({"reply": completion.choices[0].message.content})
    except Exception as e:
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role":"system","content": system_prompt},{"role":"user","content": user_msg}],
                max_tokens=1000
            )
            return jsonify({"reply": completion.choices[0].message.content})
        except Exception as e2:
            return jsonify({"reply": f"Error: {str(e)[:200]}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
