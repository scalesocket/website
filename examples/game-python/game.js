//@ts-check
/// <reference path="./index.d.ts" />

export class Game {
    /**
     * @param {Pixi} app
     * @param {WebSocket} ws
     * @param {Record<string, any>} resources
     */
    constructor(app, ws, resources) {
        this.app = app;
        this.ws = ws;
        this.resources = resources;
        this.events = new EventEmitter(ws);

        this.layers = {
            fg: new PIXI.Container(),
            mg: new PIXI.Container(),
            bg: new PIXI.Container(),
        }
        this.app.stage.addChild(this.layers.bg);
        this.app.stage.addChild(this.layers.mg);
        this.app.stage.addChild(this.layers.fg);

        this.state = new GameState(this.app.stage, this.layers, resources);
    }

    async init() {
        // Handle events
        this.events.addEventListener('client.pointerdown', (event) => {
            this.send('input', event.detail);
        });

        this.events.addEventListener('server.state', (event) => {
            this.state.update(event.detail);
        });

        this.events.addEventListener('server.leave', (event) => {
            this.state.remove(event.detail);
        });


        // Listen to clicks
        this.app.stage.interactive = true;
        this.app.stage.on('pointerdown', (/** @type {Event} */ e) => {
            this.events.emit('pointerdown', e.global);
        });


        // Interpolate sprite positions on every tick
        PIXI.Ticker.shared.add((/** @type {number} */ dt) => this.state.interpolate(dt));
    }

    /**
     * @param {string} type
     * @param {Record<string, any>} data
     */
    send(type, data = {}) {
        this.ws.send(JSON.stringify({ type, data }));
    }
}

class GameState {
    /** @type {Record<number, Player>} */
    players = {}
    /** @type {any[][]} */
    walls = []
    /** @type {{data:any[][]}} */
    map = { data: [] }
    /** @type {Record<number, Item>} */
    items = {}

    /**
     * @param {any} stage
     * @param {Record<string,any>} layers
     * @param {Record<string, any>} resources
     */
    constructor(stage, layers, resources) {
        this.stage = stage;
        this.layers = layers;
        this.resources = resources;
    }

    /**
     * @param {StateUpdate} data
     */
    update(data) {
        // update player count
        const playerCount = Object.values(data.players).length;
        // @ts-ignore
        document.querySelector("#usercount").textContent = `${playerCount} user${playerCount > 1 ? 's' : ''} online`;

        // update players
        for (const [id, _] of Object.entries(this.players)) {
            if (id in data.players) {
                this._movePlayer(id, data.players[id].pos);
                delete data.players[id]
            } else {
                this._delPlayer(id)
            }
        }
        // new players
        for (const [id, player] of Object.entries(data?.players ?? {})) {
            this._addPlayer(id, player.pos);
        }

        // walls
        this._setMap(data?.map.data);

        // update items 
        for (const [id, item] of Object.entries(this.items)) {
            if (id in data.items) {
                delete data.players[id]
            } else {
                this._delItem(id)
            }
        }

        // new items 
        for (const [id, item] of Object.entries(data?.items ?? {})) {
            if (!(id in this.items)) {
                this._addItem(id, item.type, item.pos);
            }
        }
    }

    /**
     * @param {any} id
     */
    remove(id) {
        this._delPlayer(id);
    }

    /**
     * @param {number} dt
     */
    interpolate(dt) {
        for (const { pos, sprite } of Object.values(this?.players ?? {})) {
            const [x, y] = pos;
            const dx = (x * 32 - sprite.x) / 3;
            const dy = (y * 32 - sprite.y) / 3;
            sprite.x += dx;
            sprite.y += dy;
        }
    }
    /**
     * @param {number[][]} walls
     */
    _setMap(walls) {
        // unload current walls
        this.walls.flat().forEach(sprite => {
            if (sprite) {
                this.stage.removeChild(sprite);
                sprite.destroy();
            }
        });

        // load new walls
        this.walls = walls.map((row, y) => {
            return row.map((tile, x) => {
                const rect = new PIXI.Rectangle(tile * 32, 0, 32, 32);
                const sprite = new PIXI.Sprite(new PIXI.Texture(this.resources.assets.baseTexture, rect));
                // sprite.anchor.set(0.5);
                sprite.anchor.set(0);
                sprite.x = x * 32;
                sprite.y = y * 32;
                // sprite.zindex = -10;
                this.layers.bg.addChild(sprite);
                return sprite;
            })
        });
    }

    /**
     * @param {string} id
     * @param {[any, any]} pos
     */
    _addPlayer(id, pos) {
        const [x, y] = pos;
        const rect = new PIXI.Rectangle(0, 32, 32, 32);
        const sprite = new PIXI.Sprite(new PIXI.Texture(this.resources.assets.baseTexture, rect));

        // sprite.anchor.set(0.5);
        sprite.anchor.set(0);
        sprite.x = x * 32;
        sprite.y = y * 32;

        this.players[id] = { pos, sprite, id };
        this.layers.fg.addChild(sprite);
    }

    /**
     * @param {string} id
     */
    _delPlayer(id) {
        if (id in this.players) {
            const sprite = this.players[id].sprite;
            this.stage.removeChild(sprite);
            sprite.destroy();
            delete this.players[id];
        }
    }

    /**
     * @param {string} id
     * @param {Point} pos
     */
    _movePlayer(id, pos) {
        this.players[id].pos = pos
    }

    /**
     * @param {string} id
     * @param {string} type
     * @param {[any, any]} pos
     */
    _addItem(id, type, pos) {
        const [x, y] = pos;
        let tile = 3;
        let container = this.layers.fg;

        if (type == "explosive") {
            tile = 1;
        } else if (type == "fire") {
            tile = 2
        } else if (type == "boots") {
            tile = 3
            container = this.layers.mg;
        }
        const rect = new PIXI.Rectangle(tile * 32, 32, 32, 32);
        const sprite = new PIXI.Sprite(new PIXI.Texture(this.resources.assets.baseTexture, rect));

        sprite.anchor.set(0);
        sprite.x = x * 32;
        sprite.y = y * 32;

        this.items[id] = { pos, sprite, id };
        container.addChild(sprite);
    }

    /**
     * @param {string} id
     */
    _delItem(id) {
        if (id in this.items) {
            const sprite = this.items[id].sprite;
            this.stage.removeChild(sprite);
            sprite.destroy();
            delete this.items[id];
        }
    }
}

class EventEmitter extends EventTarget {
    /**
     * @param {WebSocket} ws
     */
    constructor(ws) {
        super();

        // emit websocket messages as events
        ws.addEventListener('message', (/** @type {{ data: string; }} */ event) => {
            const payload = JSON.parse(event.data);
            this.emit(payload.type, payload.data, 'server');
        });
    }

    /**
     * @param {string} type
     */
    emit(type, data = {}, prefix = 'client') {
        this.dispatchEvent(new CustomEvent(`${prefix}.${type}`, { detail: data }));
    }

}
