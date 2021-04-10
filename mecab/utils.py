import math

def read_ptr(ptr, size):
    ptr = ptr[size:]
    return ptr

def read_static(ptr, value):
    r = read_ptr(ptr, value)
    return r

def logsumexp(x, y, flg):
    MINUS_LOG_EPSILON = 50
    if flg: return y
    vmin = min(x, y)
    vmax = max(x, y)
    if (vmax > vmin + MINUS_LOG_EPSILON):
        return vmax
    else:
        return vmax + math.log(math.exp(vmin - vmax) + 1.0)

def tocost(x, y):
    x = float(x)
    y = float(y)

    max_value = 32767
    min_value = -32767
    return max(min((-y * x), max_value), min_value)