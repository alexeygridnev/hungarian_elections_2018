import requests
import bs4
import re
import datetime
import time

def get_stations(url, parser="lxml"):
    try:
        html=requests.get(url, timeout=1).text
        soup=bs4.BeautifulSoup(html, parser)
        links_raw=soup.findAll('a')
        links=[]
        for link in links_raw:
            links.append(url.rstrip('szkkiv.htm')+link['href'])
        return links
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print('Connection error. Reconnecting in 1 second...')
        time.sleep(1)
        return get_stations(url)
    except KeyError:
        return get_stations(url, parser="html.parser")
    
def find_party(party, soup):
    table_results=soup.findAll('tr', align=None)
    party_score=''
    for el in table_results:
        for name in party:
            if name in el.text.upper():
                party_score=el.find('td', align='right').text.replace('\xa0', '')
                break
    return party_score

def get_data(url, parser="lxml"):
    try:
        html=requests.get(url).text
        start=html.find('területi választókerülete')
        end=len(html)
        html=html[start:end]
        soup=bs4.BeautifulSoup(html, parser)
        tab_cells=soup.findAll('tr', align='center')
        total=tab_cells[-1].td.text.replace('\xa0', '')
        registered=tab_cells[2].findAll('td')[-1].text.replace('\xa0', '')
        fidesz=find_party(['FIDESZ'], soup)
        jobbik=find_party(['JOBBIK'], soup)
        mszp=find_party(['MSZP','MAGYAR SZOCIALISTA PÁRT'], soup)
        lmp=find_party(['LMP','LEHET MÁS A POLITIKA'], soup)
        dataseq=[registered, fidesz, jobbik, mszp, lmp, total]
        datastr=",".join(dataseq)
        return datastr
    except (requests.exceptions.ConnectionError, requests. exceptions.Timeout):
        print('Connection error. Reconnecting in 1 seconds...')
        time.sleep(1)
        return get_data(url)
    except KeyError:
        return get_data(url, parser="html.parser")

csv=open('PR_'+str(datetime.datetime.now())+'.csv','w')
csv.write('polling_stations,registered,fidesz,mszp,jobbik,lmp,total\n')

bugs=open('Bugs.txt', "w")
#getting data, loop:

letters='abcdefghijklmnoprstuvz'


url_base='http://www.valasztas.hu/dyn/pv10/outroot/vdin1/hu/tk'

for letter in letters:
    html_i=requests.get(url_base+letter+'.htm').text
    start_i=html_i.find('<table border="0" cellspacing="0" width="100%" cellpadding="3">')
    end_i=html_i.find('</html>')
    html_i=html_i[start_i:end_i]
    soup_i=bs4.BeautifulSoup(html_i, "html.parser")
    for el in soup_i.findAll('a'):
        location=el.text
        url_dist='http://www.valasztas.hu/dyn/pv10/outroot/vdin1/hu/'+el['href']
        links=get_stations(url_dist)
        if len(links)==0:
            csv.write(location+','+get_data(url_dist)+'\n')
        else:
            try:
                for link in links:
                    loc_id=re.findall('jkv\d+', link)[0].lstrip('jkv')
                    csv.write(location+'_'+loc_id+','+get_data(link)+'\n')
            except IndexError:
                bugs.write(link+'\n')
                continue
        print(location+' done')                
            
csv.close()
bugs.close()
