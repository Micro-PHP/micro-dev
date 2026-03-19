import os
import logging
import argparse
import subprocess
import sys
from types import SimpleNamespace
import pytest
from git import Repo
import init, fix, release, clean
from git_commands import MissingBranchError, RepositoryDirtyError, MissingBaseBranchError


def test_init_handles_missing_branch(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(init, 'read_packages', lambda f: {'pkg': str(tmp_path)})
    monkeypatch.setattr(init, 'get_repository_link', lambda pkg: 'url')
    monkeypatch.setattr(init, 'init_repository', lambda folder, repo, branch: 'repo')
    def fake_checkout(repo, package, branch):
        raise MissingBranchError('missing')
    monkeypatch.setattr(init, 'checkout', fake_checkout)
    init.main('2.x', 'cfg')
    captured = capsys.readouterr()
    assert 'pkg' in captured.out


def test_init_creates_missing_branch_from_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr(init, 'read_packages', lambda f: {'pkg': str(tmp_path)})
    monkeypatch.setattr(init, 'get_repository_link', lambda pkg: 'url')
    monkeypatch.setattr(init, 'init_repository', lambda folder, repo, branch: 'repo')

    calls = []

    def fake_checkout(repo, package, branch):
        calls.append(branch)
        raise MissingBranchError('missing')

    called = {}

    def fake_create(repo, package, branch, from_branch, push_missing_branches):
        called['args'] = (package, branch, from_branch, push_missing_branches)

    monkeypatch.setattr(init, 'checkout', fake_checkout)
    monkeypatch.setattr(init, 'create_branch_from_remote', fake_create)

    init.main('2.x-dev', 'cfg', from_branch='2.x', push_missing_branches=True)

    assert calls == ['2.x-dev']
    assert called['args'] == ('pkg', '2.x-dev', '2.x', True)


def test_init_checks_out_fallback_branch_when_push_not_requested(monkeypatch, tmp_path):
    monkeypatch.setattr(init, 'read_packages', lambda f: {'pkg': str(tmp_path)})
    monkeypatch.setattr(init, 'get_repository_link', lambda pkg: 'url')
    monkeypatch.setattr(init, 'init_repository', lambda folder, repo, branch: 'repo')

    calls = []

    def fake_checkout(repo, package, branch):
        calls.append(branch)
        if branch == '2.x-dev':
            raise MissingBranchError('missing')

    monkeypatch.setattr(init, 'checkout', fake_checkout)

    init.main('2.x-dev', 'cfg', from_branch='2.x', push_missing_branches=False)

    assert calls == ['2.x-dev', '2.x']


def test_init_reports_missing_fallback_branch(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(init, 'read_packages', lambda f: {'pkg': str(tmp_path)})
    monkeypatch.setattr(init, 'get_repository_link', lambda pkg: 'url')
    monkeypatch.setattr(init, 'init_repository', lambda folder, repo, branch: 'repo')

    def fake_checkout(repo, package, branch):
        raise MissingBranchError('missing')

    def fake_create(repo, package, branch, from_branch, push_missing_branches):
        raise MissingBaseBranchError('missing base')

    monkeypatch.setattr(init, 'checkout', fake_checkout)
    monkeypatch.setattr(init, 'create_branch_from_remote', fake_create)

    init.main('2.x-dev', 'cfg', from_branch='2.x')

    captured = capsys.readouterr()
    assert 'fallback 2.x branch' in captured.out


def test_init_reports_dirty_repository(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(init, 'read_packages', lambda f: {'pkg': str(tmp_path)})
    monkeypatch.setattr(init, 'get_repository_link', lambda pkg: 'url')
    monkeypatch.setattr(init, 'init_repository', lambda folder, repo, branch: 'repo')

    def fake_checkout(repo, package, branch):
        raise RepositoryDirtyError('dirty')

    monkeypatch.setattr(init, 'checkout', fake_checkout)
    init.main('2.x', 'cfg')
    captured = capsys.readouterr()
    assert 'local changes' in captured.out


def test_fix_main_logs_errors(monkeypatch, caplog, tmp_path):
    paths = {'pkg1': str(tmp_path / 'p1'), 'pkg2': str(tmp_path / 'p2')}
    for p in paths.values():
        os.makedirs(p)
    monkeypatch.setattr(fix, 'read_packages', lambda f: paths)
    monkeypatch.setattr(fix, 'get_repository_link', lambda pkg: 'url')
    def fake_get_repo(path):
        if path.endswith('p1'):
            raise fix.InvalidGitRepositoryError('bad')
        return 'repo'
    monkeypatch.setattr(fix, 'get_repository', fake_get_repo)
    def fake_update(repo, name, url):
        if repo == 'repo' and name == 'origin':
            raise Exception('err')
    monkeypatch.setattr(fix, 'update_repository_remote_link', fake_update)
    caplog.set_level(logging.ERROR)
    fix.main('cfg')
    assert 'pkg1' in caplog.text
    assert 'pkg2' in caplog.text


def test_clean_removes_git_directory(tmp_path):
    package_dir = tmp_path / 'pkg'
    git_dir = package_dir / '.git'
    git_dir.mkdir(parents=True)
    (package_dir / 'file.txt').write_text('keep me')

    removed = clean.remove_git_metadata(str(package_dir))

    assert removed is True
    assert not git_dir.exists()
    assert (package_dir / 'file.txt').read_text() == 'keep me'


def test_clean_removes_git_file(tmp_path):
    package_dir = tmp_path / 'pkg'
    package_dir.mkdir(parents=True)
    git_file = package_dir / '.git'
    git_file.write_text('gitdir: /tmp/example')

    removed = clean.remove_git_metadata(str(package_dir))

    assert removed is True
    assert not git_file.exists()


def test_clean_main_processes_packages(monkeypatch, tmp_path):
    paths = {'pkg1': str(tmp_path / 'p1'), 'pkg2': str(tmp_path / 'p2')}
    monkeypatch.setattr(clean, 'read_packages', lambda f: paths)
    removed = []
    monkeypatch.setattr(clean, 'remove_git_metadata', lambda path: removed.append(path) or path.endswith('p1'))

    cleaned = clean.main('cfg')

    assert removed == [str(tmp_path / 'p1'), str(tmp_path / 'p2')]
    assert cleaned == [str(tmp_path / 'p1')]


def test_all_scripts_support_help():
    scripts_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')

    for script_name in sorted(name for name in os.listdir(scripts_dir) if name.endswith('.py')):
        result = subprocess.run(
            [sys.executable, script_name, '--help'],
            cwd=scripts_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        combined_output = f'{result.stdout}\n{result.stderr}'

        assert result.returncode == 0, f'--help failed for {script_name}: {combined_output}'
        assert 'usage:' in combined_output.lower(), f'No usage output for {script_name}'


def test_release_main_merge(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    monkeypatch.setattr(release, 'read_packages', lambda f: paths)
    monkeypatch.setattr(release, 'preflight_branches', lambda packages, rel, base, merge: [])
    monkeypatch.setattr(release, 'preflight_clean_worktrees', lambda packages: [])
    monkeypatch.setattr(release, 'check_for_open_prs', lambda cwd, b: True)
    monkeypatch.setattr(release, 'check_for_merged_prs', lambda cwd, b: False)
    monkeypatch.setattr(release, 'check_gh_installed', lambda: True)
    monkeypatch.setattr(release, 'validate_gh_access', lambda: True)
    monkeypatch.setattr(release, 'get_repository', lambda p: object())
    monkeypatch.setattr(release, 'compute_next_version', lambda r: 'v2.0.1')
    monkeypatch.setattr(release, 'collect_release_notes', lambda r, b: 'notes')
    called = {}
    monkeypatch.setattr(release, 'fetch_tags', lambda repo: called.setdefault('fetch_tags', True))
    def fake_merge(cwd, b, r):
        called['merge'] = r
    def fake_release(cwd, base, r, notes):
        called['release'] = (r, notes)
    monkeypatch.setattr(release, 'merge_pr', fake_merge)
    monkeypatch.setattr(release, 'create_release', fake_release)
    failed = release.main('v1', 'br', 'base', 'cfg', True, False, False)
    assert failed == []
    assert called == {'fetch_tags': True, 'merge': 'v2.0.1', 'release': ('v2.0.1', 'notes')}


def test_release_main_merge_skips_release_without_open_pr(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    monkeypatch.setattr(release, 'read_packages', lambda f: paths)
    monkeypatch.setattr(release, 'preflight_branches', lambda packages, rel, base, merge: [])
    monkeypatch.setattr(release, 'preflight_clean_worktrees', lambda packages: [])
    monkeypatch.setattr(release, 'check_for_open_prs', lambda cwd, b: False)
    monkeypatch.setattr(release, 'check_for_merged_prs', lambda cwd, b: False)
    monkeypatch.setattr(release, 'check_gh_installed', lambda: True)
    monkeypatch.setattr(release, 'validate_gh_access', lambda: True)
    monkeypatch.setattr(release, 'get_repository', lambda p: object())
    monkeypatch.setattr(release, 'fetch_tags', lambda repo: None)
    actions = []
    monkeypatch.setattr(release, 'merge_pr', lambda *args: actions.append('merge'))
    monkeypatch.setattr(release, 'create_release', lambda *args: actions.append('release'))

    failed = release.main('v1', 'br', 'base', 'cfg', True, False, False)

    assert failed == []
    assert actions == []


def test_release_main_commit_flow(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    repo = object()
    monkeypatch.setattr(release, 'read_packages', lambda f: paths)
    monkeypatch.setattr(release, 'preflight_branches', lambda packages, rel, base, merge: [])
    monkeypatch.setattr(release, 'preflight_clean_worktrees', lambda packages: [])
    monkeypatch.setattr(release, 'get_repository', lambda p: repo)
    monkeypatch.setattr(release, 'get_changes_to_commit', lambda r: (['a'], []))
    monkeypatch.setattr(release, 'check_gh_installed', lambda: True)
    monkeypatch.setattr(release, 'validate_gh_access', lambda: True)
    actions = []
    monkeypatch.setattr(release, 'create_or_update_branch', lambda r, pkg, br: actions.append('branch'))
    monkeypatch.setattr(release, 'commit_changes', lambda r, rn, pkg: actions.append('commit'))
    monkeypatch.setattr(release, 'push_changes', lambda r: actions.append('push'))
    monkeypatch.setattr(release, 'check_for_open_prs', lambda c, b: False)
    monkeypatch.setattr(release, 'create_merge_request', lambda c, base, br, rn: actions.append('pr'))
    failed = release.main('v1', 'br', 'base', 'cfg', False, False, False)
    assert failed == []
    assert actions == ['branch', 'commit', 'push', 'pr']


def test_release_main_creates_missing_release_for_already_merged_pr(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    monkeypatch.setattr(release, 'read_packages', lambda f: paths)
    monkeypatch.setattr(release, 'preflight_branches', lambda packages, rel, base, merge: [])
    monkeypatch.setattr(release, 'preflight_clean_worktrees', lambda packages: [])
    monkeypatch.setattr(release, 'check_for_open_prs', lambda cwd, b: False)
    monkeypatch.setattr(release, 'check_for_merged_prs', lambda cwd, b: True)
    monkeypatch.setattr(release, 'check_gh_installed', lambda: True)
    monkeypatch.setattr(release, 'validate_gh_access', lambda: True)
    monkeypatch.setattr(release, 'get_repository', lambda p: object())
    monkeypatch.setattr(release, 'fetch_tags', lambda repo: None)
    monkeypatch.setattr(release, 'has_unreleased_commits', lambda repo, branch: True)
    monkeypatch.setattr(release, 'compute_next_version', lambda r: 'v2.0.1')
    monkeypatch.setattr(release, 'collect_release_notes', lambda r, b: 'notes')
    actions = []
    monkeypatch.setattr(release, 'merge_pr', lambda *args: actions.append('merge'))
    monkeypatch.setattr(release, 'create_release', lambda cwd, base, rel, notes: actions.append((base, rel, notes)))

    failed = release.main('v1', 'br', 'base', 'cfg', True, False, False)

    assert failed == []
    assert actions == [('base', 'v2.0.1', 'notes')]


def test_release_main_skips_missing_release_recovery_when_nothing_unreleased(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    monkeypatch.setattr(release, 'read_packages', lambda f: paths)
    monkeypatch.setattr(release, 'preflight_branches', lambda packages, rel, base, merge: [])
    monkeypatch.setattr(release, 'preflight_clean_worktrees', lambda packages: [])
    monkeypatch.setattr(release, 'check_for_open_prs', lambda cwd, b: False)
    monkeypatch.setattr(release, 'check_for_merged_prs', lambda cwd, b: True)
    monkeypatch.setattr(release, 'check_gh_installed', lambda: True)
    monkeypatch.setattr(release, 'validate_gh_access', lambda: True)
    monkeypatch.setattr(release, 'get_repository', lambda p: object())
    monkeypatch.setattr(release, 'fetch_tags', lambda repo: None)
    monkeypatch.setattr(release, 'has_unreleased_commits', lambda repo, branch: False)
    actions = []
    monkeypatch.setattr(release, 'merge_pr', lambda *args: actions.append('merge'))
    monkeypatch.setattr(release, 'create_release', lambda *args: actions.append('release'))

    failed = release.main('v1', 'br', 'base', 'cfg', True, False, False)

    assert failed == []
    assert actions == []


def test_release_cli_requires_base_branch(monkeypatch):
    monkeypatch.setattr(release, 'check_gh_installed', lambda: True)
    captured = {}

    def fake_error(self, message):
        captured['msg'] = message
        raise SystemExit(2)

    monkeypatch.setattr(argparse.ArgumentParser, 'error', fake_error, raising=False)
    with pytest.raises(SystemExit):
        release.run_cli(['--release-branch', 'rel-branch', '--config', 'cfg', 'rel'])
    assert 'base-branch' in captured['msg']


def test_release_cli_requires_release_branch(monkeypatch):
    monkeypatch.setattr(release, 'check_gh_installed', lambda: True)
    captured = {}

    def fake_error(self, message):
        captured['msg'] = message
        raise SystemExit(2)

    monkeypatch.setattr(argparse.ArgumentParser, 'error', fake_error, raising=False)
    with pytest.raises(SystemExit):
        release.run_cli(['--base-branch', '2.x', '--config', 'cfg', 'rel'])
    assert 'release-branch' in captured['msg']


def test_release_cli_exits_non_zero_on_failed_packages(monkeypatch):
    monkeypatch.setattr(release, 'main', lambda *args: ['pkg'])
    monkeypatch.setattr(release, 'os', os)

    with pytest.raises(SystemExit) as exc:
        release.run_cli(['--base-branch', '2.x', '--release-branch', 'release/1', '--config', 'cfg', 'rel'])

    assert exc.value.code == 1


def test_validate_gh_access_handles_shell_error(monkeypatch, caplog):
    monkeypatch.setattr(release, 'check_auth', lambda: (_ for _ in ()).throw(release.ShellError('bad auth')))
    caplog.set_level(logging.ERROR)

    assert release.validate_gh_access() is False
    assert 'authentication check failed' in caplog.text


def test_preflight_branches_fails_for_missing_base_branch(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    repo = object()
    monkeypatch.setattr(release, 'get_repository', lambda p: repo)
    monkeypatch.setattr(release, 'fetch_remote', lambda repo: None)
    monkeypatch.setattr(release, 'has_remote_branch', lambda repo, branch: branch == 'release/1')
    monkeypatch.setattr(release, 'check_for_merged_prs', lambda cwd, branch: False)

    failed = release.preflight_branches(paths, 'release/1', '2.x', False)

    assert failed == ['pkg']


def test_preflight_branches_fails_for_missing_release_branch_in_prepare(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    repo = object()
    monkeypatch.setattr(release, 'get_repository', lambda p: repo)
    monkeypatch.setattr(release, 'fetch_remote', lambda repo: None)
    monkeypatch.setattr(release, 'has_remote_branch', lambda repo, branch: branch == '2.x')
    monkeypatch.setattr(release, 'check_for_merged_prs', lambda cwd, branch: False)

    failed = release.preflight_branches(paths, 'release/1', '2.x', False)

    assert failed == ['pkg']


def test_preflight_branches_allows_missing_release_branch_for_merged_pr_recovery(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    repo = object()
    monkeypatch.setattr(release, 'get_repository', lambda p: repo)
    monkeypatch.setattr(release, 'fetch_remote', lambda repo: None)
    monkeypatch.setattr(release, 'has_remote_branch', lambda repo, branch: branch == '2.x')
    monkeypatch.setattr(release, 'check_for_merged_prs', lambda cwd, branch: True)

    failed = release.preflight_branches(paths, 'release/1', '2.x', True)

    assert failed == []


def test_release_main_returns_preflight_failures_without_processing(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    monkeypatch.setattr(release, 'read_packages', lambda f: paths)
    monkeypatch.setattr(release, 'check_gh_installed', lambda: True)
    monkeypatch.setattr(release, 'validate_gh_access', lambda: True)
    monkeypatch.setattr(release, 'preflight_branches', lambda packages, rel, base, merge: ['pkg'])
    called = []
    monkeypatch.setattr(release, 'get_repository', lambda p: called.append('repo'))

    failed = release.main('v1', 'release/1', '2.x', 'cfg', False, False, False)

    assert failed == ['pkg']
    assert called == []


def test_preflight_clean_worktrees_fails_for_tracked_changes(tmp_path):
    repo = Repo.init(tmp_path)
    file_path = tmp_path / 'file.txt'
    file_path.write_text('a')
    repo.index.add(['file.txt'])
    repo.index.commit('init')
    file_path.write_text('b')

    failed = release.preflight_clean_worktrees({'pkg': str(tmp_path)})

    assert failed == ['pkg']


def test_preflight_clean_worktrees_fails_for_untracked_files(tmp_path):
    repo = Repo.init(tmp_path)
    file_path = tmp_path / 'file.txt'
    file_path.write_text('a')
    repo.index.add(['file.txt'])
    repo.index.commit('init')
    (tmp_path / 'extra.txt').write_text('untracked')

    failed = release.preflight_clean_worktrees({'pkg': str(tmp_path)})

    assert failed == ['pkg']


def test_preflight_clean_worktrees_passes_for_clean_repo(tmp_path):
    repo = Repo.init(tmp_path)
    file_path = tmp_path / 'file.txt'
    file_path.write_text('a')
    repo.index.add(['file.txt'])
    repo.index.commit('init')

    failed = release.preflight_clean_worktrees({'pkg': str(tmp_path)})

    assert failed == []


def test_release_main_returns_worktree_preflight_failures_without_processing(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    monkeypatch.setattr(release, 'read_packages', lambda f: paths)
    monkeypatch.setattr(release, 'check_gh_installed', lambda: True)
    monkeypatch.setattr(release, 'validate_gh_access', lambda: True)
    monkeypatch.setattr(release, 'preflight_branches', lambda packages, rel, base, merge: [])
    monkeypatch.setattr(release, 'preflight_clean_worktrees', lambda packages: ['pkg'])
    called = []
    monkeypatch.setattr(release, 'get_repository', lambda p: called.append('repo'))

    failed = release.main('v1', 'release/1', '2.x', 'cfg', False, False, False)

    assert failed == ['pkg']
    assert called == []


def test_release_main_skips_worktree_preflight_in_merge_mode(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    monkeypatch.setattr(release, 'read_packages', lambda f: paths)
    monkeypatch.setattr(release, 'preflight_branches', lambda packages, rel, base, merge: [])
    called = []
    monkeypatch.setattr(release, 'preflight_clean_worktrees', lambda packages: called.append('worktree') or ['pkg'])
    monkeypatch.setattr(release, 'check_gh_installed', lambda: True)
    monkeypatch.setattr(release, 'validate_gh_access', lambda: True)
    monkeypatch.setattr(release, 'get_repository', lambda p: object())
    monkeypatch.setattr(release, 'fetch_tags', lambda repo: None)
    monkeypatch.setattr(release, 'check_for_open_prs', lambda cwd, b: False)
    monkeypatch.setattr(release, 'check_for_merged_prs', lambda cwd, b: False)

    failed = release.main('v1', 'release/1', '2.x', 'cfg', True, False, False)

    assert failed == []
    assert called == []


def test_plan_package_action_reports_blocked_dirty_prepare_repo(monkeypatch, tmp_path):
    repo = Repo.init(tmp_path)
    file_path = tmp_path / 'file.txt'
    file_path.write_text('a')
    repo.index.add(['file.txt'])
    repo.index.commit('init')
    file_path.write_text('dirty')

    monkeypatch.setattr(release, 'fetch_remote', lambda repo: None)
    monkeypatch.setattr(release, 'has_remote_branch', lambda repo, branch: branch == '2.x')

    action, blocked = release.plan_package_action('pkg', str(tmp_path), 'release/1', '2.x', False, False, False)

    assert blocked is True
    assert 'local changes or untracked files' in action


def test_release_main_dry_run_uses_preview_without_running_preflight(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    monkeypatch.setattr(release, 'read_packages', lambda f: paths)
    monkeypatch.setattr(release, 'check_gh_installed', lambda: True)
    monkeypatch.setattr(release, 'validate_gh_access', lambda: True)
    monkeypatch.setattr(release, 'preview_actions', lambda *args: [])
    called = []
    monkeypatch.setattr(release, 'preflight_branches', lambda *args: called.append('branches') or [])
    monkeypatch.setattr(release, 'preflight_clean_worktrees', lambda *args: called.append('worktrees') or [])

    failed = release.main('v1', 'release/1', '2.x', 'cfg', False, False, False, dry_run=True)

    assert failed == []
    assert called == []


def test_release_main_status_returns_blocked_preview_packages(monkeypatch, tmp_path):
    paths = {'pkg': str(tmp_path)}
    monkeypatch.setattr(release, 'read_packages', lambda f: paths)
    monkeypatch.setattr(release, 'check_gh_installed', lambda: True)
    monkeypatch.setattr(release, 'validate_gh_access', lambda: True)
    monkeypatch.setattr(release, 'preview_actions', lambda *args: ['pkg'])

    failed = release.main('v1', 'release/1', '2.x', 'cfg', False, False, False, status=True)

    assert failed == ['pkg']


def test_collect_release_notes_uses_commit_subjects_for_squash_flow(tmp_path):
    repo = Repo.init(tmp_path)
    file_path = tmp_path / 'file.txt'

    file_path.write_text('base')
    repo.index.add(['file.txt'])
    repo.index.commit('Initial commit')
    repo.create_head('main')
    repo.heads['main'].checkout()
    repo.create_tag('v1.0.0')

    file_path.write_text('change 1')
    repo.index.add(['file.txt'])
    repo.index.commit('Release feature A\n\nbody text')

    file_path.write_text('change 2')
    repo.index.add(['file.txt'])
    repo.index.commit('Fix bug B')

    notes = release.collect_release_notes(repo, 'main')

    assert notes == 'Release feature A\nFix bug B'
