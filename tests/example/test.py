from unittest.mock import MagicMock, patch

from git import Repo
from git.cmd import Git

original_call_process = Git._call_process


def custom_side_effect(self, command, *args, **kwargs):
    if command == "diff":
        return "mocked diff output"
    # fallback to the real behavior for all other commands
    return original_call_process(self, command, *args, **kwargs)


repo = Repo("C:/Users/longlp/Downloads/build-commands/chromium_patcher")
with patch.object(Git, "_call_process", new=custom_side_effect):
    print(repo.git.diff())  # -> mocked diff output
    print(repo.git.status())  # -> real status output from git
