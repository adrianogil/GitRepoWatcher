from repo import Repo
from category import Category

class EntityFactory:
    def create_repo(self,args):
        return Repo(args)
    def create_category(self, name):
        return Category(name)

