import { Suspense, useState, useEffect, lazy } from "react";

import { Tabs } from "@nextgisweb/gui/antd";
import i18n from "@nextgisweb/pyramid/i18n";
import settings from "@nextgisweb/pyramid/settings!";
import entrypoint from "@nextgisweb/jsrealm/entrypoint";
import { SaveButton } from "@nextgisweb/gui/component/SaveButton";

import { FeatureEditorStore } from "./FeatureEditorStore";

import type { EditorWidgetRegister } from "../type";
import type { FeatureEditorWidgetProps } from "./type";

type TabProps = Parameters<typeof Tabs>[0];

const AttributesForm = lazy(() => import("./AttributesForm"));

const saveText = i18n.gettext("Save");
const attributesTabText = i18n.gettext("Attributes");

export const FeatureEditorWidget = ({
    feature_id,
    id,
}: FeatureEditorWidgetProps) => {
    const [store] = useState(
        () => new FeatureEditorStore({ resourceId: id, featureId: feature_id })
    );

    const [items, setItems] = useState<TabProps["items"]>([]);

    useEffect(() => {
        const loadWidgets = async () => {
            const items_: TabProps["items"] = [
                {
                    key: "attributes",
                    label: attributesTabText,
                    children: (
                        <Suspense fallback="loading...">
                            <AttributesForm store={store}></AttributesForm>,
                        </Suspense>
                    ),
                },
            ];

            for (const key in settings.editor_widget) {
                const mid = settings.editor_widget[key];
                try {
                    const widgetResource = (await entrypoint(mid))
                        .default as EditorWidgetRegister;

                    const widgetStore = new widgetResource.store({
                        featureId: feature_id,
                        resourceId: id,
                    });
                    store.addExtensionStore(key, widgetStore);

                    const Widget = lazy(
                        async () => await widgetResource.component()
                    );
                    items_.push({
                        key,
                        label: widgetResource.label,
                        children: (
                            <Suspense fallback="loading...">
                                <Widget store={widgetStore}></Widget>
                            </Suspense>
                        ),
                    });
                } catch (er) {
                    console.error(er);
                }
            }

            setItems(items_);
        };
        loadWidgets();
    }, [feature_id, id, store]);

    return (
        <Tabs
            items={items}
            tabBarExtraContent={
                <SaveButton loading={store.saving} onClick={store.save}>
                    {saveText}
                </SaveButton>
            }
        />
    );
};
