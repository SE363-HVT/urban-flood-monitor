# -*- coding: utf-8 -*-
"""
Bộ tự động căn chỉnh và chuẩn hóa Index Triplet chính xác 100%:
Tìm kiếm chính xác từng cụm từ Aspect và Opinion trong danh sách tokens của text,
loại bỏ hoàn toàn lỗi offset thủ công, tự động cắt bỏ dấu câu ở biên và giới từ ở đầu.
"""

bad_puncts = [',', '.', '!', '?', ';', ':', '(', ')', '"', '“', '”', '…', '•', '’', '‘', '#', '🆘', '‼', '❌', '🛑', '💥', '💦', '🌧', '👉', '📍', '♥', '⚠', '·']
bad_preps = ['ở', 'tại', 'trên', 'trong', 'tới', 'vào', 'bởi', 'do', 'đến', 'thuộc', 'gần', 'của', 'dọc', 'khu', 'đoạn']

def find_subsequence(tokens, phrase_words):
    p_len = len(phrase_words)
    for i in range(len(tokens) - p_len + 1):
        if [t.lower() for t in tokens[i:i+p_len]] == [w.lower() for w in phrase_words]:
            return list(range(i, i + p_len))
    return None

def sanitize_span(tokens, idx_list, is_aspect=True):
    # Strip bad puncts from start and end
    while idx_list and tokens[idx_list[0]] in bad_puncts:
        idx_list = idx_list[1:]
    while idx_list and tokens[idx_list[-1]] in bad_puncts:
        idx_list = idx_list[:-1]
        
    if is_aspect:
        while idx_list and tokens[idx_list[0]].lower() in bad_preps:
            idx_list = idx_list[1:]
        while idx_list and tokens[idx_list[0]] in bad_puncts:
            idx_list = idx_list[1:]
            
    return idx_list

def make_triplet(text, asp_phrase, opi_phrase, polarity):
    tokens = text.split()
    asp_words = asp_phrase.split()
    opi_words = opi_phrase.split()
    
    asp_idx = find_subsequence(tokens, asp_words)
    opi_idx = find_subsequence(tokens, opi_words)
    
    assert asp_idx is not None, f"Không tìm thấy Aspect '{asp_phrase}' trong tokens: {tokens}"
    assert opi_idx is not None, f"Không tìm thấy Opinion '{opi_phrase}' trong tokens: {tokens}"
    
    asp_idx = sanitize_span(tokens, asp_idx, is_aspect=True)
    opi_idx = sanitize_span(tokens, opi_idx, is_aspect=False)
    
    assert asp_idx, f"Aspect bị rỗng sau khi sanitize: '{asp_phrase}'"
    assert opi_idx, f"Opinion bị rỗng sau khi sanitize: '{opi_phrase}'"
    assert set(asp_idx).isdisjoint(set(opi_idx)), f"Overlap: {asp_idx} vs {opi_idx} trong text: {text}"
    assert polarity in ['POS', 'NEG', 'NEU'], f"Invalid polarity: {polarity}"
    
    return (asp_idx, opi_idx, polarity)
