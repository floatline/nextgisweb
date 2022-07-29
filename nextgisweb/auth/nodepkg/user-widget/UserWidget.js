import { Alert } from "@nextgisweb/gui/antd";
import { ContentBox, LoadingWrapper } from "@nextgisweb/gui/component";
import { KeynameTextBox, LanguageSelect } from "@nextgisweb/gui/fields-form";
import { ModelForm } from "@nextgisweb/gui/model-form";
import { useRouteGet } from "@nextgisweb/pyramid/hook/useRouteGet";
import { route } from "@nextgisweb/pyramid/api";
import i18n from "@nextgisweb/pyramid/i18n!auth";
import { PropTypes } from "prop-types";
import { useMemo } from "react";
import { PrincipalMemberSelect } from "../field";
import { default as oauth, makeTeamManageButton } from "../oauth";
import getMessages from "../userMessages";

export function UserWidget({ id }) {
    const { data: group, isLoading } = useRouteGet({
        name: "auth.group.collection",
    });

    const fields = useMemo(() => {
        const fields_ = [];

        fields_.push(
            ...[
                {
                    name: "display_name",
                    label: i18n.gettext("Full name"),
                    required: true,
                },
                {
                    name: "keyname",
                    label: i18n.gettext("Login"),
                    required: true,
                    widget: KeynameTextBox,
                },
                {
                    name: "password",
                    label: i18n.gettext("Password"),
                    widget: "password",
                    autoComplete: 'new-password',
                    // required only when creating a new user
                    required: id === undefined,
                    placeholder:
                        id !== undefined
                            ? i18n.gettext("Enter new password here")
                            : "",
                },
            ]
        );

        if (oauth.enabled && id) {
            fields_.push({
                name: "oauth_subject",
                label: oauth.name,
                disabled: true,
            });
        }

        fields_.push(
            ...[
                {
                    name: "disabled",
                    label: i18n.gettext("Disabled"),
                    widget: "checkbox",
                },
                {
                    name: "member_of",
                    label: i18n.gettext("Groups"),
                    widget: PrincipalMemberSelect,
                    choices: group || [],
                    value:
                        group && id === undefined
                            ? group
                                .filter((g) => g.register)
                                .map((g) => g.id)
                            : [],
                },
                {
                    name: "language",
                    label: i18n.gettext("Language"),
                    widget: LanguageSelect,
                    value: 'default',
                },
                {
                    name: "description",
                    label: i18n.gettext("Description"),
                    widget: "textarea",
                },
            ]
        );

        return fields_;
    }, [group]);

    const p = { fields, model: "auth.user", id, messages: getMessages() };

    // prettier-ignore
    const infoNGID = useMemo(() => oauth.isNGID && !id && <Alert
        type="info" style={{marginBottom: "1ex"}}
        message={i18n.gettext("Consider adding {name} user to your team instead of creating a new user with a password.").replace("{name}", oauth.name)}
        action={makeTeamManageButton()}
    />, []);

    if (isLoading) {
        return <LoadingWrapper></LoadingWrapper>;
    }

    return (
        <div className="ngw-auth-user-widget">
            {infoNGID}
            <ContentBox>
                <ModelForm {...p}></ModelForm>
            </ContentBox>
        </div>
    );
}

UserWidget.propTypes = {
    id: PropTypes.number,
};
