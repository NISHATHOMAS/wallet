import random
import re
import string


def unique_string_generator(size=6,
                            chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))