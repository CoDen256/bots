dev PROJECT TAG="latest":
    docker run -d -v "$PWD"/{{PROJECT}}/main.py:/app/main.py coden256/{{PROJECT}}:{{TAG}}

sh PROJECT TAG="latest":
    docker run -it --entrypoint /bin/sh -v "$PWD"/{{PROJECT}}/main.py:/app/main.py coden256/{{PROJECT}}:{{TAG}}

run PROJECT TAG="latest":
    docker run -d coden256/{{PROJECT}}:{{TAG}}

build PROJECT TAG="latest":
    docker build {{PROJECT}} -t coden256/{{PROJECT}}:{{TAG}}

push PROJECT TAG="latest":
    docker push coden256/{{PROJECT}}:{{TAG}}

undeploy TARGET PROJECT TAG="latest":
    #!/usr/bin/env bash
    set -euxo pipefail
    target=`ssh root@{{TARGET}} "docker ps -a -q --filter ancestor=coden256/{{PROJECT}} --format='{{{{.ID}}'"`
    echo Removing $target
    ssh root@{{TARGET}} "docker stop $target || true"
    ssh root@{{TARGET}} "docker rm $target || true"

deploy TARGET PROJECT TAG="latest": (undeploy TARGET PROJECT TAG)
    ssh root@{{TARGET}} "docker pull coden256/{{PROJECT}}:{{TAG}} && docker run -d coden256/{{PROJECT}}:{{TAG}}"