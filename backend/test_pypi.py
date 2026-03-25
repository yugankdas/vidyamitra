import urllib.request
import json

res = urllib.request.urlopen('https://pypi.org/pypi/hindsight-all/json')
data = json.loads(res.read())
print("hindsight-all deps:", data['info']['requires_dist'])

try:
    res = urllib.request.urlopen('https://pypi.org/pypi/hindsight-core-slim/json')
    data = json.loads(res.read())
    print("hindsight-core-slim version:", data['info']['version'])
except Exception as e:
    print("error", e)
