# Examples

Examples for using scalesocket. The examples require Docker for running.

## Chat (javascript)

The most basic example. A chat based on wrapping [cat(1)](https://linux.die.net/man/1/cat) without any backend code.

```sh
cd examples/
docker compose up --build chat
````

## Game (javascript + python)

A simple canvas-based game using [Pixi.js](https://pixijs.com/) and a single python file as the backend.

```sh
cd examples/
docker compose up --build game
````


