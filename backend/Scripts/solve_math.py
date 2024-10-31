import sympy as sp
import re


def solve_math_expression(expression):
    try:
        # Verificar si la expresión es una ecuación
        if '=' in expression:
            # Separar la ecuación en lado izquierdo y derecho
            lhs, rhs = expression.split('=')

            # Detectar las variables en la ecuación
            variables = re.findall(r'[a-zA-Z]', expression)
            symbols = {var: sp.symbols(var) for var in variables}

            # Convertir ambos lados a expresiones simbólicas
            lhs_sympy = sp.sympify(lhs, locals=symbols)
            rhs_sympy = sp.sympify(rhs, locals=symbols)

            # Crear la ecuación simbólica usando sp.Eq
            equation = sp.Eq(lhs_sympy, rhs_sympy)

            # Resolver la ecuación para la primera variable detectada
            main_variable = list(symbols.values())[0]
            solution = sp.solve(equation, main_variable)
            return solution

        else:
            # Si no es una ecuación, simplemente evaluar la expresión aritmética
            expr = sp.sympify(expression)
            return expr
    except Exception as e:
        return str(e)
