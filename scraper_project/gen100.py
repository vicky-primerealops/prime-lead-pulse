import requests, json, re

print('Downloading US cities dataset for Top 100...')
url = 'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/geonames-all-cities-with-a-population-1000/exports/json?refine=cou_name_en%3A%22United%20States%22'
r = requests.get(url)
data = r.json()

states = {}
for c in data:
    state = c.get('admin1_code', '').lower()
    city = c.get('name', '')
    pop = c.get('population', 0)
    if not state or not city: continue
    if state not in states: states[state] = []
    states[state].append({'name': city, 'pop': pop})

dict_str = 'CITIES = {\n'
for state, cities in sorted(states.items()):
    cities = sorted(cities, key=lambda x: x['pop'], reverse=True)
    # Bumped to Top 100!
    top_cities = [c['name'] for c in cities[:100]]
    dict_str += f'    \"{state}\": [\n'
    for i in range(0, len(top_cities), 5):
        chunk = top_cities[i:i+5]
        line = ', '.join(f'\"{c}\"' for c in chunk) + ','
        dict_str += f'        {line}\n'
    dict_str += '    ],\n'
dict_str += '}\n'

with open('Zillow_Agents_Scraper.py', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'CITIES\s*=\s*\{.*?\n\}\n'
new_content = re.sub(pattern, dict_str, content, flags=re.DOTALL)

with open('Zillow_Agents_Scraper.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'Successfully populated CITIES dictionary with Top 100 for {len(states)} states!')
