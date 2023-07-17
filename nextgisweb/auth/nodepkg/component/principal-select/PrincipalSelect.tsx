import { useEffect, useState, useMemo } from "react";

import { route, routeURL } from "@nextgisweb/pyramid/api";
import { useAbortController } from "@nextgisweb/pyramid/hook/useAbortController";
import { Select, Tag, Space } from "@nextgisweb/gui/antd";

import AdministratorIcon from "@material-icons/svg/local_police";
import RegularUserIcon from "@material-icons/svg/person";
import SystemUserIcon from "@material-icons/svg/attribution";
import GroupIcon from "@material-icons/svg/groups";

import type { PrincipalSelectProps, Member, SelectProps } from "./type";

type TagProps = Parameters<SelectProps["tagRender"]>[0];

export function PrincipalSelect({
    editOnClick,
    systemUsers,
    multiple = false,
    onChange,
    model = "principal",
    value,
    ...restSelectProps
}: PrincipalSelectProps) {
    const [members, setMembers] = useState<Member[]>([]);
    const { makeSignal } = useAbortController();

    const memberById = (memberId: number) =>
        members.find((itm) => itm.id === memberId);

    const editUrl = (member: Member) => {
        if (member) {
            const memberId = member.id;
            if (member._user) {
                return routeURL("auth.user.edit", memberId);
            }
            return routeURL("auth.group.edit", memberId);
        }
    };

    const getIcon = (member: Member) => {
        if (member._user) {
            if (member.is_administrator) {
                return <AdministratorIcon />;
            } else if (member.system) {
                return <SystemUserIcon />;
            }
            return <RegularUserIcon />;
        } else {
            return <GroupIcon />;
        }
    };

    const optionRender = ({
        label,
        value,
    }: {
        label: string;
        value: number;
    }) => {
        return (
            <Space>
                {getIcon(memberById(value))}
                {label}
            </Space>
        );
    };

    const tagRender = (tagProps: TagProps) => {
        const { label, closable, onClose, value } = tagProps;
        const member = memberById(value);
        return (
            <Tag
                onMouseDown={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                }}
                closable={closable}
                onClose={onClose}
                style={{ marginRight: 3 }}
            >
                {editOnClick ? (
                    <a
                        href={editUrl(member)}
                        style={{ textDecoration: "none" }}
                        target="_blank"
                        rel="noreferrer"
                    >
                        {label}
                    </a>
                ) : (
                    <span>{label}</span>
                )}
            </Tag>
        );
    };

    useEffect(() => {
        const loadData = () => {
            const promises: Promise<Member[]>[] = [];
            const loadUsers = model === "principal" || model === "user";
            const loadGroups = model === "principal" || model === "group";
            if (loadUsers) {
                promises.push(
                    route("auth.user.collection")
                        .get({
                            query: { brief: true },
                            signal: makeSignal(),
                            cache: true,
                        })
                        .then((data) => {
                            return data
                                .filter((itm) => {
                                    if (itm.system) {
                                        if (Array.isArray(systemUsers)) {
                                            return systemUsers.includes(
                                                itm.keyname,
                                            );
                                        }
                                        return !!systemUsers;
                                    }
                                    return true;
                                })
                                .map((data) => ({ ...data, _user: true }));
                        }),
                );
            }
            if (loadGroups) {
                promises.push(
                    route("auth.group.collection").get({
                        query: { brief: true },
                        signal: makeSignal(),
                        cache: true,
                    }),
                );
            }
            return Promise.all(promises).then((members_) =>
                members_.flat().sort((a, b) => {
                    if (a.system !== b.system) {
                        return a.system ? -1 : 1;
                    }
                    return a.display_name > b.display_name ? 1 : -1;
                }),
            );
        };
        loadData().then((choices_) => {
            setMembers(choices_);
        });
    }, [model, makeSignal, systemUsers]);

    const options = useMemo(() => {
        return members
            ? members.map(({ display_name, id }) => {
                  return {
                      label: display_name,
                      value: id,
                  };
              })
            : [];
    }, [members]);

    return (
        <Select
            showSearch
            style={{ width: "100%" }}
            value={value}
            onChange={onChange}
            mode={multiple ? "multiple" : undefined}
            optionFilterProp="label"
            loading={!members}
            allowClear
            tagRender={tagRender}
            {...restSelectProps}
        >
            {options.map(({ label, value }) => {
                return (
                    <Select.Option key={value} value={value} label={label}>
                        {typeof optionRender === "function"
                            ? optionRender({ label, value })
                            : label}
                    </Select.Option>
                );
            })}
        </Select>
    );
}
