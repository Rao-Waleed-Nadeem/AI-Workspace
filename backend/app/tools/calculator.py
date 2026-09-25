import ast
import operator


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluate(
    node: ast.AST,
) -> float | int:

    if (
        isinstance(node, ast.Constant)
        and isinstance(
            node.value,
            (int, float),
        )
    ):
        return node.value

    if (
        isinstance(node, ast.BinOp)
        and type(node.op)
        in _BINARY_OPERATORS
    ):
        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if (
            isinstance(node.op, ast.Pow)
            and abs(right) > 10
        ):
            raise ValueError(
                "Exponent is too large."
            )

        return _BINARY_OPERATORS[
            type(node.op)
        ](
            left,
            right,
        )

    if (
        isinstance(node, ast.UnaryOp)
        and type(node.op)
        in _UNARY_OPERATORS
    ):
        return _UNARY_OPERATORS[
            type(node.op)
        ](
            _evaluate(node.operand)
        )

    raise ValueError(
        "Only basic arithmetic expressions "
        "are allowed."
    )


def calculate(
    expression: str,
) -> str:

    try:
        tree = ast.parse(
            expression,
            mode="eval",
        )

        result = _evaluate(
            tree.body
        )

        return str(result)

    except Exception:
        return (
            "Unable to calculate "
            "the expression."
        )