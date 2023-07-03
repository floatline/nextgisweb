from datetime import datetime
from pathlib import Path
from time import monotonic

from sortedcontainers import SortedListWithKey

from nextgisweb.lib.logging import logger


class Storage:
    BATCH_SIZE = 1000
    FLUSH_INTERVAL = 10

    def __init__(self, path: Path, read_only: bool = True) -> None:
        self.con = duckdb.connect(str(path), read_only=read_only)
        if not read_only:
            self.con.sql("""
            CREATE TABLE IF NOT EXISTS request (
                tstamp LONG NOT NULL,
                data JSON NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sink (
                id VARCHAR PRIMARY KEY,
                position LONG NOT NULL,
                updated TIMESTAMP NOT NULL,
                deleted TIMESTAMP
            )""")

        self.buffer = SortedListWithKey(key=lambda rec: rec.head.pos)
        self.position = dict()
        self.last_flush = 0

    def push(self, record):
        self.buffer.add(record)
        self.position[record.head.sid] = record.head.pos
        if len(self.buffer) >= self.BATCH_SIZE:
            self.flush(force=True)

    def flush(self, *, force=False):
        if len(self.buffer) == 0 and len(self.position) == 0:
            return

        if not force and (monotonic() - self.last_flush) < self.FLUSH_INTERVAL:
            return

        con = self.con
        try:
            con.begin()
            con.executemany(
                "INSERT INTO request (tstamp, data) VALUES (?, ?)",
                ((r.head.tstamp, r.data) for r in self.buffer))
            updated = datetime.utcnow().isoformat()
            con.executemany(
                "INSERT OR REPLACE INTO sink VALUES (?, ?, ?, NULL)",
                ((k, v, updated) for k, v in self.position.items()))
        except:
            con.rollback()
            raise
        finally:
            con.commit()

            self.buffer.clear()
            self.position = dict()
            self.last_flush = monotonic()

        print(con.sql('SELECT * FROM sink'))

    def fetch(
        self, *,
        tstamp_from: datetime = None,
        tstamp_to: datetime = None,
        user_id: int = None,
        limit: int = 50,
    ):
        where = ['TRUE']
        params = []

        if tstamp_from:
            where.append('tstamp >= ?')
            params.append(tstamp_from.isoformat())
        
        if tstamp_to:
            where.append('tstamp < ?')
            params.append(tstamp_to.isoformat())

        params.append(limit)
        for row in self.con.execute(
            f"SELECT * FROM request WHERE {' AND '.join(where)} LIMIT ?",
            params,
        ):
            logger.critical(row)