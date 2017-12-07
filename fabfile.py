from datetime import datetime
from hashlib import md5
from fabric.api import run, local, env, get, put, runs_once, execute

env.hosts = ['host1']
PRJ_NAME = 'PROJECT'


def init():
    run(f'mkdir -p ~/{PRJ_NAME}/images ~/{PRJ_NAME}/data')


def image_hash():
    hsh = md5()
    hsh.update(open('docker/Dockerfile', 'rb').read())
    hsh.update(open('requirements.txt', 'rb').read())
    return hsh.hexdigest()[:10]


@runs_once
def prepare_image():
    hsh = image_hash()
    local(f'''
        docker inspect {PRJ_NAME}:{hsh} > /dev/null || docker build -t {PRJ_NAME}:{hsh} docker
        docker save {PRJ_NAME}:{hsh} | gzip -1 > /tmp/image.tar.gz
    ''')


def push_image():
    hsh = image_hash()
    execute(prepare_image)
    local(f'rsync -P /tmp/image.tar.gz {env.host}:{PRJ_NAME}/images/{hsh}.tar.gz')
    run(f'docker load -i {PRJ_NAME}/images/{hsh}.tar.gz')


def backup(fname=f'/tmp/{PRJ_NAME}-backup.tar.gz'):
    run(f'tar -C {PRJ_NAME}/data -czf /tmp/backup.tar.gz .')
    get('/tmp/backup.tar.gz', fname)


def restore(fname=f'/tmp/{PRJ_NAME}-backup.tar.gz'):
    put(fname, '/tmp/backup.tar.gz')
    run(f'tar -C {PRJ_NAME}/data xf /tmp/backup.tar.gz .')


@runs_once
def pack_backend():
    hsh = image_hash()
    local(f'''
        echo {hsh} > image_hash
        ( git ls-files && echo image_hash ) | tar czf /tmp/backend.tar.gz -T -
     ''')


def upload():
    version = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    execute(pack_backend)
    put('/tmp/backend.tar.gz', PRJ_NAME)
    run(f'''
        cd {PRJ_NAME}
        mkdir app-{version}
        tar -C app-{version} -xf backend.tar.gz
        ln -snf app-{version} app
    ''')


def restart():
    run(f'''
        docker stop -t 10 {PRJ_NAME}-http
        docker rm {PRJ_NAME}-http || true
        cd {PRJ_NAME}
        docker run -d --name {PRJ_NAME}-http -p 5000:5000 -e CONFIG=/data/config.py \\
                   -v $PWD/app:/app -v $PWD/data:/data -w /app -u $UID \\
                   {PRJ_NAME}:`cat app/image_hash` uwsgi --ini /app/uwsgi.ini
        sleep 3
        docker logs --tail 10 {PRJ_NAME}-http
    ''')


def shell():
    run(f'''
        cd {PRJ_NAME}
        docker run --rm -e CONFIG=/data/config.py -it \\
                   -v $PWD/app:/app -v $PWD/data:/data -w /app -u $UID \\
                   {PRJ_NAME}:`cat app/image_hash` bash
    ''')
