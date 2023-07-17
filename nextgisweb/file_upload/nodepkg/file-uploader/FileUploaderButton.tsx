import { InboxOutlined } from "@ant-design/icons";
import { Upload, Button } from "@nextgisweb/gui/antd";

import { useFileUploader } from "./hook/useFileUploader";
import locale from "./locale";

import type { FileUploaderProps } from "./type";

export function FileUploaderButton({
    showProgressInDocTitle,
    setFileMeta,
    uploadText = locale.btnUploadText,
    inputProps,
    onChange,
    fileMeta,
    multiple,
    accept,
}: FileUploaderProps) {
    const { uploading, props } = useFileUploader({
        showProgressInDocTitle,
        setFileMeta,
        inputProps,
        fileMeta,
        onChange,
        multiple,
        accept,
    });

    return (
        <Upload {...props}>
            <Button icon={<InboxOutlined />} loading={uploading}>
                {uploadText}
            </Button>
        </Upload>
    );
}
