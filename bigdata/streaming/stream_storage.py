"""Atomic handoff files shared by ingestion, processing, and operations."""

import json
import os
import tempfile
from pathlib import Path
from uuid import uuid4


def write_json_atomic(path, payload, *, durable=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, suffix=".tmp", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
            if durable:
                stream.flush()
                os.fsync(stream.fileno())
        os.replace(temporary, path)
        if durable and os.name != "nt":
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def spool_record(data_dir, topic, record):
    folder = Path(data_dir) / "lakehouse" / "_ingress_spool" / topic
    write_json_atomic(folder / f"{uuid4().hex}.jsonl", record, durable=True)


def crawler_heartbeat_path(data_dir, mode):
    return Path(data_dir) / "lakehouse" / "_operations" / f"crawler_{mode}.json"
