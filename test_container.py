"""CI-only actual Docker image and disposable dedicated-volume persistence check."""
import subprocess, time, urllib.request, json, uuid
suffix=uuid.uuid4().hex[:10]
name='releasepad-test-'+suffix
volume=name+'-data'
port=4193

def docker(*args):
    return subprocess.check_output(['docker',*args],text=True).strip()

def request(path,method='GET',body=None,token=None):
    headers={'Content-Type':'application/json'}
    if token: headers['X-Workspace']=token
    with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:'+str(port)+path,data=None if body is None else json.dumps(body).encode(),method=method,headers=headers),timeout=5) as response:
        return json.load(response)

def start():
    docker('run','-d','--name',name,'-p','127.0.0.1:'+str(port)+':'+str(port),'-e','PORT='+str(port),'-v',volume+':/data','releasepad-ci')
    for _ in range(100):
        try:
            assert request('/api/health')['storage']=='sqlite'
            return
        except Exception: time.sleep(.2)
    raise RuntimeError('Container did not become healthy')

try:
    docker('volume','create',volume)
    start()
    token=request('/api/workspaces','POST')['workspace']
    candidate=request('/api/candidates','POST',{'title':'Container volume test'},token)['candidate']
    for check in candidate['checks']:
        candidate=request('/api/candidates/'+candidate['id']+'/checks/'+check['id'],'PATCH',{'version':candidate['version'],'status':'pass','reference':'Synthetic container CI test'},token)['candidate']
    snapshot=request('/api/candidates/'+candidate['id']+'/snapshots','POST',{'version':candidate['version']},token)['snapshot']
    with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/') as response:
        assert b'<html' in response.read().lower()
    docker('rm','-f',name)
    start()
    restored=request('/api/candidates/'+candidate['id'],token=token)['candidate']
    saved=request('/api/candidates/'+candidate['id']+'/snapshots/'+snapshot['id'],token=token)['snapshot']
    assert restored['ready'] and restored['title']==candidate['title']
    assert saved['digest']==snapshot['digest'] and saved['payload']==snapshot['payload']
    print('PASS actual container build, non-default PORT, frontend, API, SQLite and replacement-container dedicated-volume persistence. Not a hosting-provider deployment.')
finally:
    subprocess.run(['docker','rm','-f',name],check=False)
    subprocess.run(['docker','volume','rm',volume],check=False)
