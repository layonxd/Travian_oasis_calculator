from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import math

app = Flask(__name__)
CORS(app)  
#ADD TOURNAMENT SQUARE SUPPORT FOR DIST CALCULATION (done)
#add support to ground troops  (done)
#dump single ground troops , fix mix troops calcs and var names 
#calcs are wrong for big army sizes 



# Unit defense stats
unit_defense = {
    "Rato":      {"infantry": 25,  "cavalry": 20, "r":40},
    "Aranha":    {"infantry": 35,  "cavalry": 40, "r":40},
    "Morcego":   {"infantry": 66,  "cavalry": 50, "r":40},
    "Serpente":  {"infantry": 40,  "cavalry": 60, "r":40},
    "Lobo":      {"infantry": 80,  "cavalry": 70, "r":80},
    "Urso":      {"infantry": 140, "cavalry": 200, "r":120},
    "Javali":    {"infantry": 70,  "cavalry": 33, "r":80},
    "Crocodilo": {"infantry": 380, "cavalry": 240, "r":120},
    "Tigre":     {"infantry": 170, "cavalry": 250, "r":120},
    "Elefante":  {"infantry": 440, "cavalry": 520, "r":200}
}

ELp = [120, 121.7, 123.5, 125.2, 127, 128.8, 130.6, 132.4, 134.2, 136.1,
       137.9, 139.8, 141.6, 143.5, 145.4, 147.3, 149.3, 151.2, 153.1, 155.1, 157.1, 0]
Elpc = 1410





#WIP
Emp = [70, 70, 70, 70, 71, 72, 73, 74, 75, 76,
       77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 0]
Empc = 600
#WIP





def gettile(token, x, y):
    url = "https://ts2.x1.america.travian.com/api/v1/map/tile-details"
    cookies = {"JWT": token}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://ts2.x1.america.travian.com/karte.php",
        "Origin": "https://ts2.x1.america.travian.com",
        "X-Version": "247.6"
    }
    payload = {"x": x, "y": y}
    
    try:
        resp = requests.post(url, cookies=cookies, headers=headers, json=payload, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            soup = BeautifulSoup(data["html"], "html.parser")
            
            title_h1 = soup.find("h1", class_="titleInHeader")
            if not title_h1:
                return 0
                
            title_text = title_h1.find(text=True, recursive=False).strip()
            
            if len(title_text) == 13 and title_text[0] == "O":
                troop_info = soup.find(id="troop_info")
                if not troop_info:
                    return 0
                    
                tds = troop_info.find_all("td")
                
                cav = 10
                inf = 10
                r = 0
                maxtroop = 0
                
                for i in range(0, len(tds)-2, 3):
                    unit_td = tds[i]
                    count_td = tds[i+1]
                    
                    unit_name = unit_td.img["title"]
                    count = int(count_td.text)
                    
                    if unit_name in unit_defense:
                        cav += count * unit_defense[unit_name]["cavalry"]
                        inf += count * unit_defense[unit_name]["infantry"]
                        r += count * unit_defense[unit_name]["r"]
                        if count > maxtroop:
                            maxtroop = count
                
                r = r * 4  # 4 recursos
                return [inf, cav, r, maxtroop]
        return 0
    except Exception as e:
        print(f"Error fetching tile {x},{y}: {e}")
        return 0

def parse_txt(content):
    lines = content.strip().split("\n")
    result = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            result.append(parts)
    return result

def get_power(atacantes, poder):
    return atacantes * poder

def get_k(N):
    k = 2 * (1.8592 - pow(N, 0.015))
    return min(k, 1.5)

def win_cas(lp, wp, N):
    k = get_k(N)
    return pow((lp / wp), k)

def get_losses(att_troops, loss):
    return round(att_troops * loss)

def killed_all(lp, wp, N, lista_pos_6):
    maxunit = lista_pos_6
    los_cas = lp / (wp + lp)
    lost = los_cas * maxunit
    return round(lost)

def breakpoints(max_atacantes, hammerp, defense, maxtroops):
    lasta = 7
    breakpoints_list = []
    for i in range(1, max_atacantes):
        wp = get_power(i, hammerp)
        if wp > defense:
            a = get_losses(i, win_cas(defense, wp, i))
            if a < lasta:
                lasta = a
                breakpoints_list.append([a, i])
    return breakpoints_list

def get_max_val(breakpoints_list, rew, dist,troopval):
    max_val = 0
    savereq = 0
    saveloss = 0
    for i in breakpoints_list:
        loss = i[0]
        req = i[1]
        lossres = loss * troopval
        prof = rew - lossres
        if dist > 0 and req > 0:
            val = prof / req
            val = val/dist
            if val > max_val:
                saveloss = loss
                savereq = req
                max_val = val
    return [saveloss, savereq, max_val]

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        token = data.get('token')
        x = int(data.get('x'))
        y = int(data.get('y'))
        
        el_level = int(data.get('elLevel'))
        metallurgy = float(data.get('metallurgy'))
        coordinates = data.get('coordinates', [])
        
        tournament_square_level = int(data.get('tournamentSquareLevel', 0))  
        ts_speed=1+(0.2*tournament_square_level)



        #emp1
        emp_level = int(data.get('empLevel'))
        #emp1


        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        



        # Calculate power
        setpower = ELp[el_level] * (1 + (metallurgy / 100))
        max_atacantes = 3000


        #emp1
        #setpoweremp
        setpoweremp=(Emp[emp_level] * (1 + (metallurgy / 100)))
        setpowerempmix=setpoweremp+(setpower)
        ratiocav=(setpower/setpowerempmix)
        print("ratio cav:",ratiocav)
        ratioemp=1-ratiocav
        print("ratio emp:",ratioemp)

        max_atacantes_emp = 3000
        #emp1
        
        results = []
        results_emp = []
        
        for coord in coordinates:
            try:
                coord_x = int(coord[0])
                coord_y = int(coord[1])
                
                tile_data = gettile(token, coord_x, coord_y)
                
                if tile_data != 0 and tile_data[0] != 0:
                    dist = round(math.hypot(x - coord_x, y - coord_y))
                    
                    if tile_data[1] > 10:  # cavalry defense > 10
                        bk = breakpoints(max_atacantes, setpower, tile_data[1], tile_data[3])
                        
                        if bk:
                            if dist<=20:
                                ts_dist=dist
                            else:
                                inc=dist-20
                                ts_dist=inc/ts_speed
                                ts_dist+=20

                            max_val_data = get_max_val(bk, tile_data[2], ts_dist,Elpc)
                            print(dist,ts_dist)
                            
                            results.append({
                                'x': coord_x,
                                'y': coord_y,
                                'losses': max_val_data[0],
                                'troops': max_val_data[1],
                                'value': max_val_data[2],
                                'distance': dist
                            })

                        #emp1
                        defense=(tile_data[1]*ratiocav)+(tile_data[0]*ratioemp)
                        print("defense in :",defense,"x:",coord_x,"y:",coord_y)
                        bk_emp = breakpoints(max_atacantes_emp, setpowerempmix, defense, tile_data[3])
                        
                        if bk_emp:
                            if dist<=20:
                                ts_dist=dist
                            else:
                                inc=dist-20
                                ts_dist=inc/ts_speed
                                ts_dist+=20
                            mixcost=Empc+Elpc
                            max_val_data = get_max_val(bk_emp, tile_data[2], ts_dist,mixcost)
                            print(dist,ts_dist)
                            
                            results_emp.append({
                                'x': coord_x,
                                'y': coord_y,
                                'losses': max_val_data[0],
                                'troops': max_val_data[1],
                                'value': max_val_data[2],
                                'distance': dist
                            })
                        #emp1
            except Exception as e:
                print(f"Error processing coordinate {coord}: {e}")
                continue
        
        # Sort by value (descending)
        results.sort(key=lambda r: r['value'], reverse=True)
        results_emp.sort(key=lambda r: r['value'], reverse=True)
        
        return jsonify({'results': results, 'results_emp': results_emp})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)