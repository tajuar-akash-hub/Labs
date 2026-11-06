import botocore.session
s=botocore.session.get_session()
for endpoint, label in [('http://127.0.0.1:9000','ip9000'),('http://localhost:4566','localhost4566'),('http://127.0.0.1:9001','ip9001')]:
    c=s.create_client('s3', region_name='ap-southeast-1', endpoint_url=endpoint,
                      aws_access_key_id='a', aws_secret_access_key='b')
    def cap(request, **kw):
        print(label, request.url)
        raise SystemExit
    c.meta.events.register('before-send.s3.ListBuckets', cap)
    try:
        c.list_buckets()
    except SystemExit:
        pass
    except Exception as e:
        print(label, 'ERR', type(e).__name__, str(e)[:200])
