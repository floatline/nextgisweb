import type { EditorStore } from "../type/EditorStore";
import type { FeatureEditorStore } from "./FeatureEditorStore";

export interface AttributesFormProps {
    store: FeatureEditorStore;
}

export interface FeatureEditorWidgetProps {
    /** Resource id */
    id: number;
    feature_id: number;
}

export interface FeatureEditorStoreOptions {
    resourceId: number;
    featureId: number;
}

export interface EditorWidgetProps<
    V = unknown,
    S extends EditorStore<V> = EditorStore<V>,
> {
    store: S;
}
