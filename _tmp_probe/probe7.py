import urllib.request,urllib.error,re
def get(url):
    try:
        with urllib.request.urlopen(url, timeout=25) as r: return r.status, r.read().decode('utf8','ignore')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf8','ignore')[:300]
    except Exception as e: return 'ERR', str(e)[:200]
base='https://raw.githubusercontent.com/s3s-project/s3s/5761ddfe4c509fcac87e3b99fd5bd9e176b442c0/'
s,b=get(base+'crates/s3s/src/config.rs')
lines=b.splitlines()
print('\n'.join(f'{i}: {l}' for i,l in enumerate(lines[200:250],201)))
