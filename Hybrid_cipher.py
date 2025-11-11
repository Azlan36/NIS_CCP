import time

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def mod_inverse(a, m):
    if gcd(a, m) != 1:
        return None

    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0

    return x1 % m0

def letter_to_num(c):
    return ord(c.upper()) - 65

def num_to_letter(n):
    return chr((n % 26) + 65)

VALID_A_VALUES = [1,3,5,7,9,11,15,17,19,21,23,25]

def extract_keys(key_string):
    key = key_string.replace(" ", "").upper()

    vigenere_key = key
    a = VALID_A_VALUES[letter_to_num(key[0]) % len(VALID_A_VALUES)]
    b = letter_to_num(key[1]) if len(key) > 1 else 0
    shift_value = sum(letter_to_num(c) for c in key) % 26

    return vigenere_key, a, b, shift_value

def vigenere_encrypt(text, key):
    result = ""
    k = 0
    for c in text:
        t = letter_to_num(c)
        s = letter_to_num(key[k % len(key)])
        result += num_to_letter((t + s) % 26)
        k += 1
    return result

def vigenere_decrypt(text, key):
    result = ""
    k = 0
    for c in text:
        t = letter_to_num(c)
        s = letter_to_num(key[k % len(key)])
        result += num_to_letter((t - s) % 26)
        k += 1
    return result


def affine_encrypt(text, a, b):
    return "".join(num_to_letter((a * letter_to_num(c) + b) % 26) for c in text)

def affine_decrypt(text, a, b):
    inv = mod_inverse(a, 26)
    if inv is None:
        raise ValueError(f"No modular inverse available for a = {a}")
    return "".join(num_to_letter((inv * (letter_to_num(c) - b)) % 26) for c in text)

def shift_encrypt(text, s):
    return "".join(num_to_letter((letter_to_num(c) + s) % 26) for c in text)

def shift_decrypt(text, s):
    return "".join(num_to_letter((letter_to_num(c) - s) % 26) for c in text)

def hybrid_encrypt(plaintext, key):
    plaintext = plaintext.replace(" ", "").upper()
    v_key, a, b, s = extract_keys(key)

    step1 = vigenere_encrypt(plaintext, v_key)
    print(f"\nAfter Vigenere : {step1}")

    step2 = affine_encrypt(step1, a, b)
    print(f"After Affine   : {step2}")

    step3 = shift_encrypt(step2, s)
    print(f"After Shift    : {step3}")

    return step3

def hybrid_decrypt(ciphertext, key):
    ciphertext = ciphertext.replace(" ", "").upper()
    v_key, a, b, s = extract_keys(key)

    step1 = shift_decrypt(ciphertext, s)
    step2 = affine_decrypt(step1, a, b)
    step3 = vigenere_decrypt(step2, v_key)

    return step3

def prompt_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty. Try again.")

def main():
    while True:
        print("\nSelect an option:")
        print("1) Encrypt a plaintext")
        print("2) Decrypt a ciphertext")
        print("3) Exit\n")

        choice = input("Enter choice (1/2/3): ").strip()

        if choice == "1":
            plaintext = prompt_nonempty("\nEnter Plaintext: ")

            while True:
                key = prompt_nonempty("Enter Key (at least 10 letters): ")
                letters_only = "".join(ch for ch in key if ch.isalpha())
                if len(letters_only) >= 10:
                    break
                print("\nKey must contain at least 10 alphabetic characters.\n")

            start = time.perf_counter()
            ciphertext = hybrid_encrypt(plaintext, key)
            end = time.perf_counter()

            print(f"\nFinal Ciphertext: {ciphertext}")
            print(f"Time Taken for Encryption: {end - start:.6f} seconds")

        elif choice == "2":
            ciphertext = prompt_nonempty("\nEnter Ciphertext: ")
            key = prompt_nonempty("Enter Key: ")

            start = time.perf_counter()
            decrypted = hybrid_decrypt(ciphertext, key)
            end = time.perf_counter()

            print(f"\nRecovered Plaintext: {decrypted}")
            print(f"Time Taken for Decryption: {end - start:.6f} seconds")

        elif choice == "3":
            break

        else:
            print("\nInvalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()