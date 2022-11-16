interface Event {
  detail: any;
  data: any;
  global?: { x: number; y: number };
}

type Pixi = {
  screen: any;
  stage: any;
  [key: string]: type;
};

declare const PIXI: Pixi;

type Point = [number, number];

type Player = {
  id?: number;
  pos: Point;
  sprite: any;
};

type Item = {
  id?: number;
  type: string;
  pos: Point;
  sprite: any;
};

type StateUpdate = {
  players: Record<string, Player>;
  items: Array<Item>;
  map: { data: number[][] };
};
