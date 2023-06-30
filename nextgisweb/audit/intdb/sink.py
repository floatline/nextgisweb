import io
from datetime import datetime
from pathlib import Path
from struct import calcsize, pack, unpack
from typing import NamedTuple

MAGIC = "NGW1DUCK".encode('ascii')

HEAD_STRUCT = 'QI'
HEAD_SIZE = calcsize(HEAD_STRUCT)
MAX_TIMESTAMP = int(datetime(2100, 1, 1).timestamp() * 1000)


class Sink:

    def __init__(self, path: Path) -> None:
        self.path = path
        self.ckey = None
        self.cfile = None

    def write(self, tstamp: datetime, data: str):
        self.file(tstamp).write(tstamp, data.encode('utf-8'))

    def file(self, tstamp: datetime):
        ckey = tstamp.strftime('%Y%m%d')

        if self.ckey != ckey:
            if self.cfile is not None:
                self.cfile.close()

            fn = self.path / ckey
            self.cfile = SinkWriter(fn)
            self.ckey = ckey

        return self.cfile

    def sink(self):
        pass


class Head(NamedTuple):
    sid: str
    pos: int
    tstamp: int
    length: int


class Record(NamedTuple):
    head: Head
    data: bytes


class SinkWriter:

    def __init__(self, path: Path) -> None:
        if path.exists():
            with io.open(path, mode='rb') as fd:
                assert fd.read(len(MAGIC)) == MAGIC
        else:
            with io.open(path, mode='wb') as fd:
                fd.write(MAGIC)

        self.fd = io.open(path, mode='ab', buffering=0)

    def write(self, tstamp: datetime, data: bytes) -> None:
        head = pack(HEAD_STRUCT, int(tstamp.timestamp()), len(data))
        self.fd.write(head + data)


class SinkReader:

    def __init__(self, path: Path, seek: int = 0) -> None:
        self.fd = io.open(path, mode='rb', buffering=0)
        self.sid = path.name
        magic = self.fd.read(len(MAGIC))
        assert magic == MAGIC, f'{magic} != {MAGIC}'

        if seek != 0:
            self.fd.seek(seek)
            self.head_pos = seek
        else:
            self.head_pos = len(MAGIC)

        self.buf = bytes()
        self.head = None

    def fetch_head(self):
        if res := self.head:
            return res

        if res := self.read_head():
            self.head = res
            return res

    def fetch_record(self, head: Head):
        assert self.head_pos == head.pos
        data = self.read_bytes(head.length)
        assert data is not None
        self.head_pos += HEAD_SIZE + len(data)
        self.head = None
        return Record(head, data)

    def sort_key(self):
        if head := self.fetch_head():
            return head.tstamp
        return MAX_TIMESTAMP

    def read_bytes(self, size):
        to_read = size - len(self.buf)

        if to_read > 0:
            b = self.fd.read(to_read)
            self.buf = self.buf + b

        to_read = size - len(self.buf)
        if to_read > 0:
            return None

        res = self.buf[:size]
        self.buf = self.buf[size:]
        return res

    def read_head(self):
        if b := self.read_bytes(HEAD_SIZE):
            return Head(self.sid, self.head_pos, *unpack(HEAD_STRUCT, b))
