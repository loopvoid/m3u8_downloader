from Crypto.Cipher import AES


def _aes_128_decryption(key, data):
	cryptor = AES.new(key, AES.MODE_CBC, key)
	plain_text = cryptor.decrypt(data)
	return plain_text.rstrip(b'\0')  # .decode('urf-8')


# for AES-128
def aes_decryption(key, data):
	return _aes_128_decryption(key,data)