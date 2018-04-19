import requests
import bs4
import re
import datetime

def get_stations(url):
    try:
        html=requests.get(url, timeout=1).text.encode('ISO-8859-1').decode('UTF-8')
        soup=bs4.BeautifulSoup(html)
        links_raw=soup.findAll('a')
        links=[]
        for link in links_raw:
            links.append(url.rstrip('szkkiv.html')+link['href'])
        return links
    except (requests.exceptions.ConnectionError, requests. exceptions.Timeout):
        print('Connection error. Reconnecting in 5 seconds...')
        time.sleep(5)
        return get_stations(url)


def get_data(url):
    try:
        html=requests.get(url, timeout=1).text.encode('ISO-8859-1').decode('UTF-8')
        turnout=re.findall('<br>\d+\.\d+ %</td>', html)[0]
        turnout=turnout.lstrip('<br>').rstrip(' %</td>')
        start_part=html.find('<th>A pártlista neve</th>')
        end_part=html.find('A nemzetiségi listák adatai')
        html_part=html[start_part:end_part]
        soup=bs4.BeautifulSoup(html_part)
        party_results=soup.findAll('td', style="text-align:right;")
        datastr=''
        for i in range(len(party_results)-2):
            datastr=datastr+party_results[i].text.lstrip().rstrip()+','
        datastr=datastr+party_results[-1].text.lstrip().rstrip()+','+turnout+'\n'
        return datastr
    except (requests.exceptions.ConnectionError, requests. exceptions.Timeout):
        print('Connection error. Reconnecting in 5 seconds...')
        time.sleep(5)
        return get_data(url)

def get_headers():
    html=requests.get('http://www.valasztas.hu/dyn/pv18/szavossz/hu/M04/T004/szkjkv_001.html').text.encode('ISO-8859-1').decode('UTF-8')
    start=html.find('<th>A pártlista neve</th>')
    end=html.find('A nemzetiségi listák adatai')
    html=html[start:end]
    soup=bs4.BeautifulSoup(html)
    party_names=soup.findAll('td', style="text-align:left;")
    i=1
    headstr=''
    for party in party_names:
        headstr=headstr+'v'+str(i)+' - '+party.text+'\n'
        i+=1
    return headstr


#writing codebook
with open('Codebook.txt', 'w') as codebook:
    codebook.write(get_headers())

#writing table header:
csv=open('PR_'+str(datetime.datetime.now())+'.csv','w')
csv.write('polling_stations,')
for i in range(1, 23):
    csv.write('v'+str(i)+',')
csv.write('total,turnout_perc\n')

#open bugfile:
bugs=open('Bugs_'+str(datetime.datetime.now())+'.txt', 'w')

#getting data, loop:

letters='abcdefghijklmnoprstuvz'
url_base='http://www.valasztas.hu/dyn/pv18/szavossz/hu/TK/szkkivtk'

for letter in letters:
    html_i=requests.get(url_base+letter+'.html').text.encode('ISO-8859-1').decode('UTF-8')
    start_i=html_i.find('<table cellspacing="0" border="0">')
    end_i=html_i.find('</html>')
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
        print(location+' done')
    
csv.close()
bugs.close()
