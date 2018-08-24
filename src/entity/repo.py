import datetime

class Repo:
    def __init__(self, args):
        
        if 'id' in args:
            self.id = int(args['id'])
        else:
            self.id = -1
            
        if 'name' in args:
            self.name = args['name']
        else:
            self.name = ""

        if 'path' in args:
            self.path = args['path']
        else:
            self.path = ""

        if 'categories' in args:
            self.categories = args['categories']
        else:
            self.categories = []

        if 'update_command' in args:
            self.update_command = args['update_command']
        else:
            self.update_command = ""

    def __str__(self):
        return "(ID: " + str(self.id) + \
                 ', repo: ' + self.repo_name + \
                 ', path: ' + str(self.repo_path) + \
                 ', update_command: ' + self.update_command + ')'


    def get_register_dt(self):
        return datetime.strftime("%Y-%m-%d %H:%M:%S")

    def get_data_tuple(self, add_timestamp=False):
        data_tuple = (self.name, \
                     self.path, \
                     self.update_command)
        if add_timestamp:
            data_tuple = data_tuple + (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
        return data_tuple



