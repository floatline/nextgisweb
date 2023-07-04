import { observer } from "mobx-react-lite";
import i18n from "@nextgisweb/pyramid/i18n!tileset";
import { Button, Tabs, Modal, Upload, Checkbox } from "@nextgisweb/gui/antd";
import { useFileUploader } from "@nextgisweb/file-upload";

export const TilesetWidget = observer(({}) => {
    const onChange = (a,b,c) => {
        console.log('onchange!')
        console.log(a,b,c)
    };
    const { props } = useFileUploader({
        openFileDialogOnClick: true,
        onChange,
        multiple: false,
    });
    return (
        <div>
            <Upload {...props}>
            </Upload>
        </div>
    );
});

TilesetWidget.title = i18n.gettext("Tileset");
TilesetWidget.activateOn = { create: true };
