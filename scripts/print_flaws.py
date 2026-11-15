import sys, ast
sys.stdout.reconfigure(encoding='utf-8')

with open('data/validate_label/thuan/phase2.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip()]

for idx, line in enumerate(lines):
    rec_num = idx + 1
    text, trip_str = line.split('####')
    tokens = text.split()
    triplets = ast.literal_eval(trip_str)
    for t_idx, (asp, opi, pol) in enumerate(triplets):
        for k in range(len(asp) - 1):
            if asp[k+1] != asp[k] + 1:
                print(f"Rec {rec_num}: NON_CONTIGUOUS_ASPECT {asp}")
        for k in range(len(opi) - 1):
            if opi[k+1] != opi[k] + 1:
                print(f"Rec {rec_num}: NON_CONTIGUOUS_OPINION {opi}")
        asp_str = ' '.join(tokens[i] for i in asp)
        opi_str = ' '.join(tokens[i] for i in opi)
        if asp_str not in text:
            print(f"Rec {rec_num}: ASPECT_NOT_IN_TEXT '{asp_str}'")
        if opi_str not in text:
            print(f"Rec {rec_num}: OPINION_NOT_IN_TEXT '{opi_str}'")
