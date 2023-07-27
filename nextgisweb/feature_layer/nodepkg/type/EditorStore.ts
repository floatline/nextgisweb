import type { FeatureEditorStore } from "../feature-editor/FeatureEditorStore";

export interface EditorStoreConstructorOptions {
    parentStore: FeatureEditorStore;
}

export interface EditorStore<V = unknown> {
    value: V;

    load: (value: V) => void;

    isValid?: boolean;
}
