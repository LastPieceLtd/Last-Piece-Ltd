"""Test read-only of eBay Browse API; no credentials or listings are stored."""
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

client_id = os.environ.get('EBAY_CLIENT_ID', '').strip()
client_secret = os.environ.get('EBAY_CLIENT_SECRET', '').strip()
if not client_id or not client_secret:
    sys.exit('ERREUR : secret EBAY_CLIENT_ID ou EBAY_CLIENT_SECRET absent.')


def request(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            return json.load(response)
    except urllib.error.HTTPError as err:
        body = err.read().decode('utf-8', errors='replace')[:1000]
        # API errors may contain details, but never print auth headers or credentials.
        print(f'Erreur HTTP {err.code} pour {urllib.parse.urlsplit(url).path}: {body}')
        sys.exit(1)

credentials = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()
token = request(
    'https://api.ebay.com/identity/v1/oauth2/token',
    data=urllib.parse.urlencode({'grant_type': 'client_credentials', 'scope': 'https://api.ebay.com/oauth/api_scope'}).encode(),
    headers={'Authorization': 'Basic ' + credentials, 'Content-Type': 'application/x-www-form-urlencoded'},
)
access_token = token['access_token']
print('Authentification eBay : OK')
params = urllib.parse.urlencode({'q': 'LEGO 75367', 'limit': 5})
results = request(
    'https://api.ebay.com/buy/browse/v1/item_summary/search?' + params,
    headers={'Authorization': 'Bearer ' + access_token, 'X-EBAY-C-MARKETPLACE-ID': 'EBAY_FR', 'Accept': 'application/json'},
)
print('Recherche LEGO 75367 : OK')
print('Nombre total d’annonces renvoyé par eBay :', results.get('total', 'non indiqué'))
for item in results.get('itemSummaries', []):
    price = item.get('price', {})
    print('-', str(item.get('title', 'Sans titre'))[:110], '|', price.get('value', '?'), price.get('currency', ''))
print('TEST TERMINÉ : il s’agit de prix demandés, pas de ventes conclues.')
