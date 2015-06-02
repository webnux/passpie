from functools import wraps
import logging

from git import Repo
from git.exc import InvalidGitRepositoryError

from ._compat import which
from .utils import reverse_enumerate


def ensure_git(return_value=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if which('git'):
                try:
                    return func(*args, **kwargs)
                except InvalidGitRepositoryError as e:
                    logging.debug('"{}" is not a git repository'.format(e))
                except Exception as e:
                    logging.debug(str(e))
            else:
                logging.debug('git is not installed')
            return return_value
        return wrapper
    return decorator


class Git(object):

    def __init__(self, path):
        self.path = path

    @ensure_git()
    def init(self, message='Initialized database'):
        repo = Repo.init(self.path)
        repo.git.add(all=True)
        repo.index.commit(message)

    @ensure_git()
    def commit(self, message):
        repo = Repo(self.path)
        repo.git.add(all=True)
        repo.index.commit(message)

    @ensure_git(return_value=[])
    def commit_list(self):
        repo = Repo(self.path)
        return reverse_enumerate(list(repo.iter_commits()))

    @ensure_git()
    def commit_by_index(self, index):
        for number, commit in self.commit_list():
            if index == number:
                return commit

    @ensure_git()
    def reset(self, index):
        repo = Repo(self.path)
        commit = self.commit_by_index(index)
        if commit:
            repo.git.reset('--hard', commit.hexsha)