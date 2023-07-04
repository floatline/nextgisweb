import { toJS, makeAutoObservable } from "mobx";

export class TilesetStore {
    identity = "tileset";

    dump() {
        const result = {};
        return toJS(result);
    }

    get isValid() {
        return true;
    }
}
