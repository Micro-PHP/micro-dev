import git_shell, github


def test_create_or_update_branch_existing(monkeypatch):
    calls = []
    def fake_exec(cmd, cwd=None, capture_output=False):
        calls.append((cmd, cwd, capture_output))
        if cmd == ['git', 'branch', '-a']:
            return 'remotes/origin/feat'
        return ''
    monkeypatch.setattr(git_shell, 'execute_shell_command', fake_exec)
    git_shell.create_or_update_branch('cwd', 'feat')
    assert calls[0][0] == ['git', 'fetch']
    assert calls[1][0] == ['git', 'branch', '-a']
    assert calls[2][0] == ['git', 'push', '-f']

def test_create_or_update_branch_new(monkeypatch):
    calls = []
    def fake_exec(cmd, cwd=None, capture_output=False):
        calls.append(cmd)
        return "" 
    monkeypatch.setattr(git_shell, "execute_shell_command", fake_exec)
    git_shell.create_or_update_branch("cwd", "feat")
    assert calls[0] == ['git', 'fetch']
    assert calls[1] == ['git', 'branch', '-a']
    assert calls[2] == ['git', 'checkout', '-b', 'feat']



def test_commit_and_push(monkeypatch):
    cmds = []
    monkeypatch.setattr(git_shell, 'execute_shell_command', lambda cmd, cwd=None, capture_output=False: cmds.append(cmd) or '')
    git_shell.commit_changes('cwd', 'msg')
    git_shell.push_changes('cwd', 'br')
    assert cmds == [
        ['git', 'add', '.'],
        ['git', 'commit', '-am', 'msg'],
        ['git', 'push', 'origin', 'br']
    ]


def test_github_commands(monkeypatch):
    cmds = []
    monkeypatch.setattr(github, 'execute_shell_command', lambda cmd, cwd=None, capture_output=False: cmds.append(cmd) or '')
    github.check_auth('cwd')
    github.create_merge_request('cwd', 'main', 'feat', 'rel')
    github.merge_pr('cwd', 'feat', 'rel')
    github.create_release('cwd', 'main', 'rel')
    monkeypatch.setattr(github, 'execute_shell_command', lambda cmd, cwd=None, capture_output=True: 'open')
    assert github.check_for_open_prs('cwd', 'feat')
    monkeypatch.setattr(github, 'execute_shell_command', lambda cmd, cwd=None, capture_output=True: 'merged')
    assert github.check_for_merged_prs('cwd', 'feat')
    expected = [
        ['gh', 'auth', 'status'],
        ['gh', 'pr', 'create', '--base', 'main', '--head', 'feat', '--title', 'Release rel', '--body', 'Automated release PR for rel'],
        ['gh', 'pr', 'merge', 'feat', '--squash', '--delete-branch', '--subject', 'Merge Release rel'],
        ['gh', 'release', 'create', 'rel', '--target', 'main', '--title', 'rel']
    ]
    assert cmds == expected
