# syntax=docker/dockerfile:1.2
FROM scalesocket/scalesocket:latest
RUN apk add --no-cache python3

WORKDIR /app
COPY index.html game.js bunny.png /var/www/public/
COPY game.py .

CMD scalesocket --addr 0.0.0.0:5000 --staticdir /var/www/public/\
    --frame=json\
    --joinmsg '{"op":"join","id":"#ID"}'\
    --leavemsg '{"op":"leave","id":"#ID"}'\
    ./game.py
