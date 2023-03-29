import { PropTypes } from "prop-types";

import { Button, Dropdown } from "@nextgisweb/gui/antd";

import settings from "@nextgisweb/pyramid/settings!feature_layer";
import i18n from "@nextgisweb/pyramid/i18n!feature_layer";

import { useExportFeatureLayer } from "../../hook/useExportFeatureLayer";

import ExportIcon from "@material-icons/svg/file_download";

const exportFormats = settings.export_formats;

let formatItems = exportFormats.map((format) => ({
    key: format.name,
    label: format.display_name,
}));

const exportTitleMsg = i18n.gettext("Export");
const gotToSettingsTitleMsg = i18n.gettext("Export settigns");

const settingsKey = "go-to-settings";

export const ExportAction = ({ id, query, size = "middle" }) => {
    const { exportFeatureLayer, openExportPage, exportLoading } =
        useExportFeatureLayer({ id });

    const handleMenuClick = (e) => {
        const params = { ilike: query };
        if (e.key === settingsKey) {
            openExportPage(params);
        } else {
            params.format = e.key;
            exportFeatureLayer(params);
        }
    };

    const menuProps = {
        items: [
            {
                key: settingsKey,
                label: gotToSettingsTitleMsg,
            },
            {
                type: "divider",
            },
            ...formatItems,
        ],
        onClick: handleMenuClick,
    };

    return (
        <Dropdown menu={menuProps}>
            <Button icon={<ExportIcon />} size={size} loading={exportLoading}>
                {exportTitleMsg}
            </Button>
        </Dropdown>
    );
};

ExportAction.propTypes = {
    query: PropTypes.string,
    id: PropTypes.number,
    size: PropTypes.oneOf(["small", "middle", "large"]),
};
