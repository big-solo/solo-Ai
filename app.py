import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

HTML = """
<!DOCTYPE html>
<html><head><title>SOLO AI V4.1 - Fixed</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{background:#111;color:white;font-family:Arial;padding:15px}
#chat{max-height:70vh;overflow-y:auto;margin-bottom:15px}
.msg{padding:12px;border-radius:12px;margin:8px 0;word-wrap:break-word}
.user{background:#2a7fff;margin-left:20%;}
.bot{background:#222;margin-right:20%;}
.row{display:flex;gap:8px}
input{flex:1;padding:12px;border-radius:10px;border:none}
button{padding:12px 18px;border-radius:10px;border:none;background:#2a7fff;color:white;font-weight:bold}
</style></head><body>
<h3>🤖 SOLO AI V4.1 - Live ✅</h3>
<div id="chat"></div>
<div class="row"><input id="inp" placeholder="Ask anything..." onkeydown="if(event.key==='Enter')send()"><button onclick="send()">Send</button></div>
<script>
async function send(){
 let v=document.getElementById('inp').value.trim(); if(!v) return;
 let c=document.getElementById('chat');
 c.innerHTML+=`<div class='msg user'>${v}</div>`; document.getElementById('inp').value='';
 c.scrollTop=c.scrollHeight;
 let r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:v})});
 let d=await r.json();
 c.innerHTML+=`<div class='msg bot'>${d.reply||d.error}</div>`;
 c.scrollTop=c.scrollHeight;
}
</script></body></html>
"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/api/chat", methods=["POST"])
def chat():
    if not api_key: return jsonify({"reply": "GROQ_API_KEY missing"}), 500
    msg = request.json.get("message","")
    # NEW 2026 MODELS - these are active on Groq free tier
    models = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile"
    ]
    for m in models:
        try:
            completion = client.chat.completions.create(
                model=m,
                messages=[{"role":"user","content":msg}],
                max_tokens=1000,
                temperature=0.7
            )
            return jsonify({"reply": completion.choices[0].message.content})
        except Exception as e:
            last = str(e)
            if "decommissioned" in last or "not_found" in last or "does not exist" in last:
                continue
            else:
                # If it's a real error, return it
                continue
    return jsonify({"reply": f"Still failing. Last error: {last}. Go to https://console.groq.com/docs/deprecations to see active models. Key OK: {api_key[:10]}..."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
