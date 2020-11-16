import math
import typing as t
import random


from Crypto.PublicKey import RSA
from Crypto.Hash import SHAKE256
from Crypto.Cipher import PKCS1_v1_5, AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes


# TODO:  add references
def lcm(a: int, b: int) -> int:
	return a*b // math.gcd(a, b)

def to_int(key: bytes) -> int:
	return int(key.hex(), 16)

def rabinMiller(num: int, trials: int = 40) -> bool:
	s = num - 1
	t = 0
	
	while s % 2 == 0:
		s = s // 2
		t += 1
	for _ in range(trials):
		a = random.randrange(2, num - 1)
		v = pow(a, s, num)
		if v != 1:
			i = 0
			while v != (num - 1):
				if i == t - 1:
					return False
				else:
					i = i + 1
					v = (v ** 2) % num
	return True

def is_prime(num: int) -> bool:
	# TODO: do more checks
	if (num < 2):
		return False
	lowPrimes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 
	67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 
	157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 
	251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313,317, 331, 337, 347, 349, 
	353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 
	457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 
	571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 
	673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 
	797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 
	911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]
	
	if num in lowPrimes:
		return True
	for prime in lowPrimes:
		if (num % prime == 0):
			return False
	return rabinMiller(num)

def get_next_prime(num: int, cycle: bool = True) -> int:
	assert num > 1
	bit_length = len(bin(num)) - 2 
	max_for_bit_length = (1<<bit_length) - 1
	min_for_bit_length = 1<<(bit_length -1)
	prime_candidate = num +1

	while prime_candidate < max_for_bit_length:
		# we're iterating over all, is_prime should do all little optimizations
		if is_prime(prime_candidate):
			assert prime_candidate != num
			return prime_candidate
		prime_candidate += 1
	if cycle:
		return get_next_prime(min_for_bit_length)
	else:
		raise ValueError(f"No prime greater then {num} in bit length of {bit_length}")



def get_var_hash(passphrase: bytes, length: int) -> bytes:
	shake = SHAKE256.new()
	shake.update(passphrase)
	return shake.read(length)

def egcd(a: int, b: int)-> t.Tuple[int, int, int]:
	if a == 0:
		return (b, 0, 1)
	else:
		g, y, x = egcd(b % a, a)
		return (g, x - (b // a) * y, y)

#### https://stackoverflow.com/a/9758173/14624614
def modinv(a:int, m:int) -> int:
	g, x, _ = egcd(a, m)
	if g != 1:
		raise Exception('modular inverse does not exist')
	else:
		return x % m

def get_components(p: int, q: int, e: int = 65537) -> t.Tuple[int, int, int, int, int, int]:
	# TODO: make checks if they all are correct
	# pycryptodome library also checks them
	n = p * q
	lcm_val = lcm(p-1, q-1)
	d = modinv(e, lcm_val)
	u = modinv(p, q)
	return (n, e, d, p, q, u)

def generate_keys_from_primes(prime1: int, prime2: int) -> RSA.RsaKey:
	# TODO:
	p, q = prime1, prime2
	rsa_components = get_components(p, q)
	# RSA.construct makes checks of component values but RSA.RsaKey doesn't
	# so we'll use the former
	return RSA.construct(rsa_components)




def generate_rsa_key(passphrase: bytes, key_len: int = 2048) -> RSA.RsaKey:
	""" algorithm 

	passphrase ------------------------>   hash1 -----------------------> hash2
					SHAKE256				|		   SHAKE256			   | 
											|							   | 
											| binary					   | binary 
											|							   |  
											v							   v
										  hash1b						 hash2b		  
											|							   |  
											| next prime nubmer			   | next prime number
											|							   |  
											v							   v
										   prime1						  prime2  
											|							   |  
											 ------------------------------
														   |			   
														   v
							generate public/private rsa key as usual based on these two primes


	* binary referes to converting bytes into integer ( for calculating prime )
	* ctr is for tweaking length of resulting prime numbers
	* we can do as many sha-256+ctr iteration as we want to increase compute time
	* if next prime number is not found in the bit range of number then start from 10000000...(i.e. 1<<(bit_length-1)) again
	"""

	key_len_bytes = key_len//8
	hash1 = get_var_hash(passphrase, key_len_bytes//2)
	hash2 = get_var_hash(hash1, key_len_bytes - (key_len_bytes//2))
	hash1_int = to_int(hash1)
	hash2_int = to_int(hash2)
	prime1 = get_next_prime(hash1_int)
	prime2 = get_next_prime(hash2_int)
	primes = [prime1, prime2]
	private_key = generate_keys_from_primes(*sorted(primes))
	return private_key

def encrypt(public_key: RSA.RsaKey, content: bytes) -> bytes:
	cipher = PKCS1_v1_5.new(public_key)
	try:
		return cipher.encrypt(content)
	except ValueError:
		raise ValueError("content too long to encrypt. use encrypt_large which uses aes encryption")

def decrypt(private_key: RSA.RsaKey, content: bytes) -> bytes:
	cipher = PKCS1_v1_5.new(private_key)
	# large length is necessary, because RSA generally cannot encrypt this long content
	# TODO: lookup about maximum length contraint
	large_senintel = b"a"*2048*2048
	original_content = cipher.decrypt(content, large_senintel) # type: ignore TODO: error in .pyi file

	if original_content == large_senintel:
		raise ValueError("Couldn't decrypt")
	return original_content

def encrypt_large(public_key: RSA.RsaKey, content: bytes) -> bytes:
	aes_key = get_random_bytes(16)
	cipher = AES.new(aes_key, AES.MODE_GCM)
	encoded_bytes, tag = cipher.encrypt_and_digest(content) # type: ignore encrypt_and_digest method isn't recognized
	# we're depending on a fact that tag size is always of 16 bytes
	# maybe we should make it more explicit by sizeBlocksizeBlock way, TODO: find name of this format sizeBlocksizeBlock
	# 16key + 16tag + 16nonce + ..encoded_bytes
	assert hasattr(cipher, "nonce")
	assert isinstance(cipher.nonce, bytes) # type: ignore pycryptodome: assert covers ^
	return encrypt(public_key, aes_key) + tag + cipher.nonce + encoded_bytes # type: ignore pycryptodome: assert covers ^
	
def decrypt_large(private_key: RSA.RsaKey, content: bytes) -> bytes:
	key_length = private_key._n.size_in_bytes() # type: ignore pycryptodome: _n is dynamically added
	nonce_length = tag_length = 16
	if len(content) < key_length + 16:
		raise ValueError("Not valid content")

	pointer = 0
	aes_key = decrypt(private_key, content[pointer:pointer + key_length])
	pointer += key_length

	tag = content[pointer:pointer+tag_length]
	pointer += tag_length

	nonce = content[pointer:pointer+nonce_length]
	pointer += nonce_length

	encrypted_data = content[pointer:]

	cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
	decoded_content = cipher.decrypt_and_verify(encrypted_data, tag) # type: ignore decrypt_and_verify method isn't recognized

	return decoded_content

if __name__ == "__main__":
	import sys
	if len(sys.argv) != 3:
		print("usage: security.py {{passphrase}} {{key_to_export: [private|public]}}")
		exit()
	
	passphrase = sys.argv[1].encode("utf-8")
	key = generate_rsa_key(passphrase)
	if sys.argv[2] == "private":
		print(key.export_key("PEM"))
	else:
		print(key.publickey().export_key("PEM"))

