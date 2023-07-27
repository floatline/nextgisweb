import { makeAutoObservable } from "mobx";

import type { EditorStore as IEditorStore } from "@nextgisweb/feature-layer/type";
import type { ExtensionValue } from "@nextgisweb/feature-layer/type";

class EditorStore implements IEditorStore<ExtensionValue<string>> {
    value: ExtensionValue<string> = null;

    constructor() {
        makeAutoObservable(this, {});
    }

    load = (value: ExtensionValue<string>) => {
        this.value = value;
    };
}

export default EditorStore;
