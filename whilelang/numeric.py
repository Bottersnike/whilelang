from .util import from_numeric_name, phi_prime


def arith_from_num(num):
    from .nodes import ConstantNode, VariableNode, AddNode, SubNode, MulNode

    if num % 5 == 0:
        n = int(num / 5)
        return ConstantNode(n)
    elif num % 5 == 1:
        x = from_numeric_name(int((num - 1) // 5))
        return VariableNode(x)
    else:
        remainder = num % 5

        a = int((num - remainder) // 5)
        a1, a2 = phi_prime(a)
        a1 = arith_from_num(a1)
        a2 = arith_from_num(a2)

        if remainder == 2:
            return AddNode(a1, a2)
        if remainder == 3:
            return SubNode(a1, a2)
        if remainder == 4:
            return MulNode(a1, a2)


def bool_from_num(num):
    from .nodes import ConstantNode, EqNode, CmpNode, NotNode, AndNode

    if num == 0:
        return ConstantNode(True)
    elif num == 1:
        return ConstantNode(False)
    if num % 4 == 2 or num % 4 == 3:
        remainder = num % 5

        a = int((num - remainder) // 4)
        a1, a2 = phi_prime(a)
        a1 = arith_from_num(a1)
        a2 = arith_from_num(a2)

        if remainder == 3:
            return EqNode(a1, a2)
        else:
            return CmpNode(a1, "<=", a2)
    elif num % 4 == 0:
        return NotNode(bool_from_num(int(num // 4)))
    elif num % 4 == 1:
        b = int((num - 1) // 4)
        b1, b2 = phi_prime(b)
        b1 = bool_from_num(b1)
        b2 = bool_from_num(b2)

        return AndNode(b1, b2)


def stmt_from_num(num):
    from .nodes import SkipNode, WhileNode, AssignNode, SuiteNode, IfNode

    if num == 0:
        return SkipNode()
    elif num % 4 == 1:
        b, S = phi_prime(int((num - 1) // 4))
        return WhileNode(bool_from_num(b), stmt_from_num(S))
    elif num % 4 == 2:
        x, a = phi_prime(int((num - 2) // 4))
        x = from_numeric_name(x)
        a = arith_from_num(a)
        return AssignNode(x, a)
    elif num % 4 == 3:
        S1, S2 = phi_prime(int((num - 3) // 4))
        return SuiteNode([stmt_from_num(S1), stmt_from_num(S2)])
    elif num % 4 == 0:
        b, S = phi_prime(int((num - 4) // 4))
        S1, S2 = phi_prime(S)
        return IfNode(bool_from_num(b), stmt_from_num(S1), stmt_from_num(S2))
