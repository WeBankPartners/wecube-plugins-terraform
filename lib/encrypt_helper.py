# coding: utf-8

from pyDes import *
from wecube_plugins_terraform.settings import ENCRYPT_SEED

ENCRYPT_SEED = ENCRYPT_SEED[:16]

if len(ENCRYPT_SEED) < 16:
    ENCRYPT_SEED = ENCRYPT_SEED + 's' * (16 - len(ENCRYPT_SEED))


def encrypt_str(text, key=ENCRYPT_SEED):
    try:
        from Crypto.Cipher import AES
    except:
        return text
    import os
    import base64

    BS = AES.block_size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    cipher = AES.new(key, IV='w' * len(key))
    return base64.b64encode(cipher.encrypt(pad(text)))


def decrypt_str(encryptstr, key=ENCRYPT_SEED):
    try:
        from Crypto.Cipher import AES
    except:
        return encryptstr
    import base64
    unpad = lambda s: s[0:-ord(s[-1])]
    cipher = AES.new(key, IV='w' * len(key))
    return unpad(cipher.decrypt(base64.b64decode(encryptstr)))
