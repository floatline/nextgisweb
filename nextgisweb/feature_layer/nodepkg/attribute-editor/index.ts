import AttributeEditorStore from "./AttributeEditorStore";

import i18n from "@nextgisweb/pyramid/i18n";

import type { EditorWidgetRegister } from "@nextgisweb/feature-layer/type";
import type { NgwAttributeValue } from "./type";

const titleText = i18n.gettext("Attachments");

const editorWidgetRegister: EditorWidgetRegister<NgwAttributeValue> = {
    component: () => import("./AttributeEditor"),
    store: AttributeEditorStore,
    label: titleText,
};

export default editorWidgetRegister;
