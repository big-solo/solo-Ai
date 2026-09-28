import os
from flask import Flask, request, jsonify, render_template_string
from groq import Groq

app = Flask(__name__)
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

HTML = """
<!DOCTYPE html>
<html><head><title>SOLO AI V4.1</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{background:#0f0f0f;color:white;font-family:Arial;padding:20px}.msg{padding:12px;border-radius:12px;margin:10px 0}.user{background:#2a7fff;margin-left:auto;max-width:80%}.bot{background:#222;max-width:80%}input{width:70%;padding:12px;border-radius:10px;border:none}button{padding:12px 20px;border-radius:10px;border:none;background:#2a7fff;color:white}</style>
</head><body>
<h2>🤖 SOLO AI V4.1 - Live</h2>
<div id="chat"></div>
<input id="inp" placeholder="Ask anything..."><button onclick="send()">Send</button>
<script>
async function send(){
 let v=document.getElementById('inp').value;
 document.getElementById('chat').innerHTML+=`<div class='msg user'>${v}</div>`;
 document.getElementById('inp').value='';
 let r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:v})});
 let d=await r.json();
 document.getElementById('chat').innerHTML+=`<div class='msg bot'>${d.reply||d.error}</div>`;
}
</script></body></html>
"""

@app.route("/")
def home(): return render_template_string(HTML)

@app.route("/api/chat", methods=["POST"])
def chat():
    if not api_key: return jsonify({"error": "GROQ_API_KEY missing on Render"}), 500
    if not client: return jsonify({"error": "Groq client failed to init"}), 500
    msg = request.json.get("message","")
    models_to_try = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "llama3-8b-8192"]
    last_err = ""
    for model_name in models_to_try:
        try:
            c = client.chat.completions.create(model=model_name, messages=[{"role":"user","content":msg}], max_tokens=800)
            return jsonify({"reply": c.choices[0].message.content})
        except Exception as e:
            last_err = str(e)
            continue
    return jsonify({"error": f"All models failed. Last error: {last_err}. Key starts with: {api_key[:7]}..."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
