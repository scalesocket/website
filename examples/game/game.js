export class Game {
    constructor(app, ws, resources) {
        this.app = app;
        this.ws = ws;
        this.resources = resources;
        this.events = new EventEmitter(ws);
        this.state = new GameState(this.app.stage, resources);
    }

    async init() {
        // Handle events
        this.events.addEventListener('client.pointerdown', (event) => {
            this.send('input', event.detail);
        });

        this.events.addEventListener('server.state', (event) => {
            this.state.update(event.detail);
            const userCount = Object.values(event.detail.players).length;
            document.getElementById("usercount").textContent = `${userCount} user${userCount > 1 ? 's' : ''} online`;
        });

        this.events.addEventListener('server.leave', (event) => {
            this.state.remove(event.detail);
        });

        // Background
        const graphics = new PIXI.Graphics();
        graphics.beginFill(0xF9FAFB);
        graphics.drawRect(0, 0, this.app.screen.width, this.app.screen.height);
        graphics.endFill();
        this.app.stage.addChild(graphics);

        // Info text
        const style = new PIXI.TextStyle({
            fontFamily: 'Arial',
            fontSize: 12,
            fill: '#aaaaaa',
            lineJoin: 'round',
        });
        const infoText = new PIXI.Text('Multiplayer example, try tapping around.', style);
        infoText.x = 5;
        infoText.y = 5;
        this.app.stage.addChild(infoText);

        // Listen to clicks
        this.app.stage.interactive = true;
        this.app.stage.on('pointerdown', (e) => {
            this.events.emit('pointerdown', e.global);
        });

        // Interpolate sprite positions on every tick
        PIXI.Ticker.shared.add((dt) => this.state.interpolate(dt));
    }

    send(op, data = {}) {
        this.ws.send(JSON.stringify({ op, data }));
    }
}

class GameState {
    players = {
        // Contains player states in the form
        // "id" : { "pos": [1, 2], "sprite": Sprite }
    }

    constructor(stage, resources) {
        this.stage = stage;
        this.resources = resources;
    }

    update(data) {
        for (const [id, pos] of Object.entries(data?.players ?? {})) {
            if (!(id in this.players)) {
                this._addPlayer(id, pos);
            } else {
                this._movePlayer(id, pos);
            }
        }
    }

    remove(id) {
        this._delPlayer(id);
    }

    interpolate(dt) {
        for (const { pos, sprite } of Object.values(this?.players ?? {})) {
            const [x, y] = pos;
            const dx = (x - sprite.x) / 3;
            const dy = (y - sprite.y) / 3;
            sprite.x += dx;
            sprite.y += dy;
        }
    }

    _addPlayer(id, pos) {
        const [x, y] = pos;
        const sprite = new PIXI.Sprite(new PIXI.Texture(this.resources.bunny.baseTexture));
        sprite.anchor.set(0.5);
        sprite.x = x;
        sprite.y = y;

        this.players[id] = { pos, sprite };
        this.stage.addChild(sprite);
    }

    _delPlayer(id) {
        if (id in this.players) {
            const sprite = this.players[id].sprite;
            this.stage.removeChild(sprite);
            sprite.destroy();
            delete this.players[id];
        }
    }

    _movePlayer(id, pos) {
        this.players[id].pos = pos
    }

}

class EventEmitter extends EventTarget {
    constructor(ws) {
        super();

        // emit websocket messages as events
        ws.addEventListener('message', (event) => {
            const payload = JSON.parse(event.data);
            this.emit(payload.op, payload.data, 'server');
        });
    }

    emit(op, data = {}, prefix = 'client') {
        this.dispatchEvent(new CustomEvent(`${prefix}.${op}`, { detail: data }));
    }
}
