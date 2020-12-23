# coding=utf-8

import random


def random_str(strlen=8):
    src_str = "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    sa = []
    for i in range(strlen):
        sa.append(random.choice(src_str))

    return "".join(sa)
