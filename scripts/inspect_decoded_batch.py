import sys, os, ast

sys.stdout.reconfigure(encoding='utf-8')

def inspect_batch(filepath, start_idx, end_idx):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]

    print(f"================================================================================")
    print(f"                  INSPECTING DECODED WORDS: BATCH {start_idx} TO {end_idx}")
    print(f"================================================================================")
    
    for i in range(start_idx - 1, end_idx):
        rec_num = i + 1
        line = lines[i]
        text, trips_str = line.split('####')
        tokens = text.split()
        triplets = ast.literal_eval(trips_str)
        
        status = f"REJECT (0 triplets)" if not triplets else f"{len(triplets)} triplets"
        print(f"\n[Rec {rec_num}] ({status})")
        print(f"  TEXT: {text}")
        for t_idx, (asp, opi, pol) in enumerate(triplets, 1):
            asp_text = ' '.join([tokens[j] for j in asp])
            opi_text = ' '.join([tokens[j] for j in opi])
            print(f"    T{t_idx}: Aspect=\"{asp_text}\" {asp} | Opinion=\"{opi_text}\" {opi} | Pol={pol}")

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'data/validate_label/thuan/phase1.txt'
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    end = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    inspect_batch(filepath, start, end)
