def phi(n, m):
    return (2 ** n) * (2 * m + 1) - 1


def phi_prime(x):
    n = 0
    m = int(x) + 1
    while m % 2 == 0 and m > 0:
        n += 1
        m >>= 1
    m = (m - 1) // 2

    return n, m


def beta(x):
    return x
    # return (2 * x) if x >= 0 else (-2 * x - 1)


def numeric_name(name):
    return "xyz".index(name)
    val = 0
    for i in name:
        val = (val << 8) | ord(i)
    return val


def from_numeric_name(num):
    return "xyz"[num]
    name = ""
    while num:
        name += chr(num & 0xff)
        num >>= 8
    return name
