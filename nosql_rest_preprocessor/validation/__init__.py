from functools import wraps


def rule_context(f, *contexts):
    @wraps(f)
    def wrapper(*args, **kwargs):
        f.contexts = contexts or []
        return f(*args, **kwargs)

    return wrapper