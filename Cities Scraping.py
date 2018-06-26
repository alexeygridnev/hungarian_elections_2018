import requests
import bs4
import re
import datetime

def get_stations(url):
    try:
        html=requests.get(url).text.encode('ISO-8859-1').decode('UTF-8')
        soup=bs4.BeautifulSoup(html)
        links_raw=soup.findAll('a')
        links=[]
        for link in links_raw:
            links.append(url.rstrip('szkkiv.html')+link['href'])
        return links
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print('Connection error. Reconnecting in 5 seconds...')
        time.sleep(5)
        return get_stations(url)

def get_data(url):
    try:
        html=requests.get(url).text.encode('ISO-8859-1').decode('UTF-8')
        turnout=re.findall('<br>\d+\.\d+ %</td>', html)[0]
        turnout=turnout.lstrip('<br>').rstrip(' %</td>')
        start_part=html.find('<th>A pártlista neve')
        end_part=html.find('A nemzetiségi listák adatai')
        html_part=html[start_part:end_part]
        soup=bs4.BeautifulSoup(html_part)
        party_results=soup.findAll('td', style="text-align:right;")
        datastr=''
        for i in range(len(party_results)-2):
            datastr=datastr+party_results[i].text+','
        total=party_results[-1].text
        datastr=datastr+total+','+turnout+'\n'
        datastr=re.sub('\s+', '', datastr)
        return datastr
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print('Connection error. Reconnecting in 5 seconds...')
        time.sleep(5)
        return get_data(url)

def get_headers():
    try:
        html=requests.get('http://www.valasztas.hu/dyn/pv18/szavossz/hu/M04/T004/szkjkv_001.html').text.encode('ISO-8859-1').decode('UTF-8')
        start=html.find('<th>A pártlista</th>')
        end=html.find('A nemzetiségi listák adatai')
        html=html[start:end]
        soup=bs4.BeautifulSoup(html)
        party_names=soup.findAll('td', style="text-align:left;")
        headstr='polling_station,'
        for party in party_names:
            headstr=headstr+party.text.replace(' ','_').replace('-', '_')+','
        headstr=headstr+'total,turnout_gen_perc\n'
        return headstr
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print('Connection error. Reconnecting in 5 seconds...')
        time.sleep(5)
        return get_headers()
    

#writing header:
csv=open('PR_'+str(datetime.datetime.now())+'.csv','w')
csv.write(get_headers())

#open bugfile:
bugs=open('Bugs.txt', 'w')

#getting data, loop:
html_i=requests.get('http://www.valasztas.hu/dyn/pv18/szavossz/hu/TK/szkkivtk.html').text.encode('ISO-8859-1').decode('UTF-8')
start_i=html_i.find('Megyei jogú városok:')
end_i=html_i.find('<\html>')
html_i=html_i[start_i:end_i]
soup_i=bs4.BeautifulSoup(html_i)

for el in soup_i.findAll('a'):
    location=el.text
    url_dist='http://www.valasztas.hu/dyn/pv18/szavossz/hu'+el['href'].lstrip('..')
    links=get_stations(url_dist)
    for link in links:
        try:
            loc_id=re.findall('szkjkv_\d+', link)[0].lstrip('szkjkv')
            csv.write(location+loc_id+','+get_data(link))
        except IndexError:
            bugs.write(link+'\n')
            print('Index error occured')
    print(location+' done')
    
csv.close()
bugs.close()
