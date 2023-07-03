import { useEffect, useLayoutEffect, useRef, useState } from "react";

import DatePicker from "@nextgisweb/gui/antd/date-picker";
import { route } from "@nextgisweb/pyramid/api";

import "./Journal.less";

const { RangePicker } = DatePicker;

const Block = ({ head, tail, onGrow }) => {
    const [data, setData] = useState([]);
    const ref = useRef(null);

    useEffect(() => {
        if (tail) return;

        route("audit.query")
            .get({
                query: { after: head, limit: 10 },
            })
            .then((data) => {
                const tail = data[data.length - 1].tstamp;
                setData(data);
                onGrow(tail);
            });
    }, []);

    // console.log(head);

    return (
        <tbody ref={ref}>
            {data.map((v, idx) => (
                <tr key={idx}>
                    <td>{v.tstamp}</td>
                    <td>{v.user_id}</td>
                </tr>
            ))}
        </tbody>
    );
};

export function Journal() {
    const [blocks, setBlocks] = useState([{ head: "" }]);
    const [growFrom, setGrowFrom] = useState(null);

    const refParent = useRef(null);
    const refTable = useRef(null);

    const doGrow = (force = false) => {
        console.log(growFrom);
        if (
            force ||
            (growFrom &&
                refTable.current.clientHeight < refParent.current.clientHeight)
        ) {
            setBlocks((cur) => {
                const next = [...cur];
                const last = next.pop();
                last.tail = growFrom;
                next.push(last);
                next.push({ head: growFrom });
                return next;
            });
        }
    };

    useLayoutEffect(() => {
        doGrow();
        console.log(
            refParent.current.clientHeight,
            refTable.current.clientHeight,
            growFrom
        );
    }, [growFrom]);

    const onGrow = (tail) => {
        setGrowFrom(tail);
    };

    const onScrol = () => {
        const el = refParent.current;
        if (el.scrollTop + el.clientHeight > el.scrollHeight - 100) {
            doGrow(true);
        }
    };

    return (
        <div className="ngw-audit-journal">
            <div className="head">
                <RangePicker />
            </div>
            <div className="table" ref={refParent} onScroll={onScrol}>
                <table ref={refTable}>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>User</th>
                            <th>Method</th>
                            <th>Path</th>
                        </tr>
                    </thead>
                    {blocks.map((b, idx) => (
                        <Block key={idx} {...{ onGrow, ...b }} />
                    ))}
                </table>
            </div>
        </div>
    );
}
