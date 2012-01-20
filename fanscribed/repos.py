import json
import os
import random
import string
import threading
import time

import git

from pyramid.threadlocal import get_current_registry


# Ten minute lock timeout.
LOCK_TIMEOUT = 10 * 60


commit_lock = threading.Lock()


def _lock_is_expired(timestamp):
    return (timestamp + LOCK_TIMEOUT) < time.time()


def _lock_secret():
    return ''.join(random.choice(string.letters) for x in xrange(16))


def _settings():
    return get_current_registry().settings


def _snippet_ms():
    snippet_seconds = int(_settings()['fanscribed.snippet_seconds'])
    return snippet_seconds * 1000


def repo_from_request(request):
    repos_path = _settings()['fanscribed.repos']
    repo_path = os.path.join(repos_path, request.host)
    # Make sure repo path is underneath outer repos path.
    assert '..' not in os.path.relpath(repo_path, repos_path)
    return git.Repo(repo_path)


def duration(tree):
    blob = tree['transcription.json']
    transcription_info = json.load(blob.data_stream)
    return transcription_info['duration']


def get_locks(tree):
    if 'locks.json' in tree:
        blob = tree['locks.json']
        return json.load(blob.data_stream)
    else:
        return {}


def save_locks(repo, index, locks):
    filename = os.path.join(repo.working_dir, 'locks.json')
    with open(filename, 'wb') as f:
        json.dump(locks, f, indent=4)
    index.add(['locks.json'])


def get_remaining_snippets(tree):
    blob = tree['remaining_snippets.json']
    return json.load(blob.data_stream)


def save_remaining_snippets(repo, index, snippets):
    filename = os.path.join(repo.working_dir, 'remaining_snippets.json')
    with open(filename, 'wb') as f:
        json.dump(snippets, f, indent=4)
    index.add(['remaining_snippets.json'])


def remove_snippet_from_remaining(repo, index, starting_point):
    tree = repo.tree('master')
    snippets = get_remaining_snippets(tree)
    while starting_point in snippets:
        snippets.remove(starting_point)
    save_remaining_snippets(repo, index, snippets)


def get_remaining_reviews(tree):
    blob = tree['remaining_reviews.json']
    return json.load(blob.data_stream)


def save_remaining_reviews(repo, index, reviews):
    filename = os.path.join(repo.working_dir, 'remaining_reviews.json')
    with open(filename, 'wb') as f:
        json.dump(reviews, f, indent=4)
    index.add(['remaining_reviews.json'])


def remove_review_from_remaining(repo, index, starting_point):
    tree = repo.tree('master')
    reviews = get_remaining_reviews(tree)
    while starting_point in reviews:
        reviews.remove(starting_point)
    save_remaining_reviews(repo, index, reviews)


def lock_available_snippet(repo, index):
    """Return a (starting_point, lock_secret) tuple of a newly-locked snippet,
    or (None, message) if there are none remaining or all are locked."""
    tree = repo.tree('master')
    remaining = set(get_remaining_snippets(tree))
    if len(remaining) == 0:
        # All of them have been transcribed.
        return (None, 'All snippets have been completed.')
    # Remove expired locks.
    lock_structure = get_locks(tree)
    locks = lock_structure.setdefault('snippet', {})
    for lock_name, lock in locks.items():
        lock_timestamp = lock['timestamp']
        if _lock_is_expired(lock_timestamp):
            del locks[lock_name]
    # Find one that's unlocked, if there are any.
    locked = set(int(lock_name) for lock_name in locks)
    unlocked = remaining - locked
    if len(unlocked) == 0:
        # All remaining have valid locks.
        return (None, 'All snippets are locked; try again later.')
    else:
        # Pick the next one and lock it with a secret.
        starting_point = sorted(unlocked)[0]
        lock_secret = _lock_secret()
        locks[str(starting_point)] = {
            'secret': lock_secret,
            'timestamp': time.time(),
        }
        save_locks(repo, index, lock_structure)
        return (starting_point, lock_secret)


def lock_available_review(repo, index):
    """Return a (starting_point, lock_secret) tuple of a newly-locked review,
    or (None, message) if there are none remaining or all are locked."""
    tree = repo.tree('master')
    remaining = set(get_remaining_reviews(tree))
    if len(remaining) == 0:
        # All of them have been reviewed.
        return (None, 'All reviews have been completed.')
    # Remove expired locks.
    lock_structure = get_locks(tree)
    locks = lock_structure.setdefault('review', {})
    for lock_name, lock in locks.items():
        lock_timestamp = lock['timestamp']
        if _lock_is_expired(lock_timestamp):
            del locks[lock_name]
    # Find one that's unlocked, if there are any.
    locked = set(int(lock_name) for lock_name in locks)
    unlocked = remaining - locked
    # Discard all of the reviews where the snippets are still remaining.
    if len(unlocked) > 0:
        remaining_snippets = set(get_remaining_snippets(tree))
        unlocked -= remaining_snippets
    else:
        # All remaining have valid locks.
        return (None, 'All reviews are locked; try again later.')
    # Also discard any reviews where the second snippet of the review still remains.
    if len(unlocked) > 0:
        adjacent_empty = set()
        for starting_point in unlocked:
            candidate = starting_point + _snippet_ms()
            if candidate in remaining_snippets:
                adjacent_empty.add(candidate)
        unlocked -= adjacent_empty
    if len(unlocked) == 0:
        # All remaining have valid locks.
        return (None, 'Not enough snippets have been transcribed.')
    else:
        # Pick the first available one and lock it with a secret.
        starting_point = sorted(unlocked)[0]
        lock_secret = _lock_secret()
        locks[str(starting_point)] = {
            'secret': lock_secret,
            'timestamp': time.time(),
        }
        save_locks(repo, index, lock_structure)
        return (starting_point, lock_secret)


def lock_is_valid(repo, index, lock_type, starting_point, lock_secret):
    tree = repo.tree('master')
    lock_structure = get_locks(tree)
    locks = lock_structure.get(lock_type, {})
    lock_name = str(starting_point)
    if lock_name not in locks:
        return False
    lock_detail = locks[lock_name]
    return (lock_detail['secret'] == lock_secret)


def remove_lock(repo, index, lock_type, starting_point):
    tree = repo.tree('master')
    lock_structure = get_locks(tree)
    locks = lock_structure.get(lock_type, {})
    lock_name = str(starting_point)
    if lock_name in locks:
        del locks[lock_name]
        save_locks(repo, index, lock_structure)


def snippet_text(repo, index, starting_point):
    tree = repo.tree('master')
    filename = '{0:016d}.txt'.format(starting_point)
    if filename in tree:
        blob = tree[filename]
        return blob.data_stream.read()
    else:
        # new snippet
        return ''


def save_snippet_text(repo, index, starting_point, text):
    filename = os.path.join(
        repo.working_dir,
        '{0:016d}.txt'.format(starting_point),
    )
    with open(filename, 'wb') as f:
        f.write(text)
    index.add([filename])
