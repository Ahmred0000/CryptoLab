from flask import Flask, render_template, request, jsonify
import numpy as np
import base64

try:
    from Crypto.Cipher import DES, AES
    from Crypto.Util.Padding import pad, unpad
except ImportError:
    DES = None
    AES = None

app = Flask(__name__, static_folder='assets')

def mod_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1: return x
    return None

def prepare_text(text):
    return "".join([c.upper() for c in text if c.isalpha()])

def playfair_cipher_visual(text, key, mode='encrypt'):
    key = str(key).upper().replace("J", "I")
    matrix = []
    seen = set()
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    
    for char in key + alphabet:
        if char not in seen and char.isalpha():
            seen.add(char)
            matrix.append(char)
    grid = [matrix[i:i+5] for i in range(0, 25, 5)]
    
    def get_pos(c):
        for r, row in enumerate(grid):
            if c in row: return r, row.index(c)
        return None

    text_clean = prepare_text(text).replace("J", "I")
    pairs = []
    
    if mode == 'encrypt':
        i = 0
        while i < len(text_clean):
            a = text_clean[i]
            b = text_clean[i+1] if i+1 < len(text_clean) else 'X'
            if a == b: pairs.append((a, 'X')); i += 1
            else: pairs.append((a, b)); i += 2
    else:
        if len(text_clean) % 2 != 0: text_clean += 'X'
        pairs = [(text_clean[i], text_clean[i+1]) for i in range(0, len(text_clean), 2)]

    res = ""
    shift = 1 if mode == 'encrypt' else -1
    steps = [] 

    for a, b in pairs:
        p1, p2 = get_pos(a), get_pos(b)
        if not p1 or not p2: continue
        r1, c1 = p1
        r2, c2 = p2
        
        val1, val2 = "", ""
        if r1 == r2:
            val1 = grid[r1][(c1 + shift) % 5]
            val2 = grid[r2][(c2 + shift) % 5]
        elif c1 == c2: 
            val1 = grid[(r1 + shift) % 5][c1]
            val2 = grid[(r2 + shift) % 5][c2]
        else: 
            val1 = grid[r1][c2]
            val2 = grid[r2][c1]
            
        res += val1 + val2
        
        steps.append({
            'pair': [a, b],
            'cipher': [val1, val2],
            'pos1': {'r': r1, 'c': c1},
            'pos2': {'r': r2, 'c': c2}
        })
            
    return {'result': res, 'matrix': matrix, 'steps': steps}

def caesar_cipher(text, key, mode):
    try: shift = int(key)
    except: return "Error: Key must be integer"
    if mode == 'decrypt': shift = -shift
    res = ""
    for char in text:
        if char.isalpha():
            start = 65 if char.isupper() else 97
            res += chr((ord(char) - start + shift) % 26 + start)
        else: res += char
    return res

def mono_cipher(text, key, mode):
    key_map = str(key).lower()
    seen = set()
    clean_key = [x for x in key_map if x.isalpha() and not (x in seen or seen.add(x))]
    if len(clean_key) != 26: return "Error: Key must contain 26 unique chars."
    key_map = "".join(clean_key)
    plain = "abcdefghijklmnopqrstuvwxyz"
    if mode == 'encrypt': tab = str.maketrans(plain+plain.upper(), key_map+key_map.upper())
    else: tab = str.maketrans(key_map+key_map.upper(), plain+plain.upper())
    return text.translate(tab)

def vigenere_cipher(text, key, mode):
    if not str(key).isalpha(): return "Error: Alpha Key Only"
    keys = [ord(c.lower())-97 for c in key]
    if not keys: return "Error"
    res = ""; ki = 0
    for c in text:
        if c.isalpha():
            shift = keys[ki%len(keys)]
            if mode=='decrypt': shift = -shift
            base = 65 if c.isupper() else 97
            res += chr((ord(c)-base+shift)%26 + base)
            ki+=1
        else: res+=c
    return res

def rail_fence(text, key, mode):
    try: d = int(key)
    except: return "Error: Int Depth"
    if d<2: return text
    if mode == 'encrypt':
        fence = [[] for _ in range(d)]
        rail=0; direct=1
        for c in text:
            fence[rail].append(c)
            rail += direct
            if rail==d-1 or rail==0: direct = -direct
        return "".join(["".join(r) for r in fence])
    return "[Decryption Complex for Demo]"

def row_trans(text, key, mode):
    try: order = [int(k)-1 for k in str(key)]
    except: return "Error: Key like 3142"
    cols = len(order)
    if mode == 'encrypt':
        pad_len = (cols - len(text)%cols)%cols
        text += '_' * pad_len
        grid = [text[i:i+cols] for i in range(0, len(text), cols)]
        return "".join([row[c] for c in order for row in grid])
    return "[Decryption Complex for Demo]"

def hill_cipher(text, key, mode):
    try:
        K = np.array(key).reshape(2, 2)
        text = prepare_text(text).lower()
        if len(text)%2!=0: text+='x'
        vals = [ord(c)-97 for c in text]
        if mode == 'decrypt':
            det = int(np.round(np.linalg.det(K)))
            det_inv = mod_inverse(det%26, 26)
            if not det_inv: return "Error: Non-invertible Matrix"
            K = (det_inv * np.array([[K[1,1], -K[0,1]], [-K[1,0], K[0,0]]])) % 26
        res = ""
        for i in range(0, len(vals), 2):
            vec = np.array([[vals[i]], [vals[i+1]]])
            r = np.dot(K, vec) % 26
            res += chr(int(r[0][0])+97) + chr(int(r[1][0])+97)
        return res.upper()
    except Exception as e: return f"Hill Error: {e}"

def rotor_machine(text, key, mode):
    try: off = int(key)
    except: return "Error: Int Key"
    res=""
    for c in text:
        if c.isalpha():
            shift = off if mode=='encrypt' else -off
            base = 65 if c.isupper() else 97
            res += chr((ord(c)-base+shift)%26 + base)
            off = (off+1)%26
        else: res+=c
    return res

def feistel(text, key, mode):
    data = [ord(c) for c in text]
    if len(data)%2!=0: data.append(32)
    mid = len(data)//2
    L, R = data[:mid], data[mid:]
    try: k = int(key)
    except: k=5
    
    def round_func(left, right, k_val):
        new_r = [l ^ ((r + k_val)%255) for l, r in zip(left, right)]
        return right, new_r 

    if mode == 'encrypt':
        for i in range(2):
            temp = R[:]
            f = [(x+k)%255 for x in R]
            R = [l^fx for l,fx in zip(L, f)]
            L = temp
        return "".join([chr(x) for x in R+L])
    else:
        L, R = R, L
        for i in range(2):
            temp = L[:]
            f = [(x+k)%255 for x in L]
            L = [r^fx for r,fx in zip(R, f)]
            R = temp
        return "".join([chr(x) for x in L+R])

def modern(algo, text, key, mode):
    if not DES: return "Error: Lib Missing"
    try:
        kb = str(key).encode()
        if algo=='DES':
            if len(kb)!=8: return "Error: Key 8 chars"
            c = DES.new(kb, DES.MODE_ECB); bs=8
        else:
            if len(kb) not in [16,24,32]: return "Error: Key 16/24/32 chars"
            c = AES.new(kb, AES.MODE_ECB); bs=16
        
        if mode == 'encrypt':
            return base64.b64encode(c.encrypt(pad(text.encode(), bs))).decode()
        else:
            return unpad(c.decrypt(base64.b64decode(text)), bs).decode()
    except Exception as e: return f"Error: {e}"

@app.route('/')
def index(): return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    d = request.json
    algo = d.get('algorithm')
    txt = d.get('text', '')
    key = d.get('key', '')
    mode = d.get('mode')
    
    res = ""
    sec = "weak"
    extra = {} 

    try:
        if algo == "Playfair Cipher":
            out = playfair_cipher_visual(txt, key, mode)
            res = out['result']
            extra = {'matrix': out['matrix'], 'steps': out['steps']}
            sec = "medium"
        elif algo == "Caesar Cipher": res = caesar_cipher(txt, key, mode)
        elif algo == "Monoalphabetic Cipher": res = mono_cipher(txt, key, mode)
        elif algo == "Vigenère Cipher": res = vigenere_cipher(txt, key, mode); sec="medium"
        elif algo == "One-Time Pad":
            if len(str(key)) < len(txt): res = "Error: Key length"
            else: res = vigenere_cipher(txt, key, mode); sec="strong"
        elif algo == "Hill Cipher": res = hill_cipher(txt, key, mode); sec="medium"
        elif algo == "Rail Fence": res = rail_fence(txt, key, mode)
        elif algo == "Row Transposition": res = row_trans(txt, key, mode); sec="medium"
        elif algo == "Permutation Cipher": res = row_trans(txt, key, mode)
        elif algo == "Rotor Machines": res = rotor_machine(txt, key, mode); sec="medium"
        elif algo == "Feistel Cipher": res = feistel(txt, key, mode); sec="medium"
        elif algo == "DES": res = modern('DES', txt, key, mode); sec="medium"
        elif algo == "AES": res = modern('AES', txt, key, mode); sec="strong"
        else: res = "Algorithm Not Found"
    except Exception as e: res = f"Error: {str(e)}"

    return jsonify({'result': res, 'security': sec, 'extra': extra})

if __name__ == '__main__':
    app.run(debug=True)