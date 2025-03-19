dev PROJECT TAG="latest":
    docker run -d -v "$PWD"/{{PROJECT}}/main.py:/app/main.py coden256/{{PROJECT}}:{{TAG}}

sh PROJECT TAG="latest":
    docker run -it --entrypoint /bin/sh -v "$PWD"/{{PROJECT}}/main.py:/app/main.py coden256/{{PROJECT}}:{{TAG}}