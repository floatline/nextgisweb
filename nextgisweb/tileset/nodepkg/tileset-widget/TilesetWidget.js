import { observer } from "mobx-react-lite";

import { FileUploader } from "@nextgisweb/file-upload/file-uploader";

import i18n from "@nextgisweb/pyramid/i18n";

const uploaderMessages = {
    uploadText: i18n.gettext("Select a dataset"),
    helpText: i18n.gettext("MBTiles and ZIP formats are supported."),
}

export const TilesetWidget = observer(({ store }) => {
    return (
        <div>
            <FileUploader
                onChange={(value) => {
                    store.source = value;
                }}
                onUploading={(value) => {
                    store.uploading = value;
                }}
                showMaxSize
                {...uploaderMessages}
            />
        </div>
    );
});

TilesetWidget.title = i18n.gettext("Tileset");
TilesetWidget.activateOn = { create: true };
