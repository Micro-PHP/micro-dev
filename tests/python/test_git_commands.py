import os
from git import Repo
import pytest
import git_commands


def create_remote_repo(tmp_path):
    remote_path = tmp_path / "remote"
    repo = Repo.init(remote_path)
    (remote_path / "file.txt").write_text("init")
    repo.index.add(["file.txt"])
    repo.index.commit("init")
    repo.create_head("2.x")
    return repo


def test_init_repository_fetch_and_reset(tmp_path):
    remote_repo = create_remote_repo(tmp_path)
    local_dir = tmp_path / "local"
    repo = git_commands.init_repository(str(local_dir), str(remote_repo.working_tree_dir), "2.x")
    assert repo.remotes.origin.url == str(remote_repo.working_tree_dir)
    assert "2.x" in repo.heads
    assert repo.heads["2.x"].commit.hexsha == remote_repo.refs["2.x"].commit.hexsha


def test_init_repository_does_not_reset_local_changes(tmp_path):
    remote_repo = create_remote_repo(tmp_path)
    local_dir = tmp_path / "local"
    repo = git_commands.init_repository(str(local_dir), str(remote_repo.working_tree_dir), "2.x")
    repo.heads["2.x"].checkout()

    file_path = local_dir / "file.txt"
    file_path.write_text("local change")

    git_commands.init_repository(str(local_dir), str(remote_repo.working_tree_dir), "2.x")

    assert file_path.read_text() == "local change"


def test_update_repository_remote_link(tmp_path):
    repo = Repo.init(tmp_path / "repo")
    repo.create_remote("origin", "old")
    git_commands.update_repository_remote_link(repo, "origin", "new")
    assert repo.remotes.origin.url == "new"


def test_fetch_tags(tmp_path):
    remote_path = tmp_path / "remote.git"
    remote_repo = Repo.init(remote_path, bare=True)
    source_path = tmp_path / "source"
    source_repo = Repo.clone_from(str(remote_path), source_path)
    file_path = source_path / "file.txt"
    file_path.write_text("content")
    source_repo.index.add(["file.txt"])
    source_repo.index.commit("init")
    source_repo.git.push('--all', 'origin')

    local_path = tmp_path / "local"
    local_repo = Repo.clone_from(str(remote_path), local_path)

    source_repo.create_tag("v1.0.0")
    source_repo.git.push('--tags', 'origin')

    assert all(tag.name != "v1.0.0" for tag in local_repo.tags)
    git_commands.fetch_tags(local_repo)
    assert any(tag.name == "v1.0.0" for tag in local_repo.tags)


def test_checkout_fetch_and_checkout_branch(tmp_path):
    remote_dir = tmp_path / "remote"
    remote_repo = Repo.init(remote_dir)
    (remote_dir / "f.txt").write_text("test")
    remote_repo.index.add(["f.txt"])
    remote_repo.index.commit("init")
    remote_repo.create_head("feature")
    local_repo = Repo.clone_from(str(remote_dir), tmp_path / "local")
    git_commands.checkout(local_repo, "pkg", "feature")
    assert local_repo.active_branch.name == "feature"
    assert local_repo.head.commit.hexsha == remote_repo.head.commit.hexsha


def test_checkout_raises_for_dirty_repository(tmp_path):
    remote_dir = tmp_path / "remote"
    remote_repo = Repo.init(remote_dir)
    (remote_dir / "f.txt").write_text("test")
    remote_repo.index.add(["f.txt"])
    remote_repo.index.commit("init")
    remote_repo.create_head("feature")

    local_repo = Repo.clone_from(str(remote_dir), tmp_path / "local")
    (tmp_path / "local" / "f.txt").write_text("dirty")

    with pytest.raises(git_commands.RepositoryDirtyError):
        git_commands.checkout(local_repo, "pkg", "feature")


def test_checkout_unborn_repository_to_remote_branch_tracks_matching_files(tmp_path):
    remote_dir = tmp_path / "remote"
    remote_repo = Repo.init(remote_dir)
    (remote_dir / "f.txt").write_text("test")
    remote_repo.index.add(["f.txt"])
    remote_repo.index.commit("init")
    remote_repo.create_head("2.x")

    local_dir = tmp_path / "local"
    local_dir.mkdir()
    (local_dir / "f.txt").write_text("test")
    local_repo = Repo.init(local_dir)
    local_repo.create_remote("origin", str(remote_dir))

    git_commands.checkout(local_repo, "pkg", "2.x")

    assert local_repo.active_branch.name == "2.x"
    assert not local_repo.is_dirty(untracked_files=True)


def test_create_branch_from_remote(tmp_path):
    remote_dir = tmp_path / "remote"
    remote_repo = Repo.init(remote_dir)
    (remote_dir / "f.txt").write_text("test")
    remote_repo.index.add(["f.txt"])
    remote_repo.index.commit("init")
    remote_repo.create_head("2.x")

    local_repo = Repo.clone_from(str(remote_dir), tmp_path / "local")

    git_commands.create_branch_from_remote(local_repo, "pkg", "2.x-dev", "2.x")

    assert local_repo.active_branch.name == "2.x-dev"
    assert local_repo.head.commit.hexsha == remote_repo.refs["2.x"].commit.hexsha


def test_create_branch_from_remote_pushes_when_requested(tmp_path):
    remote_path = tmp_path / "remote.git"
    remote_repo = Repo.init(remote_path, bare=True)
    source_path = tmp_path / "source"
    source_repo = Repo.clone_from(str(remote_path), source_path)
    (source_path / "f.txt").write_text("test")
    source_repo.index.add(["f.txt"])
    source_repo.index.commit("init")
    source_repo.create_head("2.x")
    source_repo.git.push("--all", "origin")

    local_repo = Repo.clone_from(str(remote_path), tmp_path / "local")

    git_commands.create_branch_from_remote(local_repo, "pkg", "2.x-dev", "2.x", push_missing_branch=True)

    remote_clone = Repo.clone_from(str(remote_path), tmp_path / "verify")
    assert any(ref.remote_head == "2.x-dev" for ref in remote_clone.remotes.origin.refs)


def test_create_branch_from_remote_raises_for_missing_base(tmp_path):
    remote_dir = tmp_path / "remote"
    remote_repo = Repo.init(remote_dir)
    (remote_dir / "f.txt").write_text("test")
    remote_repo.index.add(["f.txt"])
    remote_repo.index.commit("init")

    local_repo = Repo.clone_from(str(remote_dir), tmp_path / "local")

    with pytest.raises(git_commands.MissingBaseBranchError):
        git_commands.create_branch_from_remote(local_repo, "pkg", "2.x-dev", "2.x")


def test_create_branch_from_remote_for_unborn_repo_keeps_worktree(tmp_path):
    remote_dir = tmp_path / "remote"
    remote_repo = Repo.init(remote_dir)
    (remote_dir / "f.txt").write_text("test")
    remote_repo.index.add(["f.txt"])
    remote_repo.index.commit("init")
    remote_repo.create_head("2.x")

    local_dir = tmp_path / "local"
    local_dir.mkdir()
    (local_dir / "local.txt").write_text("keep me")
    local_repo = Repo.init(local_dir)
    local_repo.create_remote("origin", str(remote_dir))

    git_commands.create_branch_from_remote(local_repo, "pkg", "2.x-dev", "2.x")

    assert local_repo.active_branch.name == "2.x-dev"
    assert (local_dir / "local.txt").read_text() == "keep me"


def test_create_branch_from_remote_for_unborn_repo_tracks_matching_files(tmp_path):
    remote_dir = tmp_path / "remote"
    remote_repo = Repo.init(remote_dir)
    (remote_dir / "f.txt").write_text("test")
    remote_repo.index.add(["f.txt"])
    remote_repo.index.commit("init")
    remote_repo.create_head("2.x")

    local_dir = tmp_path / "local"
    local_dir.mkdir()
    (local_dir / "f.txt").write_text("test")
    local_repo = Repo.init(local_dir)
    local_repo.create_remote("origin", str(remote_dir))

    git_commands.create_branch_from_remote(local_repo, "pkg", "2.x-dev", "2.x")

    assert local_repo.active_branch.name == "2.x-dev"
    assert not local_repo.is_dirty(untracked_files=True)


def test_create_branch_from_remote_for_unborn_repo_pushes_when_requested(tmp_path):
    remote_dir = tmp_path / "remote"
    remote_repo = Repo.init(remote_dir)
    (remote_dir / "f.txt").write_text("test")
    remote_repo.index.add(["f.txt"])
    remote_repo.index.commit("init")
    remote_repo.create_head("2.x")

    local_dir = tmp_path / "local"
    local_dir.mkdir()
    (local_dir / "f.txt").write_text("test")
    local_repo = Repo.init(local_dir)
    local_repo.create_remote("origin", str(remote_dir))

    git_commands.create_branch_from_remote(local_repo, "pkg", "2.x-dev", "2.x", push_missing_branch=True)

    remote_clone = Repo.clone_from(str(remote_dir), tmp_path / "verify")
    assert any(ref.remote_head == "2.x-dev" for ref in remote_clone.remotes.origin.refs)


def test_commit_changes_and_get_changes(tmp_path):
    repo_dir = tmp_path / "repo"
    repo = Repo.init(repo_dir)
    f1 = repo_dir / "f1.txt"
    f1.write_text("a")
    repo.index.add([str(f1)])
    repo.index.commit("init")
    f1.write_text("b")
    f2 = repo_dir / "f2.txt"
    f2.write_text("new")
    f3 = repo_dir / "f3.txt"
    f3.write_text("del")
    repo.index.add([str(f3)])
    repo.index.commit("tmp")
    os.remove(f3)
    f4 = repo_dir / "f4.txt"
    f4.write_text("stage")
    repo.index.add([str(f4)])


    to_add, to_remove = git_commands.get_changes_to_commit(repo)
    assert set(to_add) == {"f1.txt", "f2.txt"}
    assert to_remove == ["f3.txt"]

    git_commands.commit_changes(repo, "v1", "pkg")
    assert repo.head.commit.message == "Update v1 for pkg"
    assert not repo.is_dirty(untracked_files=True)
