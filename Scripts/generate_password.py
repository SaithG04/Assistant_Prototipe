import random
import string


def generate(long):
    include_digits = input("¿Te gustaría incluir números? (s/n):\n")
    include_sig = input("¿Te gustaría incluir signos? (s/n):\n")
    chars = string.ascii_letters
    if include_digits == 's':
        chars += string.digits
    elif include_sig == 's':
        chars += string.punctuation

    password = ''.join(random.choice(chars) for _ in range(long))
    return password
