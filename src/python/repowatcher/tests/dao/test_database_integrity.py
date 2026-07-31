import sqlite3
from types import SimpleNamespace

import pytest

from repowatcher.gitrepocontroller import GitRepoController


@pytest.fixture
def controller(tmp_path):
    repo_controller = GitRepoController(str(tmp_path))
    yield repo_controller
    repo_controller.conn.close()


def _create_repo(controller, path, categories):
    return controller.entity_factory.create_repo(
        {
            "name": path.rsplit("/", 1)[-1],
            "path": path,
            "categories": categories,
            "update_command": "git remote update",
        }
    )


def test_fresh_database_enforces_uniqueness_foreign_keys_and_cascades(controller):
    assert controller.conn.execute("PRAGMA foreign_keys").fetchone() == (1,)

    work = controller.categoryDAO.save("Work")
    same_work = controller.categoryDAO.save("work")
    assert same_work.id == work.id
    assert controller.conn.execute(
        "SELECT COUNT(*) FROM Categories WHERE category_name = ? COLLATE NOCASE",
        ("work",),
    ).fetchone() == (1,)

    repo = _create_repo(controller, "/repos/project", [work])
    controller.repoDAO.save(repo)
    controller.categoryDAO.save_repo_category(repo, work)
    assert controller.conn.execute(
        "SELECT COUNT(*) FROM RepoCategories WHERE id_repo = ?",
        (repo.id,),
    ).fetchone() == (1,)

    duplicate_repo = _create_repo(controller, "/repos/project", [work])
    with pytest.raises(sqlite3.IntegrityError):
        controller.repoDAO.save(duplicate_repo)
    assert duplicate_repo.id == -1

    controller.repoDAO.delete(repo)
    assert controller.conn.execute(
        "SELECT COUNT(*) FROM RepoCategories WHERE id_repo = ?",
        (repo.id,),
    ).fetchone() == (0,)

    repo_with_deleted_category = _create_repo(
        controller,
        "/repos/category-cascade",
        [work],
    )
    controller.repoDAO.save(repo_with_deleted_category)
    controller.categoryDAO.delete(work)
    assert controller.conn.execute(
        "SELECT COUNT(*) FROM RepoCategories WHERE id_repo = ?",
        (repo_with_deleted_category.id,),
    ).fetchone() == (0,)


def test_repo_save_rolls_back_when_category_association_fails(controller):
    repo = _create_repo(
        controller,
        "/repos/atomic-save",
        [SimpleNamespace(id=9999, name="missing")],
    )

    with pytest.raises(sqlite3.IntegrityError):
        controller.repoDAO.save(repo)

    assert repo.id == -1
    assert controller.conn.execute(
        "SELECT COUNT(*) FROM RepoWatcher WHERE repo_path = ?",
        (repo.path,),
    ).fetchone() == (0,)


def test_repo_update_rolls_back_record_and_categories_together(controller):
    original_category = controller.categoryDAO.save("original")
    repo = _create_repo(controller, "/repos/atomic-update", [original_category])
    controller.repoDAO.save(repo)

    repo.update_command = "git pull --rebase"
    repo.categories = [SimpleNamespace(id=9999, name="missing")]

    with pytest.raises(sqlite3.IntegrityError):
        controller.repoDAO.update(repo)

    stored_update_command = controller.conn.execute(
        "SELECT update_command FROM RepoWatcher WHERE id_repo = ?",
        (repo.id,),
    ).fetchone()
    stored_categories = controller.conn.execute(
        "SELECT id_category FROM RepoCategories WHERE id_repo = ?",
        (repo.id,),
    ).fetchall()
    assert stored_update_command == ("git remote update",)
    assert stored_categories == [(original_category.id,)]


def test_legacy_schema_migration_deduplicates_and_preserves_associations(tmp_path):
    database_path = tmp_path / "gitrepowatcher.sqlite"
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    cursor.executescript('''
        CREATE TABLE RepoWatcher (
            id_repo INTEGER PRIMARY KEY,
            repo_name TEXT,
            repo_path TEXT,
            update_command TEXT,
            operation_time TEXT
        );
        CREATE TABLE Categories (
            id_category INTEGER PRIMARY KEY,
            category_name TEXT
        );
        CREATE TABLE RepoCategories (
            id_repocategory INTEGER PRIMARY KEY,
            id_repo INTEGER,
            id_category INTEGER,
            FOREIGN KEY (id_repo) REFERENCES RepoWatcher (id_repo),
            FOREIGN KEY (id_category) REFERENCES Categories (id_category)
        );
        INSERT INTO RepoWatcher VALUES
            (1, 'project', '/repos/project', 'git fetch', '2026-01-01 00:00:00'),
            (2, 'project-copy', '/repos/project', 'git pull', '2026-01-02 00:00:00');
        INSERT INTO Categories VALUES (1, 'Work'), (2, 'work');
        INSERT INTO RepoCategories (id_repo, id_category) VALUES
            (1, 1),
            (2, 2),
            (999, 999);
    ''')
    connection.commit()
    connection.close()

    migrated = GitRepoController(str(tmp_path))
    try:
        migrated.repoDAO.create_tables()
        migrated.categoryDAO.create_tables()

        assert migrated.conn.execute(
            "SELECT id_repo, repo_path FROM RepoWatcher ORDER BY id_repo"
        ).fetchall() == [(1, "/repos/project")]
        assert migrated.conn.execute('''
            SELECT id_category, category_name
            FROM Categories
            WHERE category_name = 'work' COLLATE NOCASE
        ''').fetchall() == [(1, "Work")]
        assert migrated.conn.execute('''
            SELECT id_repo, id_category
            FROM RepoCategories
            ORDER BY id_repo, id_category
        ''').fetchall() == [(1, 1)]
        assert migrated.conn.execute("PRAGMA foreign_key_check").fetchall() == []

        foreign_keys = migrated.conn.execute(
            "PRAGMA foreign_key_list(RepoCategories)"
        ).fetchall()
        assert len(foreign_keys) == 2
        assert all(row[6] == "CASCADE" for row in foreign_keys)

        migrated.conn.execute("DELETE FROM RepoWatcher WHERE id_repo = 1")
        migrated.conn.commit()
        assert migrated.conn.execute(
            "SELECT COUNT(*) FROM RepoCategories"
        ).fetchone() == (0,)
    finally:
        migrated.conn.close()
