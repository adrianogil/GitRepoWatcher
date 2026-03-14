from .userinput import get_user_input
from .decorators import debug
from .base import set_class_attribute

import sys


flags = {
}


def set_properties_from_flags(class_object):
    if get_flag("--help"):
        print("Current available flags:")
        for property_name in class_object.class_properties:
            print("--" + property_name)
        exit(0)
    for property_name in class_object.class_properties:
        if verify_flag("--" + property_name):
            set_class_attribute(class_object, "_" + property_name, get_flag("--" + property_name))


def get_parsed_flags():
    '''
        return parsed flags as a dictionary
    '''
    import repowatcher.utils.datautils as datautils
    args = {}

    last_key = ''

    for i in range(1, len(sys.argv)):
        a = sys.argv[i]
        if a[0] == '-' and not datautils.is_float(a):
            last_key = a
            args[a] = []
        elif last_key != '':
            arg_values = args[last_key]
            arg_values.append(a)
            args[last_key] = arg_values

    return args


def process_args(flags_list=None):
    '''
        process current flags
        adds to internal storing system
    '''
    if flags_list is None:
        flags_list = sys.argv[1:]

    current_flag = ""
    current_values = []

    def add_flag(flag, value):
        if flag != "":
            flags[flag] = value

    for f in flags_list:
        if f.startswith('-') and (len(f) > 1 and not f[1].isdigit()):
            add_flag(current_flag, current_values)
            current_flag = f
            current_values = []
        else:
            current_values.append(f)
    add_flag(current_flag, current_values)

    return flags


def verify_flag(flag_name: str) -> bool:
    """
    Verify if a given flag exists in the flags dictionary.

    :param flag_name: The name of the flag to verify.
    :return: True if the flag exists, False otherwise.
    """
    if not flags:
        process_args()  # Assumes process_args() populates the 'flags' dictionary

    if flag_name.__class__ == list:
        flag_list = flag_name

        for f in flag_list:
            if f in flags:
                return True
    else:
        return flag_name in flags

    return False

def get_flag(flag_name, default_value=None, prompt_label: str = None, options=None, result_type=None, always_prompt=False, eval_input=False):
    """
    Get the value of a flag from a dictionary, with an option to prompt for the value.

    :param flag_name: The name of the flag to retrieve.
    :param default_value: Default value if the flag is not found.
    :param prompt_label: Label for the prompt if the flag value needs to be inputted.
    :param options: List of options to be presented to the user
    :param result_type: Type of the result to be returned.
    :return: The value of the flag or the default value.
    """

    if not flags:
        process_args()  # Assumes process_args() populates 'flags'

    flag_value = None

    if flag_name.__class__ == list:
        flag_list = flag_name
        flag_name = flag_list[0]

        for f in flag_list:
            if f in flags:
                flag_name = f
                break
    if not flag_value and flag_name in flags:
        flag_value = flags[flag_name]
    elif prompt_label:
        flag_value = get_user_input(
            prompt_label,
            options=options,
            default_value=default_value,
            cast_type=result_type,
            eval_input=eval_input)
        if not always_prompt:
            flags[flag_name] = flag_value
    else:
        flag_value = default_value

    if isinstance(flag_value, list) and len(flag_value) == 1:
        flag_value = flag_value[0]

    if result_type:
        flag_value = result_type(flag_value)

    return flag_value


def get_all_flags(exception_list=None, remove_dash=False):
    """
    Get all flags from the flags dictionary.
    """
    if not flags:
        process_args()  # Assumes process_args() populates 'flags'

    if exception_list:
        user_flags = {k: v for k, v in flags.items() if k not in exception_list}
    else:
        import copy
        user_flags = copy.deepcopy(flags)

    if remove_dash:
        user_flags = {k.replace("--", ""): v for k, v in user_flags.items()}

    return user_flags
