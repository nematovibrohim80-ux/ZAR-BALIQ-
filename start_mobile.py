import os
import sys
import time
import socket
import re
import subprocess
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# Ensure UTF-8 output on Windows
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PORT = 8000

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def run_server():
    server_address = ('0.0.0.0', PORT)
    httpd = ThreadingHTTPServer(server_address, SimpleHTTPRequestHandler)
    httpd.serve_forever()

def generate_svg_qr(data):
    try:
        import qrcode
        import qrcode.image.svg
        factory = qrcode.image.svg.SvgImage
        img = qrcode.make(data, image_factory=factory)
        return img.to_string().decode('utf-8')
    except Exception as e:
        return f"<!-- QR code error: {e} -->"

def print_ascii_qr(data):
    try:
        import qrcode
        qr = qrcode.QRCode()
        qr.add_data(data)
        qr.make()
        qr.print_ascii(invert=True)
    except Exception:
        pass

def main():
    print("=" * 60)
    print("   ZAR BALIQ - TELEFONDA KO'RISH SERVERI")
    print("=" * 60)
    
    # 1. Start HTTP server
    print(f"[*] Mahalliy veb-server ishga tushirilmoqda (Port: {PORT})...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    local_ip = get_local_ip()
    local_url = f"http://{local_ip}:{PORT}"
    print(f"[+] Mahalliy tarmoq havolasi: {local_url}")
    
    # 2. Start Cloudflare Tunnel
    public_url = None
    cloudflared_path = os.path.join(os.path.dirname(__file__), "cloudflared.exe")
    proc = None
    
    if os.path.exists(cloudflared_path):
        print("[*] Cloudflare Tunnel ishga tushirilmoqda (Global internet uchun)...")
        proc = subprocess.Popen(
            [cloudflared_path, "tunnel", "--url", f"http://127.0.0.1:{PORT}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        start_time = time.time()
        while time.time() - start_time < 20:
            line = proc.stdout.readline()
            if not line:
                break
            match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
            if match:
                public_url = match.group(0)
                break
    
    active_url = public_url if public_url else local_url
    print("\n" + "=" * 60)
    print("   TELEFONDA OCHISH UCHUN HAVOLA:")
    print(f"   -> {active_url}")
    print("=" * 60 + "\n")
    
    # Generate SVG QR codes
    qr_public_svg = generate_svg_qr(public_url) if public_url else ""
    qr_local_svg = generate_svg_qr(local_url)
    
    # Print ASCII QR in terminal
    print("QR-KOD (Telefoningiz kamerasi orqali skaner qiling):")
    print_ascii_qr(active_url)
    
    # Create HTML preview
    html_content = f"""<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zar Baliq - Telefoningizda Ko'rish</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .card {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 20px;
            padding: 30px;
            max-width: 600px;
            width: 100%;
            text-align: center;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        }}
        h1 {{
            color: #38bdf8;
            font-size: 24px;
            margin-bottom: 10px;
        }}
        p.subtitle {{
            color: #94a3b8;
            font-size: 15px;
            margin-bottom: 25px;
        }}
        .notice {{
            background: rgba(56, 189, 248, 0.1);
            border-left: 4px solid #38bdf8;
            padding: 14px 18px;
            border-radius: 8px;
            text-align: left;
            margin-bottom: 25px;
            font-size: 14px;
            line-height: 1.5;
            color: #e2e8f0;
        }}
        .notice strong {{
            color: #38bdf8;
        }}
        .qr-box {{
            background: white;
            padding: 20px;
            border-radius: 16px;
            display: inline-block;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        }}
        .qr-box svg {{
            width: 250px;
            height: 250px;
            display: block;
        }}
        .url-box {{
            background: #0f172a;
            padding: 12px 16px;
            border-radius: 10px;
            font-family: monospace;
            font-size: 16px;
            color: #4ade80;
            word-break: break-all;
            margin-bottom: 20px;
            border: 1px dashed #334155;
        }}
        .steps {{
            text-align: left;
            background: #0f172a;
            border-radius: 12px;
            padding: 16px 20px;
            font-size: 14px;
            color: #cbd5e1;
            margin-top: 15px;
        }}
        .steps ol {{
            padding-left: 20px;
        }}
        .steps li {{
            margin-bottom: 8px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h1>📱 Saytni Telefoningizda Ochish</h1>
        <p class="subtitle">Zar Baliq loyihasini mobil qurilmangizda test qiling</p>
        
        <div class="notice">
            💡 <strong>Eslatma:</strong> Expo Go ilovasi faqat <em>React Native</em> loyihalari uchun. Sizning saytingiz esa to'liq <em>Web-sayt (HTML/CSS/JS)</em> bo'lganligi sababli, telefoningizning <strong>oddiy Kamerasi</strong> orqali ushbu QR-kodni skaner qilsangiz kifoya! Brauzerda (Chrome / Safari) darhol ochiladi.
        </div>

        <div class="qr-box">
            {qr_public_svg if public_url else qr_local_svg}
        </div>

        <div class="url-box">
            👉 <a href="{active_url}" target="_blank" style="color: #4ade80; text-decoration: none;">{active_url}</a>
        </div>

        <div class="steps">
            <strong>Ko'rsatma:</strong>
            <ol>
                <li>Telefoningiz <strong>Kamera</strong>sini oching (yoki QR Scanner).</li>
                <li>Kamerani yuqoridagi QR-kodga qarating.</li>
                <li>Chiqgan havolani (link) bosing — sayt ochiladi!</li>
                <li>{"Ushbu havola Cloudflare orqali ishlaydi, shuning uchun telefoningiz Wi-Fi yoki 4G/5G mobil internetda bo'lishidan qat'iy nazar ochiladi." if public_url else "Telefoningiz kompyuter bilan bir xil Wi-Fi tarmog'iga ulangan bo'lishi kerak."}</li>
            </ol>
        </div>
    </div>
</body>
</html>
"""
    qr_file_path = os.path.join(os.path.dirname(__file__), "mobile_preview.html")
    with open(qr_file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("[*] Brauzerda QR-kod oynasi ochilmoqda...")
    webbrowser.open(f"file://{os.path.abspath(qr_file_path)}")
    
    print("\n[V] Server faol ishlamoqda. To'xtatish uchun Ctrl+C bosing.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Server to'xtatildi.")
        if proc:
            proc.terminate()

if __name__ == "__main__":
    main()
