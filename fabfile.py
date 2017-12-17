from datetime import datetime
from hashlib import md5
from fabric.api import run, local, env, get, put, runs_once, execute, task
from fabric.contrib.files import exists

PROJECT = 'my_project'
HTTP_PORT = 8000

# Container environment
ENVIRONMENT = {
    'CONFIG': '/app/settings/prod.py',
    'STATSD_OPTS': None  # '-g carbon-host -p my_project'
}

# Workaround for true container OSes, like CoreOS.
PYTHON = 'docker run --rm -u $UID:$GROUPS -v /:/mnt -w /mnt$PWD -it frolvlad/alpine-python3 python'

if not env.hosts:
    env.hosts = ['host1']


def image_hash():
    hsh = md5()
    hsh.update(open('docker/Dockerfile.base', 'rb').read())
    hsh.update(open('docker/Dockerfile.deps', 'rb').read())
    hsh.update(open('docker/Dockerfile', 'rb').read())
    hsh.update(open('requirements.txt', 'rb').read())
    return hsh.hexdigest()[:10]


def get_evars():
    return ' '.join(f'-e "{k}={v}"' for k, v in ENVIRONMENT.items() if v)


@task
def init():
    """Prepares directory structure on a remote host"""
    run(f'''
        mkdir -p ~/{PROJECT}/images ~/{PROJECT}/data ~/{PROJECT}/bin
    ''')
    put('etc/clean-expired', f'{PROJECT}/bin', mode=0o755)


@runs_once
@task
def prepare_image():
    """Builds local docker image"""
    hsh = image_hash()
    local(f'''
        docker inspect {PROJECT}:{hsh} > /dev/null \\
        || docker/build.sh {PROJECT} {hsh} \\
        && docker save {PROJECT}:{hsh} | gzip -1 > /tmp/image.tar.gz
    ''')


@task
def push_image():
    """Checks for changes in docker image and uploads new image to remote host"""
    hsh = image_hash()
    image_file = f'{PROJECT}/images/{hsh}.tar.gz'
    if not exists(image_file):
        execute(prepare_image)
        put('/tmp/image.tar.gz', image_file)
    run(f'''
        docker load -i {image_file}
        {PYTHON} {PROJECT}/bin/clean-expired -c 3 -t 15 '{PROJECT}/images/*.tar.gz'
    ''')


@task
def backup(fname=f'/tmp/{PROJECT}-backup.tar.gz'):
    """Makes backup of data dir on a remote host"""
    run(f'tar -C {PROJECT}/data -czf /tmp/backup.tar.gz .')
    get('/tmp/backup.tar.gz', fname)


@task
def restore(fname=f'/tmp/{PROJECT}-backup.tar.gz'):
    """Restores backup"""
    put(fname, '/tmp/backup.tar.gz')
    run(f'tar -C {PROJECT}/data xf /tmp/backup.tar.gz .')


@runs_once
@task
def pack_backend():
    """Makes archive with all code"""
    hsh = image_hash()
    local(f'''
        echo {hsh} > image.hash
        ( git ls-files && echo image.hash ) | tar czf /tmp/backend.tar.gz -T -
     ''')


@task
def upload():
    """Uploads code archive to remote host and switches app link"""
    version = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    execute(pack_backend)
    put('/tmp/backend.tar.gz', PROJECT)
    run(f'''
        cd {PROJECT}
        mkdir app-{version}
        tar -C app-{version} -xf backend.tar.gz
        ln -snf app-{version} app
        {PYTHON} bin/clean-expired -c 10 -t 30 'app-*'
    ''')


@task
def restart():
    """Restarts service"""
    evars = get_evars()
    run(f'''
        docker stop -t 10 {PROJECT}-http
        docker rm {PROJECT}-http || true
        cd {PROJECT}
        docker run -d --name {PROJECT}-http -p {HTTP_PORT}:5000 {evars} \\
                   -v $PWD/app:/app -v $PWD/data:/data -w /app -u $UID:$GROUPS \\
                   {PROJECT}:`cat app/image.hash` uwsgi --ini /app/etc/uwsgi.ini
        sleep 3
        docker logs --tail 10 {PROJECT}-http
    ''')


@task
def migrate(revision='head'):
    """Applies migrations"""
    evars = get_evars()
    run(f'''
        cd {PROJECT}
        docker run --rm {evars} -it \\
                   -v $PWD/app:/app -v $PWD/data:/data -w /app -u $UID:$GROUPS \\
                   {PROJECT}:`cat app/image.hash` alembic upgrade {revision}
    ''')


@task
def shell():
    """Run shell inside container"""
    evars = get_evars()
    run(f'''
        cd {PROJECT}
        docker run --rm {evars} -it \\
                   -v $PWD/app:/app -v $PWD/data:/data -w /app -u $UID:$GROUPS \\
                   {PROJECT}:`cat app/image.hash` sh
    ''')
