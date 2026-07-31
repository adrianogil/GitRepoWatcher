from repowatcher.utils.printlog import printlog


class RepoDAO:
    def __init__(self, conn, cursor, entity_factory, categoryDAO):
        self.conn = conn
        self.cursor = cursor
        self.entity_factory = entity_factory
        self.categoryDAO = categoryDAO
        self.conn.execute("PRAGMA foreign_keys = ON")

    def create_tables(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS RepoWatcher (
                    id_repo INTEGER PRIMARY KEY,
                    repo_name TEXT NOT NULL,
                    repo_path TEXT NOT NULL,
                    update_command TEXT NOT NULL,
                    operation_time TEXT NOT NULL
                )
            ''')
            self._remove_orphaned_repo_categories()
            self._deduplicate_repo_paths()
            self.cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS
                idx_repowatcher_repo_path_unique
                ON RepoWatcher (repo_path)
            ''')
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

    def _remove_orphaned_repo_categories(self):
        if not self._table_exists("RepoCategories"):
            return

        self.cursor.execute('''
            DELETE FROM RepoCategories
            WHERE id_repo NOT IN (SELECT id_repo FROM RepoWatcher)
        ''')

    def _deduplicate_repo_paths(self):
        self.cursor.execute('''
            SELECT repo_path, MIN(id_repo)
            FROM RepoWatcher
            WHERE repo_path IS NOT NULL
            GROUP BY repo_path
            HAVING COUNT(*) > 1
        ''')
        duplicate_paths = self.cursor.fetchall()
        has_repo_categories = self._table_exists("RepoCategories")

        for repo_path, retained_repo_id in duplicate_paths:
            self.cursor.execute(
                "SELECT id_repo FROM RepoWatcher WHERE repo_path = ? AND id_repo != ?",
                (repo_path, retained_repo_id),
            )
            duplicate_repo_ids = [row[0] for row in self.cursor.fetchall()]

            for duplicate_repo_id in duplicate_repo_ids:
                if has_repo_categories:
                    self.cursor.execute(
                        "UPDATE OR IGNORE RepoCategories SET id_repo = ? WHERE id_repo = ?",
                        (retained_repo_id, duplicate_repo_id),
                    )
                    self.cursor.execute(
                        "DELETE FROM RepoCategories WHERE id_repo = ?",
                        (duplicate_repo_id,),
                    )
                self.cursor.execute(
                    "DELETE FROM RepoWatcher WHERE id_repo = ?",
                    (duplicate_repo_id,),
                )

    def save(self, repo):
        sql_query_save = "INSERT INTO RepoWatcher " + \
                            "(repo_name, repo_path, update_command, operation_time)" + \
                            " VALUES (?, ?, ?, ?)"
        save_data = repo.get_data_tuple(True)
        printlog("repodao - save - " + str(save_data), debug=True)
        original_repo_id = repo.id

        try:
            self.cursor.execute(sql_query_save, save_data)
            repo.id = self.cursor.lastrowid
            self.categoryDAO.update_from(repo, commit=False)
            self.conn.commit()
            return repo
        except Exception:
            self.conn.rollback()
            repo.id = original_repo_id
            raise

    def add_condition(self, query_conditions, condition, add_mode=' ADD '):
        if query_conditions == '':
            return condition
        else:
            return query_conditions + add_mode + condition

    def build_query_condition(self, conditions, add_mode=' ADD '):
        query_conditions = ""
        conditions_data = ()

        if 'id' in conditions:
            id_conditions = "id_repo LIKE ?"
            query_conditions = self.add_condition(query_conditions, id_conditions, add_mode)
            conditions_data = conditions_data + (conditions['id'],)

        if 'path' in conditions:
            path_conditions = "repo_path LIKE ?"
            query_conditions = self.add_condition(query_conditions, path_conditions, add_mode)
            conditions_data = conditions_data + (conditions['path'],)

        if 'update_command' in conditions:
            command_conditions = "update_command LIKE ?"
            query_conditions = self.add_condition(query_conditions, command_conditions, add_mode)
            conditions_data = conditions_data + (conditions['update_command'],)

        return (query_conditions, conditions_data)


    def contains_categories(self, repo, target_categories):
        for c in target_categories:
            for rc in repo.categories:
                if c == rc.name:
                    return True
        return False

    def get_all(self, conditions=None):
        if conditions is None:
            conditions = []

        sql_query_get_all = "SELECT * FROM RepoWatcher"
        if len(conditions) == 0:
            self.cursor.execute(sql_query_get_all)
        else:
            query_conditions, conditions_data = self.build_query_condition(conditions, ' OR ')
            # print('DEBUG: repodao - get_all - ' + query_conditions)
            if len(query_conditions) > 0:
                sql_query_get_all = sql_query_get_all + " WHERE " + query_conditions
            sql_query_get_all = sql_query_get_all + " ORDER BY id_repo"
            self.cursor.execute(sql_query_get_all, conditions_data)

        rows = self.cursor.fetchall()

        repo_list = []

        for row in rows:
            # print('DEBUG: repodao - get_all - ' + row[1])
            repo = self.parse_repo_from_row(row)
            repo.categories = self.categoryDAO.get_all_from(repo)

            if 'categories' in conditions:
                target_categories = conditions['categories']
                if self.contains_categories(repo, target_categories):
                    repo_list.append(repo)
            else:
                repo_list.append(repo)

        return repo_list


    def get_from_time(self, operation_time):
        sql_query_load_id = "SELECT * FROM RepoWatcher WHERE operation_time = ?"
        self.cursor.execute(sql_query_load_id, (operation_time,))

        row = self.cursor.fetchone()
        if row is None:
            return None
        repo = self.parse_repo_from_row(row)

        return repo

    def reload(self, repo):
        sql_query_load_id = "SELECT * FROM RepoWatcher " + \
                        " WHERE operation_time = ? " + \
                        " AND repo_path LIKE ? "
        self.cursor.execute(sql_query_load_id, (repo.get_register_dt(), repo.path))

        row = self.cursor.fetchone()
        if row is None:
            return None
        repo = self.parse_repo_from_row(row)

        return repo

    def convert_to_str(self, str_value):
        try:
            str_value = str_value.decode('utf-8')
        except Exception as _:
            str_value = str(str_value)

        return str_value

    def parse_repo_from_row(self, row):
        repo_args = {
            "id"             : int(row[0]),
            "name"           : self.convert_to_str(row[1]),
            "path"           : self.convert_to_str(row[2]),
            "update_command" : self.convert_to_str(row[3]),
        }

        repo = self.entity_factory.create_repo(repo_args)
        return repo

    def update(self, repo):
        sql_query_update = "UPDATE RepoWatcher SET " + \
                            " repo_name = ?, " + \
                            " repo_path = ?, " + \
                            " update_command = ?, " + \
                            " operation_time = ? " + \
                            " WHERE id_repo = ? "
        update_data = repo.get_data_tuple(True) + (repo.id,)
        printlog("repodao - save - " + str(update_data), debug=True)

        try:
            self.cursor.execute(sql_query_update, update_data)
            self.categoryDAO.update_from(repo, commit=False)
            self.conn.commit()
            return repo
        except Exception:
            self.conn.rollback()
            raise

    def delete(self, repo):
        sql_query_delete = "DELETE FROM RepoWatcher WHERE id_repo=? "
        delete_data = (repo.id,)
        try:
            self.cursor.execute(sql_query_delete, delete_data)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
