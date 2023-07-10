import { observer } from "mobx-react-lite";

import { FileUploader } from "@nextgisweb/file-upload/file-uploader";

import i18n from "@nextgisweb/pyramid/i18n!tileset";

const uploaderMessages = {
    uploadText: i18n.gettext("Select a dataset"),
    helpText: i18n.gettext("Dataset should be in MBTiles format."),
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
