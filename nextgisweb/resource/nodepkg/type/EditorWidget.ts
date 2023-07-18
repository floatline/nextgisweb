import type { EditorStore } from "./EditorStore";

export interface EditorWidgetProps<S extends EditorStore = EditorStore> {
    store: S;
}

import type { FunctionComponent, ForwardRefRenderFunction } from "react";

export interface ActiveOnOptions {
    create?: boolean;
}

interface EditorWidgetOptions {
    title?: string;
    activateOn?: ActiveOnOptions;
    order?: number;
}

export type EditorWidgetComponent = (
    | FunctionComponent<unknown>
    | ForwardRefRenderFunction<unknown>
) &
    EditorWidgetOptions;
