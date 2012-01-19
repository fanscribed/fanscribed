import os

import git

from pyramid.threadlocal import get_current_registry


def repo_from_request(request):
    registry = get_current_registry()
    settings = registry.settings
    repos_path = settings['repos']
    repo_path = os.path.join(repos_path, request.host)
    # Make sure repo path is underneath outer repos path.
    assert '..' not in os.path.relpath(repo_path, repos_path)
    return git.Repo(repo_path)
