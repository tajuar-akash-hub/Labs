import json,urllib.request,urllib.error,re
def get(url):
    try:
        with urllib.request.urlopen(url, timeout=25) as r: return r.status, r.read().decode('utf8','ignore')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf8','ignore')[:300]
    except Exception as e: return 'ERR', str(e)[:200]
st, body = get('https://api.github.com/repos/s3s-project/s3s/git/trees/5761ddfe4c509fcac87e3b99fd5bd9e176b442c0?recursive=1')
d=json.loads(body)
cands=[t['path'] for t in d['tree'] if t['path'].endswith('.rs') and 'crates/s3s/src' in t['path']]
print(len(cands))
for p in cands:
    s,b=get('https://raw.githubusercontent.com/s3s-project/s3s/5761ddfe4c509fcac87e3b99fd5bd9e176b442c0/'+p)
    if s!=200: continue
    hits=[f'{i}: {l.strip()[:170]}' for i,l in enumerate(b.splitlines(),1) if re.search(r'InvalidRegion|AuthorizationHeaderMalformed|aws_region',l)]
    if hits:
        print('===',p)
        print('\n'.join('  '+h for h in hits[:12]))
