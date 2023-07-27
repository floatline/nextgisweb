import { Suspense, useState, useEffect, lazy, useCallback } from "react";
import { observer } from "mobx-react-lite";

import { Tabs } from "@nextgisweb/gui/antd";
import { gettext } from "@nextgisweb/pyramid/i18n";
import settings from "@nextgisweb/pyramid/settings!";
import entrypoint from "@nextgisweb/jsrealm/entrypoint";
import { SaveButton } from "@nextgisweb/gui/component/SaveButton";
import { ActionToolbar } from "@nextgisweb/gui/action-toolbar";

import { FeatureEditorStore } from "./FeatureEditorStore";
import editorWidgetRegister from "../attribute-editor";

import ResetIcon from "@material-icons/svg/restart_alt";

import type { AntParam } from "@nextgisweb/gui/antd";
import type { EditorWidgetRegister } from "../type";
import type { FeatureEditorWidgetProps } from "./type";

import "./FeatureEditorWidget.less";

type TabItems = AntParam<typeof Tabs, "items">;
type TabItem = TabItems[0];

const mLoading = gettext("Loading...");
const saveText = gettext("Save");

export const FeatureEditorWidget = observer(
    ({ resourceId, featureId }: FeatureEditorWidgetProps) => {
        const [store] = useState(
            () => new FeatureEditorStore({ resourceId, featureId })
        );

        const [items, setItems] = useState<TabItems>([]);

        const registerEditorWidget = useCallback(
            (key: string, newEditorWidget: EditorWidgetRegister) => {
                const widgetStore = new newEditorWidget.store({
                    parentStore: store,
                });

                const Widget = lazy(
                    async () => await newEditorWidget.component()
                );

                const DirtyMark = observer(() => {
                    if (widgetStore.dirty) {
                        if (widgetStore.reset) {
                            return (
                                <a onClick={() => widgetStore.reset()}>
                                    <ResetIcon />
                                </a>
                            );
                        } else {
                            return <>*</>;
                        }
                    }
                    return null;
                });

                const TabLabel = observer(() => {
                    return (
                        <>
                            <span>{newEditorWidget.label}</span>
                            {widgetStore.counter && (
                                <span>({widgetStore.counter})</span>
                            )}
                            <span>
                                <DirtyMark />
                            </span>
                        </>
                    );
                });

                const newWidget: TabItem = {
                    key,
                    label: <TabLabel />,
                    children: (
                        <Suspense fallback={mLoading}>
                            <Widget store={widgetStore}></Widget>
                        </Suspense>
                    ),
                };
                setItems((old) => [...old, newWidget]);
                return { widgetStore };
            },
            [store]
        );

        useEffect(() => {
            const loadWidgets = async () => {
                for (const key in settings.editor_widget) {
                    const mid = settings.editor_widget[key];
                    try {
                        const widgetResource = (await entrypoint(mid))
                            .default as EditorWidgetRegister;
                        const { widgetStore } = registerEditorWidget(
                            key,
                            widgetResource
                        );
                        store.addExtensionStore(key, widgetStore);
                    } catch (er) {
                        console.error(er);
                    }
                }
            };

            const { widgetStore } = registerEditorWidget(
                "attributes",
                editorWidgetRegister
            );
            store.attachAttributeStore(widgetStore);

            loadWidgets();
        }, [store, registerEditorWidget]);

        return (
            <div className="ngw-feature-layer-editor">
                <Tabs type="card" items={items} parentHeight />
                <ActionToolbar
                    actions={[
                        <SaveButton
                            key="save"
                            loading={store.saving}
                            onClick={store.save}
                        >
                            {saveText}
                        </SaveButton>,
                    ]}
                />
            </div>
        );
    }
);
