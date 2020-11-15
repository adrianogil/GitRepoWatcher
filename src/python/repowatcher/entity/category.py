from pyutils.code.classproperties import declare_props


class Category:
    def __init__(self, name='Category'):
        declare_props(
            self,
            props={
                'id': {
                    'prop_type': int,
                    'default_value': -1
                },
                'name': {
                    'prop_type': str,
                    'default_value': name
                }
            }
        )
