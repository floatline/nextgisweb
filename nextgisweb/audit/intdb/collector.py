from pathlib import Path
from time import sleep

from nextgisweb.lib.logging import logger

from .sink import SinkReader
from .storage import Storage


class SinkMonitor:

    def __init__(self, path: Path) -> None:
        self.path = path
        self.sinks = []

    def scan(self):
        for fn in self.path.glob('*'):
            self.sinks.append(SinkReader(fn))

    def sort_sinks(self):
        self.sinks.sort(key=lambda sr: sr.sort_key())



def collect(spath: Path, dbpath: Path):
    monitor = SinkMonitor(spath)
    storage = Storage(dbpath, read_only=False)
    monitor.scan()

    while True:
        monitor.sort_sinks()

        for sr in monitor.sinks:
            while head := sr.fetch_head():
                rec = sr.fetch_record(head)
                storage.push(rec)

        storage.flush()
        sleep(10)

