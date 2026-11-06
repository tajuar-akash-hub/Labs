import json,urllib.request,urllib.error
def get(url):
    try:
        with urllib.request.urlopen(url, timeout=25) as r: return r.status, r.read().decode('utf8','ignore')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf8','ignore')[:500]
    except Exception as e: return 'ERR', str(e)[:200]
st, body = get('https://api.github.com/repos/s3s-project/s3s/git/trees/5761ddfe4c509fcac87e3b99fd5bd9e176b442c0?recursive=1')
print(st)
try:
    d=json.loads(body)
    for t in d['tree']:
        if 'sigv4' in t['path'] and t['path'].endswith('.rs'):
            print(t['path'])
except Exception as e:
    print(e, body[:300])
