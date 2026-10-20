
    
  
"""Test en lecture seule de plusieurs références BrickEconomy.

Ne publie ni la clé API, ni les prix, ni les réponses complètes.
"""
import json
import os
import urllib.error
import urllib.request

BASE = 'https://www.brickeconomy.com/api/v1'
SETS = ('75367-1', '75192-1', '75252-1', '75060-1')
key = os.environ.get('BRICKECONOMY_API_KEY')
if not key:
    raise SystemExit('Secret BRICKECONOMY_API_KEY absent.')

headers = {
    'Accept': 'application/json',
    'User-Agent': 'LastPieceLtd-MarketResearch/1.0',
    'x-apikey': key,
}

def fetch(path):
    request = urllib.request.Request(BASE + path, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        print(f'Erreur HTTP {error.code} pour {path.split("?")[0]} (aucun détail sensible affiché).')
        return None
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        print(f'Requête impossible pour {path.split("?")[0]} : {type(error).__name__}')
        return None

def populated(obj, field):
    return field in obj and obj[field] is not None and obj[field] != ''

usage_result = fetch('/usage')
if isinstance(usage_result, dict):
    usage = usage_result.get('data', {})
    if isinstance(usage, dict):
        print('Quota quotidien :', usage.get('quota', 'non communiqué'))
        print('Requêtes restantes avant test :', usage.get('remaining', 'non communiqué'))

print('Analyse de', len(SETS), 'références ; aucun prix ni résultat complet ne sera enregistré.')
for number in SETS:
    print('\n---', number, '---')
    result = fetch(f'/set/{number}?currency=EUR')
    if not isinstance(result, dict):
        continue
    data = result.get('data')
    if not isinstance(data, dict) or not data.get('set_number'):
        print('Fiche non reconnue ou réponse inattendue.')
        continue
    print('Nom :', data.get('name', 'non communiqué'))
    print('Référence :', data.get('set_number'))
    print('Devise :', data.get('currency', 'non communiquée'))
    print('Valeur neuve disponible :', isinstance(data.get('current_value_new'), (int, float)))
    for label, fields in (
        ('Croissance sur 12 mois', ('rolling_growth_12months', 'rolling_growth_lastyear')),
        ('Prévision 2 ans', ('forecast_value_new_2_years',)),
        ('Prévision 5 ans', ('forecast_value_new_5_years',)),
    ):
        print(label + ' :', any(populated(data, f) for f in fields))
    events = data.get('price_events_new')
    print('Nombre d’événements de prix :', len(events) if isinstance(events, list) else 'non fourni')
    # Uniquement les noms des champs, jamais leurs valeurs.
    print('Champs disponibles :', ', '.join(sorted(data.keys())))

print('\nTest terminé. Aucune réponse ni donnée de prix sauvegardée.')

