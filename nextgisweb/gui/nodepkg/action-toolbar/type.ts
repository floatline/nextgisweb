import type { SizeType } from "antd/lib/config-provider/SizeContext";
import type { Button } from "antd";
import type { CSSProperties } from "react";

export type ButtonProps = Parameters<typeof Button>[0];

export type ActionToolbarAction = string | JSX.Element;

type Props = Record<string, unknown>;

export interface ActionToolbarProps {
    size?: SizeType;
    style?: CSSProperties;
    actions: ActionToolbarAction[];
    rightActions?: ActionToolbarAction[];
    actionProps?: Props;
}

export interface UseActionToolbarProps {
    size?: SizeType;
    props?: Props;
}

export interface CreateButtonActionOptions
    extends Omit<ButtonProps, "icon" | "disabled"> {
    icon?: string | JSX.Element;
    action?: (val: Props) => void;
    disabled?: ((val: Props) => boolean) | boolean;
}
