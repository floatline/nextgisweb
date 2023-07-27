/** @entrypoint */
import DescriptionEditorStore from "./AttachmentEditorStore";

import i18n from "@nextgisweb/pyramid/i18n";

import type { EditorWidgetRegister } from "@nextgisweb/feature-layer/type";
import type { DataSource } from "./type";

const titleText = i18n.gettext("Attachment");

const editorWidgetRegister: EditorWidgetRegister<DataSource[]> = {
    component: () => import("./AttachmentEditor"),
    store: DescriptionEditorStore,
    label: titleText,
};

export default editorWidgetRegister;
