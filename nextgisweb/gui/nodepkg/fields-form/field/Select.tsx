import { Select as AntdSelect } from "@nextgisweb/gui/antd";

import { SelectProps as AntdSelectProps } from "antd/lib/select";

import { FormItem } from "./_FormItem";

import type { FormItemProps, FormFieldChoice } from "../type";

type InputProps = Parameters<typeof AntdSelect>[0];

type SelectProps = FormItemProps<AntdSelectProps> & {
    choices?: FormFieldChoice[];
    /** @deprecated move to inputProps */
    mode?: InputProps["mode"];
};

export function Select({ choices, mode, ...props }: SelectProps) {
    return (
        <FormItem
            {...props}
            input={(inputProps) => (
                <AntdSelect {...{ mode, ...inputProps }}>
                    {choices.map(({ label, value, ...optionProps }) => (
                        <AntdSelect.Option
                            key={value}
                            value={value}
                            {...optionProps}
                        >
                            {label}
                        </AntdSelect.Option>
                    ))}
                </AntdSelect>
            )}
        />
    );
}
