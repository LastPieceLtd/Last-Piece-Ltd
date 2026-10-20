import json
import os
import urllib.error
import urllib.request

key = os.environ.get('BRICKECONOMY_API_KEY')
if not key:
    raise SystemExit('Secret BRICKECONOMY_API_KEY absent.')

headers = {
    'Accept': 'application/json',
    'User-Agent': 'LastPieceLtd-MarketResearch/1.0',
    'x-apikey': key,
}

def fetch(url):
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise SystemExit(f'Erreur HTTP {error.code} lors de la requête API.') from None

usage = fetch('https://www.brickeconomy.com/api/v1/usage').get('data', {})
print('Connexion API : OK')
print('Quota quotidien :', usage.get('quota', 'non communiqué'))
print('Requêtes restantes avant le test :', usage.get('remaining', 'non communiqué'))

result = fetch('https://www.brickeconomy.com/api/v1/set/75367-1?currency=EUR')
data = result.get('data', {})
if not isinstance(data, dict) or not data.get('set_number'):
    raise SystemExit('Réponse reçue, mais fiche LEGO non reconnue.')

print('Référence trouvée :', data['set_number'])
print('Nom :', data.get('name', 'non communiqué'))
print('Devise :', data.get('currency', 'non communiquée'))
print('Valeur neuve scellée disponible :', isinstance(data.get('current_value_new'), (int, float)))
print('Croissance 12 mois disponible :', any(k in data for k in ('rolling_growth_12months', 'rolling_growth_lastyear')))
print('Prévision 2 ans disponible :', 'forecast_value_new_2_years' in data)
print('Prévision 5 ans disponible :', 'forecast_value_new_5_years' in data)
print('Événements de prix disponibles :', len(data.get('price_events_new') or []))
print('Test terminé. Aucune donnée de prix enregistrée ou affichée.')
