import requests
from bs4 import BeautifulSoup
import time



def gettile(f,token,x,y):
    url = "https://ts2.x1.america.travian.com/api/v1/map/tile-details"
    cookies = {"JWT": token}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://ts2.x1.america.travian.com/karte.php",
        "Origin": "https://ts2.x1.america.travian.com",
        "X-Version": "247.6"
    }
    payload = {"x": x, "y": y}
    
    
    
    
    
    resp = requests.post(url, cookies=cookies, headers=headers, json=payload)

    
    
    if resp.status_code == 200:
        data = resp.json()
        soup = BeautifulSoup(data["html"], "html.parser")
        
 
        title_h1 = soup.find("h1", class_="titleInHeader")

# Get only the direct text of the tag (excluding nested spans)
        title_text = title_h1.find(text=True, recursive=False).strip()
        print(title_text)
        
        if len(title_text)==13 and title_text[0]=="O":

            
            # Write text into it
            f.write(f"{x} {y}\n")
            # Always close after writing
            
def get_tile_with_range(f,x,y,rangee):
    for i in range(x-rangee,x+rangee+1):
        for j in range(y-rangee,y+rangee+1):
            print(i," ",j," ",gettile(f,token,i,j))
        time.sleep(5)
    f.close()
    
def add_tile_with_range(f,x,y,rangee,lastrange):
    for i in range(x-rangee,x+rangee+1):
        for j in range(y-rangee,y+rangee+1):
            xdist=abs(i-x)
            ydist=abs(j-y)
            if (xdist>lastrange)|(ydist>lastrange):
                print(i," ",j," ",gettile(f,token,i,j))
                print((xdist," ", ydist))
        time.sleep(5)
    f.close()


token="jwt_token_for_server"
#f = open("myfile.txt", "w")#new file
f = open("myfile.txt", "a")#append

#select radius for scaning , and vilage location
#this program saves to a file the oasis found in that range for app.py to calculate what to attack 
add_tile_with_range(f, 182, 163,25 , 20)




