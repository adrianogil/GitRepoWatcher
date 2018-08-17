import datetime

class Repo:
    def __init__(self, args):
        self.id = -1
        if 'amount' in args:
            self.amount = args['amount']
        else:
            self.amount = 0

        if 'description' in args:
            self.description = args['description']
        else:
            self.description = ""

        if 'register_dt' in args:
            self.register_dt = args['register_dt']
        else:
            self.register_dt = datetime.datetime.now()

        if 'category' in args:
            self.category = args['category']

        if 'account' in args:
            self.account = args['account']

    def __str__(self):
        return "(ID: " + str(self.id) + \
                 ', repo: ' + self.repo_name + \
                 ', path: ' + str(self.repo_path) + \
                 ', update_command: ' + self.update_command + ')'


    def get_register_dt(self):
        return datetime.strftime("%Y-%m-%d %H:%M:%S")

    def get_data_tuple(self, add_timestamp=False):
        data_tuple = (self.repo_name, \
                     self.repo_path, \
                     self.update_command)
        if add_timestamp:
            data_tuple = data_tuple + (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
        return data_tuple



