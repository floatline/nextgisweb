export function sorterFactory<T>(attr: string): (a: T, b: T) => 0 | 1 | -1 {
    return (a, b) => {
        const va = a[attr];
        const vb = b[attr];

        if (va > vb) return 1;
        if (vb > va) return -1;
        return 0;
    };
}
