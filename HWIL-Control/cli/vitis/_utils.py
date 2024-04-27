import sys

interactive = False

# Exception types - only predefined types are supported
# Add more types as needed
exception_dict = {
    'BaseException': BaseException,
    'Exception': Exception,
    'ArithmeticError': ArithmeticError,
    'BufferError': BufferError,
    'LookupError': LookupError,
    'AssertionError': AssertionError,
    'AttributeError': AttributeError,
    'EOFError': EOFError,
    'FloatingPointError': FloatingPointError,
    'KeyError': KeyError,
    'ValueError': ValueError
}

def exception(msg, ex = None, ex_type = 'Exception'):
    if (ex != None):
        # Get the type from previous exception when available
        ex_type = str(type(ex).__name__)
        if ex_type in exception_dict:
            raise exception_dict[ex_type](f"'{msg}', " + str(ex)) from None
        else:
            raise Exception(f"'{msg}', " + str(ex)) from None
    else:
        raise exception_dict[ex_type](f"'{msg}'") from None

def grpc_exception(msg, ex):
    exception(msg=f"{msg}, status = {str(ex.code())},\n\
                \r            details = '{ex.details()}'")

# Unused
def set_interactive():
    # sys.tracebacklimit = 0
    global interactive
    interactive = True

# Unused
def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    global interactive
    # if sys.flags.interactive:
    # if (hasattr(main, '__file__') == True):
    if (interactive == False):
        debug_hook(exception_type, exception, traceback)
    else:
        print(f"'{exception_type.__name__}': '{exception}'")
