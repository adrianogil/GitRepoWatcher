

class RepoDAO:
    def __init__(self, conn, cursor, entityFactory, categoryDAO, accountDAO):
        self.conn = conn
        self.cursor = cursor
        self.entityFactory = entityFactory
        self.categoryDAO = categoryDAO
        self.accountDAO = accountDAO

    def createTables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS RepoWatcher (
                id_repo INTEGER,
                repo_name TEXT,
                repo_path TEXT,
                update_command TEXT,
                operation_time TEXT,
                PRIMARY KEY (id_repo)
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS RepoCategories (
                id_repocategory INTEGER,
                id_repo INTEGER,
                id_category INTEGER,
                FOREIGN KEY (id_repo) REFERENCES RepoWatcher (id_repo)
                FOREIGN KEY (id_category) REFERENCES Categories (id_category)
                PRIMARY KEY (id_repocategory)
                )
        ''')

    def save(self, repo):
        # Save current register
        sql_query_save = "INSERT INTO RepoWatcher (repo_name, repo_path, update_command, operation_time)" + \
                        " VALUES (:repo_name, :repo_path, :update_command, :operation_time)"
        save_data = repo.get_data_tuple()
        print(str(save_data))
        self.cursor.execute(sql_query_save, save_data)
        self.conn.commit()

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

    def delete(self, moneyRegister):
        sql_query_delete = "DELETE FROM FinancialRegisters WHERE id_register=?"
        delete_data = (moneyRegister.id,)
        self.cursor.execute(sql_query_delete, delete_data)
        self.conn.commit()