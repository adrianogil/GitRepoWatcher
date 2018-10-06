
import utils

class CategoryDAO:
    DEFAULT_CATEGORY = 'default'

    def __init__(self, conn, cursor, entityFactory):
        self.conn = conn
        self.cursor = cursor
        self.entityFactory = entityFactory
        self.default_category = None

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Categories (
                id_category INTEGER,
                category_name TEXT,
                PRIMARY KEY (id_category)
            )
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
        self.default_category = self.get(CategoryDAO.DEFAULT_CATEGORY)
        if self.default_category is None:
            self.default_category = self.save(CategoryDAO.DEFAULT_CATEGORY)
            print('Default Category with id: ' + str(self.default_category.id))

    def get(self, value):

        if utils.is_int(value):
            category_id = int(value)
            category_condition = "id_category LIKE ?"

            category_data = (category_id,)
        else:
            category_name = value
            category_condition = "category_name LIKE ?"

            category_data = (category_name,)

        # print('DEBUG: categoryDAO - trying to get category from name: ' + name)
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
            category = self.entityFactory.createCategory(row[1])
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

    def save(self, name):
        print('debug: categorydao - save - ' + name)
        sql_query_save = "INSERT INTO Categories (category_name)" + \
                        " VALUES (:category_name)"
        save_data = (name, )
        self.cursor.execute(sql_query_save, save_data)
        self.conn.commit()

        saved_category = self.get(name)

        return saved_category

    def update_from(self, repo):
        self.remove_all_categories_from(repo)
        if repo is None or repo.categories is None:
            return
        print(repo.categories)
        for c in repo.categories:
            self.save_repo_category(repo, c)

    def save_repo_category(self, repo, category):
        sql_query_save = "INSERT INTO RepoCategories (id_repo, id_category)" + \
                        " VALUES (:id_repo, :id_category)"
        save_data = (repo.id, category.id)
        self.cursor.execute(sql_query_save, save_data)
        self.conn.commit()

    def remove_all_categories_from(self, repo):
        sql_query_delete = "DELETE FROM RepoCategories WHERE id_repo = ?"
        delete_data = (repo.id,)
        self.cursor.execute(sql_query_delete, delete_data)
        self.conn.commit()

    def updateCategory(self, category):
        sql_query_update = "UPDATE Categories SET category_name = ? WHERE id_category = ?"
        update_data = (category.name, category.id)
        self.cursor.execute(sql_query_update, update_data)
        self.conn.commit()

    def delete(self, category):
        sql_query_delete = "DELETE FROM Categories WHERE id_category = ?"
        delete_data = (category.id,)
        self.cursor.execute(sql_query_delete, delete_data)
        self.conn.commit()

