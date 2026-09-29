import os, base64, io, math
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from PIL import Image, ImageEnhance, ImageOps

app = Flask(__name__)

SYSTEM_PROMPT = """
You are SOLO AI built by Samuel Solomon from Lagos, Nigeria.
You are NOT OpenAI, ChatGPT, Gemini, Claude.
If asked who built you: "I am SOLO AI built by Samuel Solomon. How can I help you?"
You can also solve maths, explain image editing, and be helpful.
"""

HTML = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>SOLO AI - Ultimate by Samuel Solomon</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Outfit',sans-serif}
body{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;color:#111}
.header{max-width:1100px;margin:0 auto;padding:18px 20px;color:white;display:flex;justify-content:space-between;align-items:center}
.logo{width:38px;height:38px;background:white;border-radius:10px;display:flex;align-items:center;justify-content:center}
.tabs{max-width:1100px;margin:0 auto;padding:0 20px;display:flex;gap:10px}
.tab{padding:10px 18px;background:rgba(255,255,255,0.2);color:white;border-radius:12px;cursor:pointer;font-weight:600;font-size:13px}
.tab.active{background:white;color:#111}
.main{max-width:1100px;width:95%;margin:12px auto;background:rgba(255,255,255,0.96);border-radius:20px;padding:20px;min-height:75vh;box-shadow:0 10px 40px rgba(0,0,0,0.15)}
.chat-box{display:flex;flex-direction:column;gap:12px;height:60vh;overflow-y:auto;padding:10px}
.msg{max-width:85%;padding:12px 16px;border-radius:16px;font-size:14px;line-height:1.5;white-space:pre-wrap}
.user{align-self:flex-end;background:#111;color:white;border-radius:16px 16px 4px 16px}
.bot{align-self:flex-start;background:#f3f4f6;border:1px solid #eee;border-radius:16px 16px 16px 4px}
.input-row{display:flex;gap:8px;margin-top:14px}
.input-row input{flex:1;padding:12px 14px;border:none;background:#f3f4f6;border-radius:12px;outline:none}
.icon{width:44px;height:44px;border:none;background:#f3f4f6;border-radius:12px;cursor:pointer}
.icon.active{background:#ef4444;color:white}
.send{background:#111;color:white;border:none;padding:12px 20px;border-radius:12px;cursor:pointer;font-weight:600}
.panel{display:none}.panel.active{display:block}
.calc-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;max-width:320px;margin:20px auto}
.calc-grid button{padding:18px;border:none;background:#f3f4f6;border-radius:12px;font-size:18px;cursor:pointer;font-weight:600}
.calc-grid button.op{background:#111;color:white}
#calcDisplay{width:100%;max-width:320px;margin:0 auto;display:block;padding:16px;background:#111;color:white;border-radius:12px;font-size:22px;text-align:right;outline:none;border:none}
.img-area{display:flex;flex-direction:column;align-items:center;gap:14px}
#preview{max-width:100%;max-height:350px;border-radius:14px;display:none;box-shadow:0 4px 20px rgba(0,0,0,0.1)}
.controls{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
.controls button,.controls input{padding:10px 14px;border:none;background:#f3f4f6;border-radius:10px;cursor:pointer;font-weight:600}
#typing{font-size:13px;color:#666}
.dot{width:5px;height:5px;background:#999;border-radius:50%;display:inline-block;animation:bounce 1s infinite}
@keyframes bounce{0%,100%{opacity:0.3}50%{opacity:1}}
</style></head><body>
<div class="header"><div style="display:flex;gap:10px;align-items:center"><div class="logo">✦</div><div><b>SOLO AI</b><div style="font-size:10px;opacity:0.8;letter-spacing:1px">BY SAMUEL SOLOMON</div></div></div></div>
<div class="tabs">
  <div class="tab active" onclick="switchTab('chat')">💬 Chat + 🎤 Mic</div>
  <div class="tab" onclick="switchTab('calc')">🧮 Maths</div>
  <div class="tab" onclick="switchTab('img')">🖼️ Edit Picture</div>
</div>
<div class="main">
  <div id="p-chat" class="panel active">
    <div class="chat-box" id="chat"></div>
    <div class="input-row">
      <button class="icon" id="micBtn" onclick="toggleMic()">🎤</button>
      <input id="inp" placeholder="Ask anything..." onkeydown="if(event.key==='Enter')sendChat()">
      <button class="send" onclick="sendChat()">Send</button>
    </div>
  </div>
  <div id="p-calc" class="panel">
    <input id="calcDisplay" readonly placeholder="0">
    <div class="calc-grid">
      <button onclick="calcPress('C')">C</button><button onclick="calcPress('(')">(</button><button onclick="calcPress(')')">)</button><button class="op" onclick="calcPress('/')">÷</button>
      <button onclick="calcPress('7')">7</button><button onclick="calcPress('8')">8</button><button onclick="calcPress('9')">9</button><button class="op" onclick="calcPress('*')">×</button>
      <button onclick="calcPress('4')">4</button><button onclick="calcPress('5')">5</button><button onclick="calcPress('6')">6</button><button class="op" onclick="calcPress('-')">-</button>
      <button onclick="calcPress('1')">1</button><button onclick="calcPress('2')">2</button><button onclick="calcPress('3')">3</button><button class="op" onclick="calcPress('+')">+</button>
      <button onclick="calcPress('0')">0</button><button onclick="calcPress('.')">.</button><button onclick="calcPress('**')">^</button><button class="op" onclick="calcSolve()">=</button>
    </div>
    <div style="text-align:center;margin-top:10px;font-size:12px;color:#666">Also type maths in chat, e.g "solve 2+2*5"</div>
  </div>
  <div id="p-img" class="panel">
    <div class="img-area">
      <input type="file" id="fileInput" accept="image/*" style="display:none" onchange="loadImg(event)">
      <button class="send" onclick="document.getElementById('fileInput').click()">📁 Upload Picture</button>
      <img id="preview">
      <canvas id="canvas" style="display:none"></canvas>
      <div class="controls" id="editControls" style="display:none">
        <button onclick="applyFilter('grayscale')">Black & White</button>
        <button onclick="applyFilter('invert')">Invert</button>
        <button onclick="applyFilter('bright')">Bright +</button>
        <button onclick="applyFilter('dark')">Dark -</button>
        <button onclick="rotateImg()">Rotate 90°</button>
        <button onclick="resetImg()">Reset</button>
        <button onclick="downloadImg()" style="background:#111;color:white">⬇️ Download</button>
      </div>
      <div style="font-size:12px;color:#666">Upload → Edit → Download - All on your phone, no server needed!</div>
    </div>
  </div>
</div>
<script>
function switchTab(t){document.querySelectorAll('.tab').forEach(e=>e.classList.remove('active'));document.querySelectorAll('.panel').forEach(e=>e.classList.remove('active'));document.getElementById('p-'+t).classList.add('active');event.target.classList.add('active');}

let recognition;let isListening=false;
if('webkitSpeechRecognition' in window || 'SpeechRecognition' in window){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  recognition=new SR();recognition.lang='en-US';
  recognition.onstart=()=>{document.getElementById('micBtn').classList.add('active');document.getElementById('micBtn').innerHTML='🔴';isListening=true;}
  recognition.onend=()=>{document.getElementById('micBtn').classList.remove('active');document.getElementById('micBtn').innerHTML='🎤';isListening=false;}
  recognition.onresult=(e)=>{document.getElementById('inp').value=e.results[0][0].transcript;sendChat();}
}
function toggleMic(){if(!recognition){alert('Use Chrome for mic');return;} if(isListening)recognition.stop(); else recognition.start();}

async function sendChat(){
  let inp=document.getElementById('inp');let text=inp.value.trim();if(!text)return;
  let chat=document.getElementById('chat');chat.innerHTML+=`<div class='msg user'>${text}</div>`;inp.value='';chat.scrollTop=chat.scrollHeight;
  // quick maths check
  try{if(/^[0-9+\\-*/().\\s^%]+$/.test(text)){ let r=eval(text.replace(/\\^/g,'**')); chat.innerHTML+=`<div class='msg bot'>🧮 Answer: ${text} = ${r}</div>`; chat.scrollTop=chat.scrollHeight; return; }}catch(e){}
  chat.innerHTML+=`<div id="typing"><span class="dot"></span> <span class="dot"></span> Thinking...</div>`;chat.scrollTop=chat.scrollHeight;
  try{let res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});let data=await res.json();document.getElementById('typing')?.remove();let d=document.createElement('div');d.className='msg bot';d.innerText=data.reply;chat.appendChild(d);chat.scrollTop=chat.scrollHeight; if('speechSynthesis' in window){let u=new SpeechSynthesisUtterance(data.reply);speechSynthesis.speak(u);} }catch(e){document.getElementById('typing')?.remove();chat.innerHTML+=`<div class='msg bot'>Error - check GROQ key</div>`;}
}
let calcVal='';function calcPress(v){let disp=document.getElementById('calcDisplay'); if(v==='C'){calcVal='';disp.value='';return;} calcVal+=v;disp.value=calcVal;}
function calcSolve(){let disp=document.getElementById('calcDisplay'); try{let ans=eval(calcVal);disp.value=ans;calcVal=ans.toString();}catch(e){disp.value='Error';calcVal='';}}

let originalImg=null;let currentRotation=0;
function loadImg(e){let file=e.target.files[0];if(!file)return;let r=new FileReader();r.onload=function(ev){let img=document.getElementById('preview');img.src=ev.target.result;img.style.display='block';originalImg=ev.target.result;document.getElementById('editControls').style.display='flex';currentRotation=0;applyCanvas();};r.readAsDataURL(file);}
function applyCanvas(){let img=document.getElementById('preview');let canvas=document.getElementById('canvas');let ctx=canvas.getContext('2d');let temp=new Image();temp.onload=()=>{canvas.width=temp.width;canvas.height=temp.height;ctx.clearRect(0,0,canvas.width,canvas.height);ctx.save();ctx.translate(canvas.width/2,canvas.height/2);ctx.rotate(currentRotation*Math.PI/180);ctx.drawImage(temp,-temp.width/2,-temp.height/2);ctx.restore();img.src=canvas.toDataURL();};temp.src=originalImg;}
function applyFilter(type){let canvas=document.getElementById('canvas');let ctx=canvas.getContext('2d');let imgData=ctx.getImageData(0,0,canvas.width,canvas.height);let d=imgData.data; if(type==='grayscale'){for(let i=0;i<d.length;i+=4){let avg=(d[i]+d[i+1]+d[i+2])/3; d[i]=d[i+1]=d[i+2]=avg;}} if(type==='invert'){for(let i=0;i<d.length;i+=4){d[i]=255-d[i];d[i+1]=255-d[i+1];d[i+2]=255-d[i+2];}} if(type==='bright'){for(let i=0;i<d.length;i+=4){d[i]=Math.min(255,d[i]+30);d[i+1]=Math.min(255,d[i+1]+30);d[i+2]=Math.min(255,d[i+2]+30);}} if(type==='dark'){for(let i=0;i<d.length;i+=4){d[i]=Math.max(0,d[i]-30);d[i+1]=Math.max(0,d[i+1]-30);d[i+2]=Math.max(0,d[i+2]-30);}} ctx.putImageData(imgData,0,0);document.getElementById('preview').src=canvas.toDataURL();}
function rotateImg(){currentRotation=(currentRotation+90)%360;applyCanvas();}
function resetImg(){currentRotation=0;document.getElementById('preview').src=originalImg;applyCanvas();}
function downloadImg(){let a=document.createElement('a');a.href=document.getElementById('preview').src;a.download='solo-ai-edited.png';a.click();}

window.onload=()=>{document.getElementById('chat').innerHTML=`<div class='msg bot'>Hello! I am SOLO AI built by Samuel Solomon. 👋\n\n💬 Chat with me\n🎤 Click mic to talk\n🧮 Go to Maths tab for calculations\n🖼️ Go to Edit Picture tab to edit any photo!</div>`;}
</script></body></html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    user_msg = data.get('message','')
    groq_key = os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY")
    if not groq_key:
        return jsonify({"reply": "Add your GROQ_API_KEY (gsk_...) in Render Environment. Your old Groq key is fine!"})
    try:
        client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":user_msg}],
            temperature=0.7
        )
        return jsonify({"reply": resp.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
