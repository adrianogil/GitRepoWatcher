import functools
import time


def debug(func):
    """
        Print the function signature and return value
    """
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]                      # 1
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]  # 2
        signature = ", ".join(args_repr + kwargs_repr)           # 3
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")           # 4
        return value
    return wrapper_debug


def timer(func):
    """
        Print the runtime of the decorated function
    """
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

def sleep(_func=None, *, sleep_time=1):
    """
    A decorator that adds a delay before calling the decorated function.

    Args:
        _func (function, optional): The function to be decorated. Defaults to None.
        sleep_time (int, optional): The amount of time to sleep in seconds. Defaults to 1.

    Returns:
        function: The decorated function.

    Example:
        @sleep(sleep_time=2)
        def my_function():
            print("Hello, world!")

        my_function()  # Will print "Hello, world!" after a 2-second delay.
    """
    def decorator_sleep(func):
        @functools.wraps(func)
        def wrapper_slow_down(*args, **kwargs):
            time.sleep(sleep_time)
            return func(*args, **kwargs)
        return wrapper_slow_down

    if _func is None:
        return decorator_sleep
    else:
        return decorator_sleep(_func)


def trycatch(_func=None, *, error_callback=None, error_message=None, stacktrace=True):
    """
        trycatch(_func=None, *, error_callback=None, error_message=None, stacktrace=True)
            Decorator to handle errors using a callback function or show a message
    """
    def decorator_handle_errors(func):
        @functools.wraps(func)
        def wrapper_handle_errors(*args, **kwargs):
            nonlocal error_callback

            func_output = None

            if "error_callback" in kwargs:
                error_callback = kwargs["error_callback"]
                kwargs.pop("error_callback")

            from .flags import verify_flag
            if verify_flag('--deactivate-error-handling'):
                func_output = func(*args, **kwargs)
                return func_output

            try:
                func_output = func(*args, **kwargs)
            except Exception as exception:
                if error_message is not None:
                    print(error_message)
                if stacktrace:
                    print("Error when executing %s" % (func,))
                    print("Stacktrace: %s" % (exception,))
                try:
                    if error_callback is not None:
                        error_callback()
                except Exception as exception2:
                    if error_message is not None:
                        print(error_message)
                    if stacktrace:
                        print("Stacktrace: %s" % (exception,))

            return func_output
        return wrapper_handle_errors

    if _func is None:
        return decorator_handle_errors
    else:
        return decorator_handle_errors(_func)


class InstanceObserver:
    def __init__(self):
        self._instances = {}
        self.total_created = 0
        self.total_live = 0

    def on_instance_created(self, obj):
        self.total_created += 1
        self.total_live += 1

        obj.instance_name = "Instance_" + str(self.total_created)

        print("Created object: %s [Total: %s/%s]" %
              (obj, self.total_live, self.total_created))
        self._instances[obj.instance_name] = obj

    def on_instance_destroyed(self, obj):
        self.total_live -= 1

        print("Destroyed object: %s [Total: %s/%s]" %
              (obj, self.total_live, self.total_created))
        self._instances[obj.instance_name] = None


instance_observer = InstanceObserver()


class ObservableInstance:
    def __init__(self):
        self.instance_name = "New_Instance"
        instance_observer.on_instance_created(self)

    def __del__(self):
        instance_observer.on_instance_destroyed(self)


def manage_instance(class_func):
    """Manage instances created"""
    @functools.wraps(class_func)
    def wrapper_instance_creation(*args, **kwargs):
        new_obj = class_func(*args, **kwargs)
        instance_observer.on_instance_created(new_obj)

        old_del = None

        if hasattr(new_obj, "__del__"):
            old_del = new_obj.__del__

        def wrapper_del(obj):
            instance_observer.on_instance_destroyed(obj)
            if old_del is not None:
                old_del()

        new_obj.__del__ = wrapper_del

        return new_obj

    return wrapper_instance_creation


class CallCount:
    def __init__(self, f):
        self.f = f
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        self.f(*args, **kwargs)


class Tracer:
    def __init__(self):
        self.enabled = False

    def __call__(self, f):
        def wrap(*args, **kwargs):
            if self.enabled:
                print("Calling {}".format(f))
            return f(*args, **kwargs)
        return wrap
