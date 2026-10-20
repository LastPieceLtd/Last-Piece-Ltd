"""Fetch a small daily BrickEconomy batch. API data may be publicly served by Pages:
only enable this workflow if your API agreement permits caching and displaying it.
"""
import datetime as dt
import json
import os
from pathlib import Path
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'data/catalog.json'
OUTPUT = ROOT / 'data/brickeconomy.json'
BATCH = min(85, max(1, int(os.getenv('BRICKECONOMY_BATCH', '85'))))
key = os.environ.get('BRICKECONOMY_API_KEY')
if not key:
    raise SystemExit('BRICKECONOMY_API_KEY manquant')
headers = {'Accept':'application/json', 'User-Agent':'LastPieceLtd-PrivateResearch/1.0','x-apikey':key}

def get(url):
    req = urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=25) as response:
        return json.load(response)

def number(value):
    if isinstance(value, bool): return None
    if isinstance(value,(int,float)): return value
    return None

catalog=json.loads(CATALOG.read_text(encoding='utf-8'))['sets']
prior=json.loads(OUTPUT.read_text(encoding='utf-8')) if OUTPUT.exists() else {'sets':{},'cursor':0}
records=prior.get('sets',{})
# Oldest catalog references first: retired models are likelier to have forecasts.
items=sorted(catalog,key=lambda s:(s.get('year') or 9999,s['id']))
usage=get('https://www.brickeconomy.com/api/v1/usage').get('data',{})
remaining=usage.get('remaining')
if isinstance(remaining,int):
    BATCH=min(BATCH,max(0,remaining-2))
start=int(prior.get('cursor',0))%len(items)
updated=0
for offset in range(BATCH):
    item=items[(start+offset)%len(items)]
    ref=item['id']+'-1'
    try:
        data=get(f'https://www.brickeconomy.com/api/v1/set/{ref}?currency=EUR').get('data',{})
        if not isinstance(data,dict) or data.get('set_number')!=ref:
            print('Réponse non reconnue pour',ref)
            continue
        row={'updated':dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
             'retired':data.get('retired'),
             'current_value_new':number(data.get('current_value_new')),
             'growth_12m':number(data.get('rolling_growth_lastyear',data.get('rolling_growth_12months'))),
             'forecast_2y':number(data.get('forecast_value_new_2_years')),
             'forecast_5y':number(data.get('forecast_value_new_5_years'))}
        records[item['id']]=row
        updated+=1
    except urllib.error.HTTPError as exc:
        print('HTTP',exc.code,'pour',ref)
        if exc.code in (401,403,429): break
    except Exception as exc:
        print('Erreur pour',ref,type(exc).__name__)

payload={'source':'BrickEconomy API (estimations, pas ventes garanties)',
         'updated':dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
         'cursor':(start+max(1,BATCH))%len(items),
         'sets':records}
OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('Références mises à jour :',updated,'; références suivies :',len(records))
