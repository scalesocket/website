# syntax=docker/dockerfile:1.2
FROM scalesocket/scalesocket:latest
RUN apk add --no-cache python3 py3-pip

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY index.html game.js assets.png /var/www/public/
COPY game.py utils.py state.py ./

CMD scalesocket --addr 0.0.0.0:5000 --staticdir /var/www/public/\
    --frame=json\
    --joinmsg '{"type":"join","id":#ID}'\
    --leavemsg '{"type":"leave","id":#ID}'\
    ./game.py
