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


def _settings():
    return get_current_registry().settings


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


def lock_random(repo, index, lock_type):
    """Return a (starting_point, lock_secret) tuple of a newly-locked snippet,
    or (None, message) if there are none remaining or all are locked."""
    tree = repo.tree('master')
    if lock_type == 'snippet':
        remaining = get_remaining_snippets(tree)
    elif lock_type == 'review':
        remaining = get_remaining_reviews(tree)
    remaining = set(remaining)
    if len(remaining) == 0:
        # All of them have been transcribed.
        return (None, 'All {0}s have been completed.'.format(lock_type))
    # Remove expired locks.
    lock_structure = get_locks(tree)
    locks = lock_structure.setdefault(lock_type, {})
    for lock_name, lock in locks.items():
        lock_timestamp = lock['timestamp']
        if _lock_is_expired(lock_timestamp):
            del locks[lock_name]
    # Find one that's unlocked, if there are any.
    locked = set(int(lock_name) for lock_name in locks)
    unlocked = sorted(remaining - locked)
    if len(unlocked) == 0:
        # All remaining have valid locks.
        return (None, 'All {0}s are locked; try again later.'.format(lock_type))
    else:
        # Pick a random one and lock it with a secret.
        starting_point = random.choice(unlocked)
        lock_secret = ''.join(random.choice(string.letters) for x in xrange(16))
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
