# Define a log method
debug_mode = False


def printlog(msg, debug=False):
    if debug and debug_mode:
        print("debug: ", msg)

    if not debug:
        print(msg)
