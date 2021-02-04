# coding: utf-8

from pyDes import *


def encrypt_str(text, key='wecube1620210201'):
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


def decrypt_str(encryptstr, key='wecube1620210201'):
    try:
        from Crypto.Cipher import AES
    except:
        return encryptstr
    import base64
    unpad = lambda s: s[0:-ord(s[-1])]
    cipher = AES.new(key, IV='w' * len(key))
    return unpad(cipher.decrypt(base64.b64decode(encryptstr)))
