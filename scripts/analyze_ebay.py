"""Temporary eBay listing analysis; no eBay responses are persisted to files."""
import base64
import json
import os
import re
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request

CLIENT_ID = os.environ.get('EBAY_CLIENT_ID', '').strip()
CLIENT_SECRET = os.environ.get('EBAY_CLIENT_SECRET', '').strip()
MARKETPLACE = os.environ.get('EBAY_MARKETPLACE', 'EBAY_FR')
LIMIT = min(max(int(os.environ.get('SET_LIMIT', '20')), 1), 50)
if not CLIENT_ID or not CLIENT_SECRET:
    sys.exit('Missing EBAY_CLIENT_ID or EBAY_CLIENT_SECRET GitHub secrets')

def api(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.load(res)
    except urllib.error.HTTPError as exc:
        print(f'API error HTTP {exc.code} at {urllib.parse.urlsplit(url).path}; response omitted to protect credentials')
        sys.exit(1)

credentials = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()
token = api('https://api.ebay.com/identity/v1/oauth2/token',
            urllib.parse.urlencode({'grant_type': 'client_credentials', 'scope': 'https://api.ebay.com/oauth/api_scope'}).encode(),
            {'Authorization': 'Basic ' + credentials, 'Content-Type': 'application/x-www-form-urlencoded'})['access_token']

with open('data/catalog.json', encoding='utf-8') as f:
    raw = json.load(f)
if isinstance(raw, list):
    sets = raw
elif isinstance(raw, dict):
    sets = next((raw[k] for k in ('sets', 'catalog', 'items', 'data') if isinstance(raw.get(k), list)), None)
    if sets is None:
        sys.exit('Unknown catalog.json structure. Expected array or sets/catalog/items/data array.')
else:
    sys.exit('Invalid catalog.json structure')

print(f'Catalogue chargé : {len(sets)} références. Analyse temporaire de {min(LIMIT, len(sets))} références sur {MARKETPLACE}.')
print('Les résultats ci-dessous sont des PRIX DEMANDÉS, pas des ventes conclues. Aucun fichier de résultats eBay n’est créé.')

for entry in sets[:LIMIT]:
    reference = str(next((entry[k] for k in ('set_num', 'set_number', 'number', 'num', 'reference', 'id') if entry.get(k)), '')).split('-')[0]
    if not reference:
        print('Référence absente, entrée ignorée')
        continue
    query = urllib.parse.urlencode({'q': f'LEGO {reference}', 'limit': 50})
    result = api('https://api.ebay.com/buy/browse/v1/item_summary/search?' + query,
                 headers={'Authorization': 'Bearer ' + token, 'X-EBAY-C-MARKETPLACE-ID': MARKETPLACE, 'Accept': 'application/json'})
    prices = []
    for item in result.get('itemSummaries', []):
        title = str(item.get('title', ''))
        if not re.search(r'(?<!\d)' + re.escape(reference) + r'(?!\d)', title):
            continue
        if re.search(r'\b(instruction|notice|manual|sticker|autocollant|boite vide|empty box|box only|minifig|figurine|compatible|moc)\b', title, re.I):
            continue
        price = item.get('price') or {}
        if price.get('currency') != 'EUR':
            continue
        try:
            prices.append(float(price['value']))
        except (ValueError, TypeError, KeyError):
            continue
    median = f'{statistics.median(prices):.2f} EUR' if prices else 'non disponible'
    print(f'{reference}: {result.get("total", "?")} annonces correspondantes selon eBay; {len(prices)} offres filtrées sur les 50 premières; médiane indicative {median}')
print('Terminé : pas de sauvegarde ni de publication des données eBay.')
