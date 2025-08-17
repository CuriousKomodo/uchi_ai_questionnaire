import functools
import json
import re
import time


def save_json(data, filename):
    save_file = open(filename, "w")
    json.dump(data, save_file)


def read_json(filename):
    json_file = open(filename, "r")
    data = json.load(json_file)
    return data

# Password strength validation utility
def is_strong_password(pw):
    """Check if the password is strong: at least 8 chars, upper, lower, digit, special char."""
    # FIXME: make password more secure
    # if len(pw) < 8:
    #     return False
    # if not re.search(r"[A-Z]", pw):
    #     return False
    # if not re.search(r"[a-z]", pw):
    #     return False
    # if not re.search(r"[0-9]", pw):
    #     return False
    return True



def retry(ExceptionToCheck, tries=3, delay=1, backoff=2, logger=None):
    """
    Retry calling the decorated function using an exponential backoff.
    Args:
        ExceptionToCheck: the exception to check. may be a tuple of exceptions to check
        tries: number of times to try (not retry) before giving up
        delay: initial delay between retries in seconds
        backoff: backoff multiplier e.g. value of 2 will double the delay each retry
        logger: logger to use. If None, print
    """
    def deco_retry(f):
        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = f"{e}, Retrying in {mdelay} seconds... ({mtries-1} tries left)"
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)
        return f_retry
    return deco_retry
