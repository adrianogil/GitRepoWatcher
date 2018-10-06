
class RepoDAO:
    def __init__(self, conn, cursor, entity_factory, categoryDAO):
        self.conn = conn
        self.cursor = cursor
        self.entity_factory = entity_factory
        self.categoryDAO = categoryDAO

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS RepoWatcher (
                id_repo INTEGER,
                repo_name TEXT,
                repo_path TEXT,
                update_command TEXT,
                operation_time TEXT,
                PRIMARY KEY (id_repo)
            )
        ''')

    def save(self, repo):
        # Save current register
        sql_query_save = "INSERT INTO RepoWatcher " + \
                            "(repo_name, repo_path, update_command, operation_time)" + \
                            " VALUES (:repo_name, :repo_path, :update_command, :operation_time)"
        save_data = repo.get_data_tuple(True)
        print("DEBUG: repodao - save - " + str(save_data))
        self.cursor.execute(sql_query_save, save_data)
        self.conn.commit()

        repo_obj = self.get_from_time(save_data[3])
        repo.id = repo_obj.id

        self.categoryDAO.update_from(repo)

        return repo

    def add_condition(self, query_conditions, condition):
        if query_conditions == '':
            return condition
        else:
            return query_conditions + ' ADD ' + condition

    def build_query_condition(self, conditions):
        query_conditions = ""
        conditions_data = ()

        if 'id' in conditions:
            id_conditions = "id_repo LIKE ?"
            query_conditions = self.add_condition(query_conditions, id_conditions)
            conditions_data = conditions_data + (conditions['id'],)

        if 'path' in conditions:
            path_conditions = "repo_path LIKE ?"
            query_conditions = self.add_condition(query_conditions, path_conditions)
            conditions_data = conditions_data + (conditions['path'],)

        if 'update_command' in conditions:
            command_conditions = "update_command LIKE ?"
            query_conditions = self.add_condition(query_conditions, command_conditions)
            conditions_data = conditions_data + (conditions['update_command'],)

        return (query_conditions, conditions_data)


    def get_all(self, conditions=[]):

        sql_query_get_all = "SELECT * FROM RepoWatcher"
        if len(conditions) == 0:
            self.cursor.execute(sql_query_get_all)
        else:
            query_conditions, conditions_data = self.build_query_condition(conditions)
            # print('DEBUG: repodao - get_all - ' + query_conditions)
            sql_query_get_all = sql_query_get_all + " WHERE " + query_conditions
            self.cursor.execute(sql_query_get_all, conditions_data)

        rows = self.cursor.fetchall()

        repo_list = []

        for row in rows:
            # print('DEBUG: repodao - get_all - ' + row[1])
            repo = self.parse_repo_from_row(row)
            repo.categories = self.categoryDAO.get_all_from(repo)
            repo_list.append(repo)

        return repo_list


    def get_from_time(self, operation_time):
        sql_query_load_id = "SELECT * FROM RepoWatcher WHERE operation_time = ?"
        self.cursor.execute(sql_query_load_id, (operation_time,))
        self.conn.commit()

        row = self.cursor.fetchone()
        if row is None:
            return None
        repo = self.parse_repo_from_row(row)

        return repo


    def parse_repo_from_row(self, row):
        repo_args = {
            "id"             : int(row[0]),
            "name"           : row[1],
            "path"           : row[2],
            "update_command" : row[3],
        }

        repo = self.entity_factory.create_repo(repo_args)
        return repo

    def update(self, moneyRegister):
        sql_query_update = "UPDATE FinancialRegisters SET description = ?," + \
                                                             " amount = ?," + \
                                                        " register_dt = ?," + \
                                                        " id_category = ?, " + \
                                                        " id_account = ? " + \
                                              " WHERE id_register = ?"
        update_data = moneyRegister.get_data_tuple() + (moneyRegister.id,)
        self.cursor.execute(sql_query_update, update_data)
        self.conn.commit()

    def delete(self, repo):
        sql_query_delete = "DELETE FROM RepoWatcher WHERE id_repo=?"
        delete_data = (repo.id,)
        self.cursor.execute(sql_query_delete, delete_data)
        self.conn.commit()