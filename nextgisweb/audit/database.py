# from pathlib import Path
# from time import monotonic, sleep
# from datetime import datetime

# import transaction
# from sortedcontainers import SortedListWithKey

# from nextgisweb.env import DBSession, inject
# from nextgisweb.lib.logging import logger

# from .component import AuditComponent
# from .intdb.sink import SinkReader
from .model import tab_log
from sqlalchemy.engine import create_engine
from nextgisweb.lib import json
# class SinkMonitor:

#     def __init__(self, path: Path) -> None:
#         self.path = path
#         self.sinks = []

#     def scan(self):
#         for fn in self.path.glob('*'):
#             self.sinks.append(SinkReader(fn))

#     def sort_sinks(self):
#         self.sinks.sort(key=lambda sr: sr.sort_key())


# class Writer:
#     BATCH_SIZE = 2
#     FLUSH_INTERVAL = 15

#     def __init__(self):
#         self.buffer = SortedListWithKey(key=lambda rec: rec.head.pos)
#         self.position = dict()

#     def push(self, record):
#         self.buffer.add(record)
#         self.position[record.head.sid] = record.head.pos
#         if len(self.buffer) >= self.BATCH_SIZE:
#             self.flush(force=True)

#     def flush(self, *, force=False):
#         if len(self.buffer) == 0 and len(self.position) == 0:
#             return

#         if not force and (monotonic() - self.last_flush) < self.FLUSH_INTERVAL:
#             return

#         with transaction.manager:
#             # con = DBSession.connection()
#             # con.execute("SELECT 1")
            
#             for w in self.buffer:
#                 DBSession.execute(tab_log.insert().values(tstamp=datetime.utcnow(), user_id=0))
#             # logger.critical("123")
#             # try:
#             #     # con.begin()
#             #     # con.executemany(
#             #     #     "INSERT INTO request (tstamp, data) VALUES (?, ?)",
#             #     #     ((r.head.tstamp, r.data) for r in self.buffer))
#             #     # updated = datetime.utcnow().isoformat()
#             #     # con.executemany(
#             #     #     "INSERT OR REPLACE INTO sink VALUES (?, ?, ?, NULL)",
#             #     #     ((k, v, updated) for k, v in self.position.items()))
#             # except:
#             #     # con.rollback()
#             #     raise
#             # finally:
#             #     con.commit()

#         self.buffer.clear()
#         self.position = dict()
#         self.last_flush = monotonic()

#         # print(con.sql('SELECT * FROM sink'))

# @inject()
# def collect(*, comp: AuditComponent):
#     monitor = SinkMonitor(comp.intdb_sink_path)
#     storage = Writer()
#     monitor.scan()

#     while True:
#         monitor.sort_sinks()

#         for sr in monitor.sinks:
#             while head := sr.fetch_head():
#                 rec = sr.fetch_record(head)
#                 storage.push(rec)

#         storage.flush()
#         sleep(10)




class DatabaseMixin:
    database_enabled: bool

    def initialize(self):
        super().initialize()
        options = self.options.with_prefix('database')
        self.database_enabled = options['enabled']
        
        engine_url = self.env.core._engine_url()
        self.database_engine = create_engine(
            engine_url, 
            json_serializer=json.dumps,
            json_deserializer=json.loads,
            isolation_level='AUTOCOMMIT',
            pool_pre_ping=True,
        )
