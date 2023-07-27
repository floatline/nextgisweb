import { makeAutoObservable, runInAction } from "mobx";

import { parseNgwAttribute, formatNgwAttribute } from "../util/ngwAttributes";

import type {
    EditorStoreConstructorOptions,
    FeatureLayerField,
    EditorStore,
} from "@nextgisweb/feature-layer/type";

import type { FeatureEditorStore } from "../feature-editor/FeatureEditorStore";
import type { AppAttributes, NgwAttributeValue } from "./type";

class AttributeEditorStore implements EditorStore<NgwAttributeValue> {
    value: NgwAttributeValue | null = null;

    readonly _parentStore: FeatureEditorStore;

    constructor({ parentStore }: EditorStoreConstructorOptions) {
        this._parentStore = parentStore;
        makeAutoObservable(this, { _parentStore: false });
    }

    load(value: NgwAttributeValue) {
        this.value = value;
    }

    /** Feature field values formatted for web */
    get attributes() {
        const values: AppAttributes = {};
        if (this.value) {
            for (const field of this.fields) {
                const { keyname, datatype } = field;
                const val = this.value[keyname];
                values[keyname] = parseNgwAttribute(datatype, val);
            }
        }
        return values;
    }

    get fields(): FeatureLayerField[] {
        return this._parentStore.fields;
    }

    setValues = (values: AppAttributes = {}) => {
        runInAction(() => {
            this.value = this._formatAttributes(values);
        });
    };

    private _formatAttributes(values: AppAttributes) {
        const attributes = { ...this.value };
        for (const key in values) {
            const val = values[key];
            const field = this.fields.find((f) => f.keyname === key);
            if (field) {
                attributes[key] = formatNgwAttribute(field.datatype, val);
            }
        }
        return attributes;
    }
}

export default AttributeEditorStore;
