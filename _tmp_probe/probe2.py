import json,urllib.request,urllib.error
def get(url, hdrs=None):
    req=urllib.request.Request(url, headers=hdrs or {})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read()[:400]
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300]
    except Exception as e:
        return 'ERR', str(e)[:200].encode()

for reg, repo in [('ghcr.io','minio/minio'), ('ghcr.io','minio/minio-server'), ('public.ecr.aws','minio/minio')]:
    st, body = get(f'https://{reg}/token?service={reg}&scope=repository:{repo}:pull')
    tok=None
    try: tok=json.loads(body)['token']
    except Exception: pass
    print(reg, repo, 'token-status', st, 'has-token', bool(tok))
    if tok:
        print('  manifest ->', get(f'https://{reg}/v2/{repo}/manifests/latest', {'Authorization':f'Bearer {tok}','Accept':'application/vnd.docker.distribution.manifest.list.v2+json,application/vnd.oci.image.index.v1+json'})[0])
