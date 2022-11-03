# Define a log method
debug_mode = False


def printlog(msg, debug=False):
    if debug:
        msg = "debug: " + msg

    if not debug or debug_mode:
        print(msg)
