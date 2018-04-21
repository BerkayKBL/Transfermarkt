from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as soup1
import psycopg2
class Transfermarkt:
    def __init__(self):
        self.base_url="https://www.transfermarkt.com.tr/"
        self.en_team=[]
        self.tr_team=[]
        self.isp_team=[]
        self.ital_team=[]
        self.my_url=["premier-league/startseite/wettbewerb/GB1"]
        self.ozellik=['numara',"adı","pozisyon","doğum tarihi","yas","boy","ayak","takıma_giriş","sozleşme_son","değer"]
    def get_team(self):
        for i in self.my_url:
            url=self.base_url+i
            client = Request(url, headers={"User-Agent" : "Mozilla/5.0"})
            page = urlopen(client).read()
            soup =soup1(page, 'html.parser')
            
            for link in soup.find_all('a'):
                if "/kader/verein/" in str(link.get("href")):
                    if i.split("/")[0] =="premier-league":
                        if link.get('href') not in self.en_team:
                            self.en_team.append(link.get('href'))
                    elif i.split("/")[0]=="super-lig":
                        if link.get('href') not in self.tr_team:
                            self.tr_team.append(link.get('href'))
                    elif i.split("/")[0]=="laliga":
                        if link.get('href') not in self.isp_team:
                            self.isp_team.append(link.get('href'))
                    elif i.split("/")[0]=="serie-a":
                        if link.get('href') not in self.ital_team:
                            self.ital_team.append(link.get('href'))
                            
                    else:
                        print("hatalı")
    def get_player_info(self):
        for i in self.en_team:        
           # print(self.base_url+i[1:]+"/plus/1")
            takim=i.split("/")[1]
            self.get_player(self.base_url+i[1:]+"/plus/1",takim)
    def get_player(self,url,takim):#url  ve takim adı alır 
        a=0
        pozisyon=[]
        client = Request(url, headers={"User-Agent" : "Mozilla/5.0"})
        page = urlopen(client).read()
        soup =soup1(page, 'html.parser')
        for tr in soup.findAll('tbody'):
            liste=[] 
            ozellik=""
            if a==1:
                for i in tr.find_all('td'):
                    b=i.get_text()
                    if "€" in b :
                        ozellik =ozellik+b+"+"
                        c=ozellik.split("+")
                        yas=c[5].split("(")[1][:-1]
                        dogum_tarihi=c[5].split("(")[0]
                        
                        c.pop(1)  
                        c.insert(4,dogum_tarihi)
                        c.insert(5,yas)
                        c.pop(6)
                        self.register(c,takim)
                        pozisyon.append(c[3])
                        #print(url)
                        ozellik=""
                    else:
                        ozellik=ozellik+b+"+"
                sayac=0
                p_sayac=0
                for i in tr.find_all('a'):
                    if "profil" in i.get('href'):
                        if sayac%2==0:
                            self.get_player_static(i.get('href'),pozisyon[p_sayac])
                            p_sayac=p_sayac+1
                    sayac =sayac+1
            a=a+1
    def get_player_static(self,url,pozisyon):
        a=1
        b=[]
        print(self.base_url[:-1]+url.replace('profil','leistungsdaten'))
        client = Request(self.base_url[:-1]+url.replace('profil','leistungsdaten'), headers={"User-Agent" : "Mozilla/5.0"})
        page = urlopen(client).read()
        soup =soup1(page, 'html.parser')
        for i in soup.find_all('tfoot'):
            if a==1:
                c=i.find_all('td')
                c=str(c).split('</td>')
                for j in range(2,len(c)-1):
                    b.append(c[j][c[j].index('>')+1:])
            else:
                pass
            a=a+1
        a=1
    
        ozellik=[]
        print(pozisyon)
        if pozisyon=="Kaleci":
            
            b.insert(2,"-")
        else:
            b.append("-")
            b.append("-")
        print(len(b))
        b.clear()
    def register(self,liste,takim):#oyuncu ozellikleri db'ye kaydolur
        liste2=[]

        try:
            con = psycopg2.connect("host='localhost' dbname='deneme' user='postgres' password='1234'")   
            cur = con.cursor()
        except :
            print("safasdf")
        
        for i in range(0,len(liste)):
            if liste[i]:
                liste2.append(liste[i])
        for i in range(0,len(self.ozellik)):
            if liste2[i]=='-':
                liste2[i]="bilinmiyor"
        liste2.append(takim)    
        query =  "INSERT INTO futbolcu (no, name, pozisyon,dogum_tarihi,yas,boy,ayak,takima_giris,sozlesme_son,deger,takim)\
        VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s);"
        data = (liste2[0], liste2[1], liste2[2],liste2[3],liste2[4],liste2[5],liste2[6],liste2[7],liste2[8],liste2[9],liste2[10])      
        cur.execute(query, data)
        
        con.commit()
    def run(self):
        self.get_team()
        self.get_player_info()    
        
if __name__ == '__main__':
    transfer = Transfermarkt()
    transfer.run()