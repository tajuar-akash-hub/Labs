import json,urllib.request,urllib.error,re
def get(url):
    try:
        with urllib.request.urlopen(url, timeout=25) as r: return r.status, r.read().decode('utf8','ignore')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf8','ignore')[:600]
    except Exception as e: return 'ERR', str(e)[:200]
base='https://raw.githubusercontent.com/s3s-project/s3s/5761ddfe4c509fcac87e3b99fd5bd9e176b442c0/'
for f in ['crates/s3s/src/s3.rs']:
    st, body = get(base+f)
    print('===',f,st)
    for i,l in enumerate(body.splitlines(),1):
        if re.search(r'aws_region|InvalidRegion|AuthorizationHeaderMalformed|check_integrity|region', l):
            print(f'  {i}: {l.strip()[:190]}')
