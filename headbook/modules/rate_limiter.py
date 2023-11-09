# Example usage:
# _convert_time("1.5s") = 1.5
# _convert_time("2m") = 120
# _convert_time("1h") = 3600
# _convert_time("1d") = 86400


def _convert_time(time_string):
    # if time_string is a number or string that can be converted to a number
    if isinstance(time_string, (int, float)):
        return float(time_string)

    try:
        time_string = float(time_string)
        return time_string
    except ValueError:
        pass

    try:
        float(time_string[:-1])
    except ValueError:
        raise ValueError("Invalid time string")

    if time_string[-1] not in ["s", "m", "h", "d", "w"]:
        raise ValueError("Invalid time annotation")
    # If the time string ends with an s
    if time_string.endswith("s"):
        # Return the time string converted to a float
        return float(time_string[:-1])
    # If the time string ends with an m
    elif time_string.endswith("m"):
        # Return the time string converted to a float times 60
        return float(time_string[:-1]) * 60
    # If the time string ends with an h
    elif time_string.endswith("h"):
        # Return the time string converted to a float times 3600
        return float(time_string[:-1]) * 3600
    # If the time string ends with a d
    elif time_string.endswith("d"):
        # Return the time string converted to a float times 86400
        return float(time_string[:-1]) * 86400
    # If the time string ends with a w
    elif time_string.endswith("w"):
        # Return the time string converted to a float times 604800
        return float(time_string[:-1]) * 604800
    # Otherwise
    else:
        raise ValueError("Invalid time string")


# This is a decorator that limits the number of requests per period.
# @Param: func - the function to be decorated
# @Param: limit - the number of requests allowed per period
# @Param: period - the period of time in seconds
# @Return: wrapped - the decorated function
# @SideEffects: aborts with 429 if the number of requests exceeds the limit


def rate_limiter(limit, period):
    def decorator(func):
        from flask import abort
        from time import time
        from headbook.app import app

        g = app.app_context().g

        def wrapped(*args, **kwargs):
            if not hasattr(g, "rate_limit"):
                g.rate_limit = {}
            # If the function is not in the rate limit dictionary
            if func.__name__ not in g.rate_limit:
                # Set the function in the rate limit dictionary to a list
                g.rate_limit[func.__name__] = {
                    "start": time(),
                    "count": 0,
                }
            # If the number of requests exceeds the limit
            if time() - g.rate_limit[func.__name__]["start"] > _convert_time(period):
                # Reset the start time and count
                g.rate_limit[func.__name__]["start"] = time()
                g.rate_limit[func.__name__]["count"] = 0
            # If the number of requests does not exceed the limit
            if g.rate_limit[func.__name__]["count"] < limit:
                # Increment the count
                g.rate_limit[func.__name__]["count"] += 1
                # Return the function
                return func(*args, **kwargs)
            # Otherwise
            else:
                # Abort with 429
                abort(
                    429, f"Rate limit exceeded. Try again in {int((g.rate_limit[func.__name__]['start'] + _convert_time(period)) - time())} seconds.")

        return wrapped
    return decorator


def test():
    print(_convert_time("1.5s") == 1.5)
    print(_convert_time("2m") == 120)
    print(_convert_time("1h") == 3600)
    print(_convert_time("1d") == 86400)
    print(_convert_time("1w") == 604800)
    print(_convert_time("1.5") == 1.5)
    print(_convert_time(2) == 2)
    try:
        _convert_time("d")
        print(False)
    except ValueError:
        print(True)


if __name__ == "__main__":
    test()
