import sys
import ast

sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.rstrip('\r\n') for line in f]

# The corrected set of indices
handled = {
    1880, 1883, 1884, 1888, 1892, 1901, 1902, 1903, 1904, 1905,
    1907, 1908, 1909, 1910, 1911, 1896, 1916, 1919, 1920, 1921,
    1923, 1924, 1925, 1926, 1929
}

for i in range(1880, 1930):
    if i not in handled:
        line = lines[i]
        parts = line.split('####')
        text = parts[0].strip()
        triplets = ast.literal_eval(parts[1].strip())
        tokens = text.split()
        print(f"REC {i+1} (idx {i}):")
        print(f"  TEXT: {text}")
        print(f"  TRIPS: {triplets}")
        for t in triplets:
            print(f"    Asp: '{' '.join(tokens[x] for x in t[0])}' | Op: '{' '.join(tokens[x] for x in t[1])}' | Pol: {t[2]}")
