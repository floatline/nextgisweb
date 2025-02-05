/** @testentry call */
export default async function () {
    console.log("Loading './auxiliary/foo' with absolute path...");
    const foo = await import("@nextgisweb/pyramid/example/auxiliary/foo");
    console.log(foo);

    console.log("Loading '/auxiliary/bar' with relative path...");
    const bar = await import("./auxiliary/bar");
    console.log(bar);

    console.log("Loading './auxiliary/entrypoint' with relative path...");
    const entrypoint = await import("./auxiliary/entrypoint");
    console.log(entrypoint);

    return "Done";
}
