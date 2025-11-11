from collections import Counter
from itertools import product
from math import inf, gcd
import time

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
VALID_A = [1,3,5,7,9,11,15,17,19,21,23,25] 


def normalize(text):
    return ''.join(ch for ch in text.upper() if ch.isalpha())

def char_to_num(c): return ord(c) - 65
def num_to_char(n): return chr((n % 26) + 65)

def modinv(a, m=26):
    a %= m
    if gcd(a, m) != 1:
        return None

    t0, t1 = 0, 1
    r0, r1 = m, a
    while r1 != 0:
        q = r0 // r1
        r0, r1, t0, t1 = r1, r0 - q*r1, t1, t0 - q*t1
    return t0 % m


def shift_decrypt(text, s):
    text = normalize(text)
    return ''.join(num_to_char((char_to_num(c) - s) % 26) for c in text)

def affine_decrypt(text, a, b):
    text = normalize(text)
    a_inv = modinv(a)
    if a_inv is None:
        return None
    return ''.join(num_to_char((a_inv * ((char_to_num(c) - b) % 26)) % 26) for c in text)

def vigenere_decrypt(text, key):
    text = normalize(text)
    key = normalize(key)
    if not key:
        return text
    res = []
    klen = len(key)
    key_nums = [char_to_num(k) for k in key]
    for i, ch in enumerate(text):
        val = (char_to_num(ch) - key_nums[i % klen]) % 26
        res.append(num_to_char(val))
    return ''.join(res)

EN_FREQ = {
    'A': 8.167, 'B': 1.492, 'C': 2.782, 'D': 4.253, 'E': 12.702, 'F': 2.228,
    'G': 2.015, 'H': 6.094, 'I': 6.966, 'J': 0.153, 'K': 0.772, 'L': 4.025,
    'M': 2.406, 'N': 6.749, 'O': 7.507, 'P': 1.929, 'Q': 0.095, 'R': 5.987,
    'S': 6.327, 'T': 9.056, 'U': 2.758, 'V': 0.978, 'W': 2.360, 'X': 0.150,
    'Y': 1.974, 'Z': 0.074
}

COMMON_WORDS = {"THE","BE","TO","OF","AND","A","IN","THAT","HAVE","I","IT","FOR","NOT","ON","WITH","HE","AS","YOU","DO","AT"}

def chi_squared(text):
    text = normalize(text)
    n = len(text)
    if n == 0:
        return float('inf')
    counts = Counter(text)
    chi = 0.0
    for L in ALPHA:
        observed = counts.get(L, 0)
        expected = EN_FREQ[L] * n / 100.0
        if expected > 0:
            chi += (observed - expected)**2 / expected
    return chi

def word_score(text):

    txt = text.upper()
    score = 0

    for w in COMMON_WORDS:
        score += txt.count(w) * len(w)
    return score

def english_score(text):

    c = chi_squared(text)
    w = word_score(text)

    return c - (w * 50)  

def brute_force_hybrid(ciphertext, max_vig_len=3, max_candidates=10, max_trials=None, stop_on_first=False):
    
    ct_norm = normalize(ciphertext)
    total_ct_len = len(ct_norm)
    best = []  
    trials = 0
    start_time = time.time()


    letters = ALPHA


    for s in range(26):
        shifted = shift_decrypt(ct_norm, s)
    
        for a in VALID_A:
            a_inv = modinv(a)
            if a_inv is None:
                continue
            for b in range(26):
                aff_rev = affine_decrypt(shifted, a, b)
                if aff_rev is None:
                    continue

      
                for L in range(1, max_vig_len + 1):
                  
               
                    nkeys = 26 ** L
                
                    for key_tuple in product(letters, repeat=L):
                        vkey = ''.join(key_tuple)
                        trials += 1
                        if max_trials and trials > max_trials:
                            elapsed = time.time() - start_time
                            print(f"[INFO] Reached trial cap ({max_trials}). Stopping.")
                            return sorted(best)[:max_candidates], trials, elapsed

                        pt_candidate = vigenere_decrypt(aff_rev, vkey)
                        score = english_score(pt_candidate)

    
                        if len(best) < max_candidates:
                            best.append((score, s, a, b, vkey, pt_candidate))
                            best.sort(key=lambda x: x[0])
                        else:
                            if score < best[-1][0]:
                                best[-1] = (score, s, a, b, vkey, pt_candidate)
                                best.sort(key=lambda x: x[0])

             
                        if stop_on_first:
                            if score < -200:  
                                elapsed = time.time() - start_time
                                print(f"[INFO] Early good candidate found. Trials: {trials}, Time: {elapsed:.2f}s")
                                best.sort(key=lambda x: x[0])
                                return best[:max_candidates], trials, time.time() - start_time


    elapsed = time.time() - start_time
    best.sort(key=lambda x: x[0])
    return best[:max_candidates], trials, elapsed


if __name__ == "__main__":
    print("Brute-force attack: Shift (26) x Affine (12x26) x Vigenere (26^L)")
    ct = input("Enter ciphertext: ").strip()
    print("Defaults: max_vig_len=3 (26^3=17576). Increase at your own risk.")
    try:
        max_vig_len = int(input("Max Vigenere key length to brute-force (1-4 recommended): ").strip() or "3")
    except:
        max_vig_len = 3
    try:
        max_candidates = int(input("How many top candidates to show [10]: ").strip() or "10")
    except:
        max_candidates = 10
    try:
        max_trials_raw = input("Optional max trials cap (0 for no cap) [0]: ").strip()
        max_trials = int(max_trials_raw) if max_trials_raw else None
        if max_trials == 0:
            max_trials = None
    except:
        max_trials = None
    stop_on_first_input = input("Stop early if strong candidate found? (y/N): ").strip().lower()
    stop_on_first = stop_on_first_input == 'y'

    results, total_trials, elapsed = brute_force_hybrid(ct, max_vig_len=max_vig_len,
                                                       max_candidates=max_candidates,
                                                       max_trials=max_trials,
                                                       stop_on_first=stop_on_first)
    print(f"\nDone. Trials: {total_trials}, Time: {elapsed:.2f}s")
    print(f"Top {len(results)} candidates (lower score = more English-like):\n")
    for i, (score, s, a, b, vkey, pt) in enumerate(results, start=1):
        print(f"#{i}: score={score:.2f}, s={s}, a={a}, b={b}, vkey={vkey}")
        print("  Plaintext start:", pt[:200])
        print("-"*60)
