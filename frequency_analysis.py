

from collections import Counter
from math import inf

EN_ORDER = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def normalize_keep_nonletters(s):
    return ''.join(ch.upper() if ch.isalpha() else ch for ch in s)

def letters_only(s):
    return ''.join(ch for ch in s.upper() if ch.isalpha())

def freq_map_from_text(text):
    letters = letters_only(text)
    counts = Counter(letters)

    sorted_cipher = sorted(ALPHA, key=lambda c: (-counts.get(c, 0), c))
    mapping = {cipher: EN_ORDER[i] for i, cipher in enumerate(sorted_cipher)}
    return mapping, counts

def apply_mapping(text, mapping):
    out = []
    for ch in text:
        if ch.isalpha():
            out.append(mapping.get(ch.upper(), ch).upper())
        else:
            out.append(ch)
    return ''.join(out)

EN_EXPECT = {
    'A': 8.167, 'B': 1.492, 'C': 2.782, 'D': 4.253, 'E': 12.702, 'F': 2.228,
    'G': 2.015, 'H': 6.094, 'I': 6.966, 'J': 0.153, 'K': 0.772, 'L': 4.025,
    'M': 2.406, 'N': 6.749, 'O': 7.507, 'P': 1.929, 'Q': 0.095, 'R': 5.987,
    'S': 6.327, 'T': 9.056, 'U': 2.758, 'V': 0.978, 'W': 2.360, 'X': 0.150,
    'Y': 1.974, 'Z': 0.074
}

def chi_squared_score(text):
    letters = letters_only(text)
    n = len(letters)
    if n == 0:
        return float('inf')
    counts = Counter(letters)
    chi = 0.0
    for L in ALPHA:
        obs = counts.get(L, 0)
        exp = EN_EXPECT[L] * n / 100.0
        if exp > 0:
            chi += (obs - exp) ** 2 / exp
    return chi

def iterative_freq_map(ciphertext, runs=3, verbose=True, stop_if_no_change=True):
   
    current = normalize_keep_nonletters(ciphertext)
    best = (None, float('inf'), -1, None)   
    previous = None

    for r in range(1, runs + 1):
        mapping, counts = freq_map_from_text(current)
        candidate = apply_mapping(current, mapping)
        score = chi_squared_score(candidate)

        if score < best[1]:
            best = (candidate, score, r, mapping.copy())

        if verbose:
            print(f"\n--- Round {r} ---")
            print("Top ciphertext frequencies:", counts.most_common(10))
            sample_map = {k: mapping[k] for k in sorted(list(mapping))[:12]}
            print("Sample mapping (cipher->plain):", sample_map)
            print("Candidate start:", candidate[:300])
            print(f"Chi-sq: {score:.2f}")

        if stop_if_no_change and previous is not None and candidate == previous:
            if verbose:
                print("No change from previous round — stopping early.")
            break

        previous = current
        current = candidate  

    if verbose:
        print("\n=== Best candidate ===")
        print(f"Round: {best[2]}, Chi-sq: {best[1]:.2f}")
        print(best[0][:1000])

    return {
        'best_text': best[0],
        'best_score': best[1],
        'best_round': best[2],
        'best_mapping': best[3]
    }

if __name__ == "__main__":
    print("Iterative frequency-mapping (progressive rounds).")
    ct = input("Paste ciphertext: ").strip()
    runs_raw = 1
    try:
        runs = int(runs_raw) if runs_raw else 3
    except:
        runs = 3
    res = iterative_freq_map(ct, runs=runs, verbose=True, stop_if_no_change=True)
    print("\nFinal best plaintext (first 1000 chars):\n")
    print(res['best_text'][:1000])
