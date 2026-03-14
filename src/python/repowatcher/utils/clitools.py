from repowatcher.utils.decorators import trycatch

import subprocess
import psutil
import time
import os


@trycatch
def run_cmd(cmd, terminal_executable=None, return_stderr=False, load_bashrc=False, live_log=False, encoding="ISO-8859-1"):
    ibash_exe = "/usr/local/bin/interactive_bash"

    if cmd:
        subprocess_cmd = cmd

    args = {"shell": True}

    if terminal_executable is not None:
        args["executable"] = terminal_executable
    elif load_bashrc:
        if os.path.exists(ibash_exe):
            args["executable"] = ibash_exe
    if return_stderr:
        args["stderr"] = subprocess.STDOUT
        args["universal_newlines"] = True
        args["timeout"] = 3

    if not live_log:
        subprocess_output = subprocess.check_output(subprocess_cmd, **args)
        subprocess_output = subprocess_output.decode(encoding)
        subprocess_output = subprocess_output.strip()
    else:
        subprocess_output = ''

        if cmd.__class__ == str:
            subprocess_cmd = subprocess_cmd.split(' ')

        process = subprocess.Popen(subprocess_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **args)
        while True:
            output = None

            try:
                output = process.stdout.readline()
            except Exception as exception:
                output = None

            if output is None or (output == b'' and process.poll() is not None):
                break
            if output:
                out = output.decode(encoding)
                subprocess_output += out + '\n'
                print(out, end="")

    return subprocess_output


def sizeof_fmt(num, suffix='B'):
    """
        Returns human readable byte
        https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_memory_usage(pid, human_format=True):
    process = psutil.Process(pid)
    memory_value_bytes = process.memory_info().rss
    if human_format:
        memory_value_human_read = sizeof_fmt(memory_value_bytes)
        memory_usage = memory_value_human_read
    else:
        memory_usage = memory_value_bytes

    return memory_usage


def perf_run_cmd(cmd, terminal_executable=None, return_stderr=False, load_bashrc=True, live_log=True):
    start_time = time.perf_counter()    # 1

    ibash_exe = "/usr/local/bin/interactive_bash"

    if cmd:
        subprocess_cmd = cmd

    args = {"shell": True}

    if terminal_executable is not None:
        args["executable"] = terminal_executable
    elif load_bashrc:
        if os.path.exists(ibash_exe):
            args["executable"] = ibash_exe
    if return_stderr:
        args["stderr"] = subprocess.STDOUT
        args["universal_newlines"] = True
        args["timeout"] = 3

    subprocess_output = ''

    if cmd.__class__ == str:
        subprocess_cmd = subprocess_cmd.split(' ')

    process = subprocess.Popen(subprocess_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = None

        try:
            print("Memory usage: ", get_memory_usage(process.pid))
            output = process.stdout.readline()
        except Exception as exception:
            output = None

        if output is None or (output == b'' and process.poll() is not None):
            break
        if output:
            out = output.decode("ISO-8859-1")
            subprocess_output += out + '\n'
            if live_log:
                print(out, end="")
    if not live_log:
        print(subprocess_output)
    end_time = time.perf_counter()      # 2
    run_time = end_time - start_time    # 3
    print(f"Command executed in {run_time} seconds")

    return subprocess_output
