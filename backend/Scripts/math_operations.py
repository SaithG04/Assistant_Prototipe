import re
import math


def preprocess_math_text(text):
    """
    Preprocesa el texto convirtiendo expresiones comunes en términos manejables por el sistema.
    """
    # Palabras innecesarias que queremos eliminar
    noise_words = ['cuánto', 'es', 'de', 'la', 'el']

    # Eliminamos las palabras no relevantes
    for word in noise_words:
        text = text.replace(word, '')

    replacements = {
        'más': '+',
        'menos': '-',
        'por': '*',
        'dividido entre': '/',
        'dividido por': '/',
        'seno': 'sin(',
        'coseno': 'cos(',
        'tangente': 'tan(',
        'raíz cuadrada': 'sqrt(',
        'logaritmo': 'log(',
        'pi': 'pi',
        'e': 'e',
    }

    # Reemplaza las palabras por los símbolos matemáticos correspondientes
    for word, symbol in replacements.items():
        if word in text:
            print(f"Reemplazando '{word}' con '{symbol}'")
            text = text.replace(word, symbol)

    # Si es una función trigonométrica o raíz, agrega el cierre de paréntesis
    if any(func in text for func in ['sin(', 'cos(', 'tan(', 'sqrt(', 'log(']):
        text += ')'  # Cierra la función

    print(f"Texto final preprocesado: {text}")
    return text.strip()


def solve_simple_math_operation(text):
    """
    Detecta y resuelve operaciones matemáticas sencillas y complejas en un texto.
    """
    # Preprocesamos el texto
    text = preprocess_math_text(text)

    # Imprimir para depurar
    print(f"Texto preprocesado: {text}")

    # Intentar resolver una operación sencilla
    text = text.replace(" ", "")  # Eliminar espacios innecesarios
    pattern = r'(\d+\.?\d*)([+\-*/])(\d+\.?\d*)'  # Patrón para operaciones simples

    match = re.search(pattern, text)

    if match:
        num1 = float(match.group(1))
        operator = match.group(2)
        num2 = float(match.group(3))

        try:
            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*':
                result = num1 * num2
            elif operator == '/':
                result = num1 / num2 if num2 != 0 else "Error: División por cero"
        except Exception as e:
            return f"Error: {str(e)}"

        return f"El resultado de la operación es: {result}"

    # Si no es una operación simple, intenta resolver como operación compleja
    result = solve_complex_math_operation(text)
    if result is not None:
        return f"El resultado de la operación compleja es: {result}"

    return "No pude resolver la operación."


def solve_complex_math_operation(expression):
    """
    Esta función intenta resolver una expresión matemática más compleja dada.
    Incluye operaciones como seno, coseno, tangente, raíz cuadrada, logaritmo, etc.
    """
    try:
        # Imprimir la expresión final antes de ser evaluada
        print(f"Expresión final a evaluar: {expression}")

        # Evalúa la expresión de manera segura utilizando un entorno limitado
        result = eval(expression, {"__builtins__": None}, {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'log': math.log,
            'pi': math.pi,
            'e': math.e
        })

        return result
    except SyntaxError:
        print(f"Error de sintaxis en la expresión: {expression}")
        return "Error de sintaxis en la operación."
    except ZeroDivisionError:
        print(f"División por cero en la expresión: {expression}")
        return "Error: División por cero."
    except Exception as e:
        print(f"Error al resolver la expresión: {e}")
        return None
