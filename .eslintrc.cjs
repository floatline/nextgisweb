const babelConfigPath = require.resolve("@nextgisweb/jsrealm/babelrc.cjs");

module.exports = {
    root: true,
    plugins: ["requirejs", "react"],
    extends: [
        "eslint:recommended",
        "plugin:requirejs/recommended",
        "plugin:react/recommended",
        "plugin:react/jsx-runtime",
        "plugin:react-hooks/recommended",
    ],
    globals: {
        dojoConfig: "readonly",
        ngwConfig: "readonly",
    },
    rules: {
        indent: ["error", 4, { SwitchCase: 1 }],
        eqeqeq: "error",
        "no-unused-vars": ["error", { args: "after-used" }],
        "no-use-before-define": "error",
        "requirejs/no-object-define": "error",
        "requirejs/one-dependency-per-line": ["error"],
        "requirejs/amd-function-arity": [
            "error",
            { allowExtraDependencies: true },
        ],
    },
    ignorePatterns: ["doc/"],
    overrides: [
        {
            files: "*.cjs",
            env: {
                node: true,
                es2020: true,
            },
        },
        {
            files: "*.js",
            env: {
                browser: true,
            },
        },
        {
            files: ["*/*/nodepkg/**/*.js"],
            env: {
                browser: true,
                es2020: true,
            },
            parser: "@babel/eslint-parser",
            parserOptions: {
                sourceType: "module",
                jsx: true,
                babelOptions: {
                    configFile: babelConfigPath,
                },
            },
        },
        {
            files: ["*/*/nodepkg/**/*.ts", "*/*/nodepkg/**/*.tsx"],
            parser: "@typescript-eslint/parser",
            plugins: ["react", "@typescript-eslint", "prettier"],
            extends: [
                "eslint:recommended",
                "plugin:@typescript-eslint/recommended",
                "plugin:react/recommended",
                "plugin:react/jsx-runtime",
                "plugin:react-hooks/recommended",
                "plugin:prettier/recommended",
            ],
            parserOptions: {
                sourceType: "module",
                jsx: true,
                babelOptions: {
                    configFile: babelConfigPath,
                },
            },
            rules: {
                "prettier/prettier": [
                    "error",
                    {
                        tabWidth: 4,
                        parser: "babel-ts",
                    },
                ],
            },
        },
        {
            files: ["*/*/amd/**/*.js"],
            plugins: ["requirejs"],
            extends: ["eslint:recommended", "plugin:requirejs/recommended"],
            env: {
                browser: true,
                amd: true,
                es2015: true,
            },
            rules: {
                eqeqeq: "off",
            },
        },
    ],
    settings: {
        react: {
            version: "17",
        },
    },
};
