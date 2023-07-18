import { observer } from "mobx-react-lite";
import { useState, useRef, useEffect, useMemo } from "react";

import ArrowBack from "@material-icons/svg/arrow_back";
import CreateNewFolder from "@material-icons/svg/create_new_folder";
import DoneIcon from "@material-icons/svg/done";
import HighlightOff from "@material-icons/svg/highlight_off";

import { Button, Col, Input, Row, Space, Tooltip } from "@nextgisweb/gui/antd";
import { errorModal } from "@nextgisweb/gui/error";
import { useKeydownListener } from "@nextgisweb/gui/hook";

import usePickerCard from "./hook/usePickerCard";
import locale from "./locale";

import type { ResourcePickerStore } from "./store/ResourcePickerStore";
import type { ResourcePickerFooterProps } from "./type";

interface CreateControlProps {
    resourceStore: ResourcePickerStore;
    setCreateMode?: (val: boolean) => void;
}

interface MoveControlProps {
    resourceStore: ResourcePickerStore;
    setCreateMode?: (val: boolean) => void;
    onOk?: (val: number | number[]) => void;
}

const createNewGroupMsg = locale.createNewGroupText;
const clearSelectionMsg = locale.clearSelectionText;

const CreateControl = observer(
    ({ setCreateMode, resourceStore }: CreateControlProps) => {
        const { resourcesLoading } = resourceStore;
        const resourceNameInput = useRef(null);

        const [resourceName, setResourceName] = useState<string>();

        const onSave = async () => {
            try {
                if (resourceName) {
                    await resourceStore.createNewGroup(resourceName);
                    setCreateMode(false);
                }
            } catch (er) {
                errorModal(er);
            }
        };

        useKeydownListener("enter", () => {
            onSave();
        });

        useEffect(() => {
            const input = resourceNameInput.current;
            if (input) {
                input.focus();
            }
        }, []);

        return (
            <Input.Group>
                <Row>
                    <Col>
                        <Button
                            icon={<ArrowBack />}
                            onClick={() => setCreateMode(false)}
                        />
                    </Col>
                    <Col flex="auto">
                        <Input
                            value={resourceName}
                            onChange={(e) => {
                                setResourceName(e.target.value);
                            }}
                            ref={resourceNameInput}
                        />
                    </Col>
                    <Col>
                        <Button
                            type="primary"
                            icon={<DoneIcon />}
                            loading={resourcesLoading}
                            disabled={!resourceName}
                            onClick={onSave}
                        />
                    </Col>
                </Row>
            </Input.Group>
        );
    }
);

const MoveControl = observer(
    ({ setCreateMode, resourceStore, onOk }: MoveControlProps) => {
        const {
            selected,
            parentId,
            multiple,
            parentItem,
            getThisMsg,
            getSelectedMsg,
            getResourceClasses,
            disableResourceIds,
            allowCreateResource,
            createNewGroupLoading,
        } = resourceStore;

        const { getCheckboxProps } = usePickerCard({ resourceStore });

        const pickThisGroupAllowed = useMemo(() => {
            if (parentItem) {
                const { disabled } = getCheckboxProps(parentItem.resource);
                return !disabled;
            }
            return false;
        }, [getCheckboxProps, parentItem]);

        const possibleToCreate = useMemo(() => {
            if (parentItem) {
                return getResourceClasses([parentItem.resource.cls]).includes(
                    "resource_group"
                );
            }
            return false;
        }, [getResourceClasses, parentItem]);

        const onCreateClick = () => {
            resourceStore.clearSelection();
            setCreateMode(true);
        };

        // eslint-disable-next-line react/prop-types
        const OkBtn = ({ disabled }: { disabled?: boolean }) => {
            return (
                <Button
                    type="primary"
                    disabled={disabled ?? !selected.length}
                    onClick={() => onOk(multiple ? selected : selected[0])}
                >
                    {getSelectedMsg}
                </Button>
            );
        };

        return (
            <Row justify="space-between">
                <Col>
                    {allowCreateResource &&
                        possibleToCreate &&
                        !createNewGroupLoading && (
                            <Tooltip title={createNewGroupMsg}>
                                <a
                                    style={{ fontSize: "1.5rem" }}
                                    onClick={onCreateClick}
                                >
                                    <CreateNewFolder />
                                </a>
                            </Tooltip>
                        )}
                </Col>
                <Col>
                    {selected.length ? (
                        <Space>
                            <Tooltip title={clearSelectionMsg}>
                                <Button
                                    icon={<HighlightOff />}
                                    onClick={() => {
                                        resourceStore.clearSelection();
                                    }}
                                ></Button>
                            </Tooltip>
                            <OkBtn />
                        </Space>
                    ) : pickThisGroupAllowed ? (
                        <Button
                            type="primary"
                            onClick={() => onOk(parentId)}
                            disabled={disableResourceIds.includes(parentId)}
                        >
                            {getThisMsg}
                        </Button>
                    ) : (
                        <OkBtn disabled={true}></OkBtn>
                    )}
                </Col>
            </Row>
        );
    }
);

export const ResourcePickerFooter = observer(
    ({ resourceStore, onOk, ...props }: ResourcePickerFooterProps) => {
        const [createMode, setCreateMode] = useState(false);

        return (
            <>
                {createMode ? (
                    <CreateControl {...{ resourceStore, setCreateMode }} />
                ) : (
                    <MoveControl
                        {...{ resourceStore, setCreateMode, onOk, ...props }}
                    />
                )}
            </>
        );
    }
);
