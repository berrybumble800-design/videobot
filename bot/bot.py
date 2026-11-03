import os, threading, requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram.ext import Application, CommandHandler

OWNER = int(os.environ["OWNER_ID"])
REPO = os.environ["REPO"]
GH_TOKEN = os.environ["GH_TOKEN"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
    def do_HEAD(self):
        self.send_response(200); self.end_headers()
    def log_message(self, *a):
        pass

def run_health():
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", "10000"))), Health).serve_forever()

async def make(update, ctx):
    if update.effective_user.id != OWNER:
        return
    idea = " ".join(ctx.args)
    if not idea:
        await update.message.reply_text("Use it like: /make a cat who finds the moon")
        return
    r = requests.post(
        f"https://api.github.com/repos/{REPO}/actions/workflows/make.yml/dispatches",
        headers={"Authorization": f"Bearer {GH_TOKEN}",
                 "Accept": "application/vnd.github+json"},
        json={"ref": "main", "inputs": {"prompt": idea,
              "chat_id": str(update.effective_chat.id)}},
        timeout=30)
    if r.status_code == 204:
        await update.message.reply_text("Started! Your video will arrive in a few minutes.")
    else:
        await update.message.reply_text(f"GitHub error {r.status_code}: {r.text[:200]}")

threading.Thread(target=run_health, daemon=True).start()
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("make", make))
app.run_polling()
