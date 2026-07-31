import repowatcher.utils as utils
from repowatcher.utils.printlog import printlog


class CategoryDAO:
    DEFAULT_CATEGORY = 'default'

    def __init__(self, conn, cursor, entityFactory):
        self.conn = conn
        self.cursor = cursor
        self.entityFactory = entityFactory
        self.default_category = None
        self.conn.execute("PRAGMA foreign_keys = ON")

    def create_tables(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Categories (
                    id_category INTEGER PRIMARY KEY,
                    category_name TEXT NOT NULL COLLATE NOCASE
                )
            ''')
            self._create_repo_categories_table()
            self._remove_orphaned_repo_categories()
            self._deduplicate_category_names()
            self.cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS
                idx_categories_category_name_unique
                ON Categories (category_name COLLATE NOCASE)
            ''')
            self._migrate_repo_categories_table()

            self.default_category = self.get(CategoryDAO.DEFAULT_CATEGORY)
            if self.default_category is None:
                self.default_category = self.save(
                    CategoryDAO.DEFAULT_CATEGORY,
                    commit=False,
                )
                printlog(
                    'Default Category with id: ' + str(self.default_category.id),
                    debug=True,
                )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def _table_exists(self, table_name):
        self.cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        )
        return self.cursor.fetchone() is not None

    def _create_repo_categories_table(self, table_name="RepoCategories"):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id_repocategory INTEGER PRIMARY KEY,
                id_repo INTEGER NOT NULL,
                id_category INTEGER NOT NULL,
                FOREIGN KEY (id_repo) REFERENCES RepoWatcher (id_repo)
                    ON DELETE CASCADE,
                FOREIGN KEY (id_category) REFERENCES Categories (id_category)
                    ON DELETE CASCADE,
                UNIQUE (id_repo, id_category)
            )
        ''')

    def _remove_orphaned_repo_categories(self):
        self.cursor.execute('''
            DELETE FROM RepoCategories
            WHERE id_repo NOT IN (SELECT id_repo FROM RepoWatcher)
               OR id_category NOT IN (SELECT id_category FROM Categories)
        ''')

    def _deduplicate_category_names(self):
        self.cursor.execute('''
            SELECT LOWER(category_name), MIN(id_category)
            FROM Categories
            WHERE category_name IS NOT NULL
            GROUP BY LOWER(category_name)
            HAVING COUNT(*) > 1
        ''')
        duplicate_names = self.cursor.fetchall()

        for normalized_name, retained_category_id in duplicate_names:
            self.cursor.execute('''
                SELECT id_category
                FROM Categories
                WHERE LOWER(category_name) = ? AND id_category != ?
            ''', (normalized_name, retained_category_id))
            duplicate_category_ids = [row[0] for row in self.cursor.fetchall()]

            for duplicate_category_id in duplicate_category_ids:
                self.cursor.execute('''
                    UPDATE OR IGNORE RepoCategories
                    SET id_category = ?
                    WHERE id_category = ?
                ''', (retained_category_id, duplicate_category_id))
                self.cursor.execute(
                    "DELETE FROM RepoCategories WHERE id_category = ?",
                    (duplicate_category_id,),
                )
                self.cursor.execute(
                    "DELETE FROM Categories WHERE id_category = ?",
                    (duplicate_category_id,),
                )

    def _repo_categories_requires_migration(self):
        foreign_keys = self.cursor.execute(
            "PRAGMA foreign_key_list(RepoCategories)"
        ).fetchall()
        cascades = [row for row in foreign_keys if row[6].upper() == "CASCADE"]

        table_info = self.cursor.execute(
            "PRAGMA table_info(RepoCategories)"
        ).fetchall()
        required_columns_are_not_null = all(
            row[3] == 1
            for row in table_info
            if row[1] in ("id_repo", "id_category")
        )

        has_unique_pair = False
        for index_row in self.cursor.execute(
            "PRAGMA index_list(RepoCategories)"
        ).fetchall():
            if index_row[2] != 1:
                continue
            index_columns = [
                row[2]
                for row in self.cursor.execute(
                    f"PRAGMA index_info('{index_row[1]}')"
                ).fetchall()
            ]
            if index_columns == ["id_repo", "id_category"]:
                has_unique_pair = True
                break

        return (
            len(foreign_keys) != 2
            or len(cascades) != 2
            or not required_columns_are_not_null
            or not has_unique_pair
        )

    def _migrate_repo_categories_table(self):
        if not self._repo_categories_requires_migration():
            return

        self.cursor.execute("DROP TABLE IF EXISTS RepoCategories_new")
        self._create_repo_categories_table("RepoCategories_new")
        self.cursor.execute('''
            INSERT OR IGNORE INTO RepoCategories_new (id_repo, id_category)
            SELECT rc.id_repo, rc.id_category
            FROM RepoCategories AS rc
            INNER JOIN RepoWatcher AS repo ON repo.id_repo = rc.id_repo
            INNER JOIN Categories AS category
                ON category.id_category = rc.id_category
        ''')
        self.cursor.execute("DROP TABLE RepoCategories")
        self.cursor.execute(
            "ALTER TABLE RepoCategories_new RENAME TO RepoCategories"
        )

    def get(self, value):

        if utils.is_int(value):
            category_id = int(value)
            category_condition = "id_category LIKE ?"

            category_data = (category_id,)
        else:
            category_name = value
            category_condition = "category_name LIKE ?"

            category_data = (category_name,)

        sql_query_get = "SELECT * from Categories WHERE " + category_condition

        self.cursor.execute(sql_query_get, category_data)
        row = self.cursor.fetchone()
        if row is None:
            return None
        category = self.entityFactory.create_category(row[1])
        category.id = int(row[0])

        return category

    def get_all(self):
        sql_query_get = "SELECT * from Categories ORDER BY id_category"
        self.cursor.execute(sql_query_get)
        category_list = []
        for row in self.cursor:
            category = self.entityFactory.create_category(row[1])
            category.id = int(row[0])

            category_list.append(category)

        return category_list

    def get_all_from(self, repo):
        sql_query_get_all = "SELECT * FROM Categories " + \
            "WHERE id_category IN (SELECT id_category FROM RepoCategories WHERE id_repo LIKE ?)"
        sql_query_data = (repo.id,)

        self.cursor.execute(sql_query_get_all, sql_query_data)
        rows = self.cursor.fetchall()

        category_list = []

        for row in rows:
            category = self.entityFactory.create_category(row[1])
            category.id = int(row[0])

            category_list.append(category)

        return category_list

    def save(self, name, commit=True):
        printlog('categorydao - save - ' + name, debug=True)
        sql_query_save = "INSERT OR IGNORE INTO Categories (category_name)" + \
                        " VALUES (?)"
        save_data = (name, )

        try:
            self.cursor.execute(sql_query_save, save_data)
            saved_category = self.get(name)
            if commit:
                self.conn.commit()
            return saved_category
        except Exception:
            if commit:
                self.conn.rollback()
            raise

    def update_from(self, repo, commit=True):
        if repo is None:
            return

        try:
            self.remove_all_categories_from(repo, commit=False)
            if repo.categories is not None:
                printlog(repo.categories, debug=True)
                for category in repo.categories:
                    self.save_repo_category(repo, category, commit=False)
            if commit:
                self.conn.commit()
        except Exception:
            if commit:
                self.conn.rollback()
            raise

    def save_repo_category(self, repo, category, commit=True):
        printlog('save_repo_category - repo - ' + str(repo.id) + ' - category - ' + str(category.id), debug=True)
        sql_query_save = "INSERT OR IGNORE INTO RepoCategories (id_repo, id_category)" + \
                        " VALUES (?, ?)"
        save_data = (repo.id, category.id)

        try:
            self.cursor.execute(sql_query_save, save_data)
            if commit:
                self.conn.commit()
        except Exception:
            if commit:
                self.conn.rollback()
            raise

    def remove_all_categories_from(self, repo, commit=True):
        sql_query_delete = "DELETE FROM RepoCategories WHERE id_repo = ?"
        delete_data = (repo.id,)

        try:
            self.cursor.execute(sql_query_delete, delete_data)
            if commit:
                self.conn.commit()
        except Exception:
            if commit:
                self.conn.rollback()
            raise

    def updateCategory(self, category):
        sql_query_update = "UPDATE Categories SET category_name = ? WHERE id_category = ?"
        update_data = (category.name, category.id)
        try:
            self.cursor.execute(sql_query_update, update_data)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def delete(self, category):
        sql_query_delete = "DELETE FROM Categories WHERE id_category = ?"
        delete_data = (category.id,)
        try:
            self.cursor.execute(sql_query_delete, delete_data)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
