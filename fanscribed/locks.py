"""Redis-based resource locking.

http://www.dr-josiah.com/2012/01/creating-lock-with-redis.html
"""

import contextlib
import time
import uuid

import redis.exceptions


class LockException(Exception):
    pass


def acquire_lock(conn, lockname, identifier, atime=10, ltime=10):
    end = time.time() + atime
    once = (atime == 0)  # Make sure we try at least once even if atime is 0.
    while end > time.time() or once:
        once = False
        if conn.setnx(lockname, identifier):
            conn.expire(lockname, ltime)
            return identifier
        elif not conn.ttl(lockname):
            conn.expire(lockname, ltime)
        time.sleep(.001)
    return False


def release_lock(conn, lockname, identifier):
    pipe = conn.pipeline(True)
    while True:
        try:
            pipe.watch(lockname)
            if pipe.get(lockname) == identifier:
                pipe.multi()
                pipe.delete(lockname)
                pipe.execute()
                return True
            pipe.unwatch()
            break
        except redis.exceptions.WatchError:
            pass
    # We lost the lock.
    return False


def acquire_model_lock(conn, instance, lockname, lockid_field):
    identifier = uuid.uuid4().hex
    lock = acquire_lock(conn, lockname, identifier, atime=0, ltime=10)
    if not lock:
        raise LockException('{lockname} already locked'.format(**locals()))
    else:
        setattr(instance, lockid_field, identifier)
        return lock


def release_model_lock(conn, instance, lockname, lockid_field):
    lockid = getattr(instance, lockid_field)
    released = release_lock(conn, lockname, lockid)
    setattr(instance, lockid_field, None)
    return released


@contextlib.contextmanager
def redis_lock(conn, lockname, atime=10, ltime=10):
    identifier = str(uuid.uuid4())
    if acquire_lock(**locals()) != identifier:
        raise LockException("could not acquire lock")
    try:
        yield identifier
    finally:
        if not release_lock(conn, lockname, identifier):
            raise LockException("lock was lost")
