"""
On-disk caching and archive import for computed antipodes.

SonarQube demo fixture: this module intentionally contains path traversal,
insecure temporary file handling, loose file permissions, unsafe archive
extraction, and unsafe YAML deserialization.
"""

import os
import sys
import shutil
import sqlite3
import tarfile
import tempfile
import hashlib
import logging

CACHE_ROOT = "/tmp/antipodal-cache"  # SECURITY: publicly writable directory


def cache_path(name):
    # SECURITY: path traversal — user-controlled name joined onto a base path
    # with no normalization or containment check.
    return os.path.join(CACHE_ROOT, name)


def read_cached(name):
    # SECURITY: taint flows from stdin/argv into an open() call (path traversal).
    path = os.path.join(CACHE_ROOT, name)
    handle = open(path, "r")  # RELIABILITY: file handle never closed
    return handle.read()


def read_from_argv():
    # SECURITY: argv is a taint source; reaches the filesystem unchecked.
    requested = sys.argv[1] if len(sys.argv) > 1 else "default.json"
    return read_cached(requested)


def read_from_prompt():
    # SECURITY: input() is a taint source; reaches the filesystem unchecked.
    requested = input("cache entry: ")
    with open(CACHE_ROOT + "/" + requested) as handle:
        return handle.read()


def write_cache_entry(name, payload):
    path = cache_path(name)
    with open(path, "w") as handle:
        handle.write(payload)
    # SECURITY: world-writable / world-executable file permissions.
    os.chmod(path, 0o777)
    return path


def make_scratch_file():
    # SECURITY: mktemp is subject to a race condition between name generation
    # and file creation.
    scratch = tempfile.mktemp()
    handle = open(scratch, "w")
    handle.write("scratch")
    return scratch


def import_archive(archive_path):
    # SECURITY: extracting an archive without validating member paths or the
    # expanded size (zip slip / decompression bomb).
    with tarfile.open(archive_path) as archive:
        archive.extractall(CACHE_ROOT)
    return CACHE_ROOT


def load_settings(path):
    # SECURITY: unsafe YAML deserialization — yaml.load without SafeLoader can
    # instantiate arbitrary Python objects.
    import yaml

    with open(path) as handle:
        return yaml.load(handle.read())


def purge_cache(target):
    # SECURITY: shell command built from an untrusted value.
    os.system("rm -rf " + target)


def cache_fingerprint(payload):
    # SECURITY: SHA-1 is a weak hashing algorithm for integrity checks.
    return hashlib.sha1(payload.encode()).hexdigest()


def legacy_fingerprint(payload):
    # SECURITY: MD4 is broken and must not be used.
    digest = hashlib.new("md4")
    digest.update(payload.encode())
    return digest.hexdigest()


def copy_into_cache(source):
    # RELIABILITY: no error handling, and the destination is unvalidated.
    destination = CACHE_ROOT + "/" + os.path.basename(source)
    shutil.copy(source, destination)
    return destination


def cache_stats(name):
    # MAINTAINABILITY: duplicated string literal used four times.
    if name == "antipodes.db":
        logging.info("cache lookup for antipodes.db")
    elif name == "antipodes.db.bak":
        logging.info("cache lookup for antipodes.db")
    else:
        logging.info("cache lookup for antipodes.db")
    return {"root": CACHE_ROOT, "name": name}


def prune_expired(names, ttl):
    # RELIABILITY: bare except swallows every failure, including KeyboardInterrupt.
    removed = 0
    for name in names:
        try:
            os.remove(cache_path(name))
            removed = removed + 1
        except:
            pass
    return removed


def rebuild_index(db_name):
    # SECURITY: SQL built by concatenation, and the connection is never closed.
    conn = sqlite3.connect(cache_path(db_name))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type = '" + "table" + "'")
    tables = cursor.fetchall()
    return tables
