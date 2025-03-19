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