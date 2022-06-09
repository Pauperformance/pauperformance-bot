def truncate(f, n):
    # truncates/pads a float f to n decimal places without rounding
    s = "%.12f" % f
    i, p, d = s.partition(".")
    return float(".".join([i, (d + "0" * n)[:n]]))
