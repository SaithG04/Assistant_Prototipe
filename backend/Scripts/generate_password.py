import random
import string


def generate(long):
    chars = string.ascii_letters
    include_digits = input("¿Te gustaría incluir números? (s/n):\n")

    while (include_digits != 's') and (include_digits != 'n'):
        print("Disculpa, no entendí...")
        include_digits = input("¿Te gustaría incluir números? (s/n):\n")

    include_sig = input("¿Te gustaría incluir signos? (s/n):\n")

    while (include_sig != 's') and (include_sig != 'n'):
        print("Disculpa, no entendí...")
        include_sig = input("¿Te gustaría incluir signos? (s/n):\n")

    if include_digits == 's':
        chars += string.digits
    elif include_sig == 's':
        chars += string.punctuation

    password = ''.join(random.choice(chars) for _ in range(long))
    return password