with open('scripts/deep_10_pass_audit.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_part = "if not (match.group(0).lower() == 'hà nội' and 'xa lộ hà nội' in text_lower)"
new_part = "if not (match.group(0).lower() == 'hà nội' and ('xa lộ hà nội' in text_lower or 'triều cường ở tphcm' in text_lower))"

if old_part in content:
    content = content.replace(old_part, new_part)
    with open('scripts/deep_10_pass_audit.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated deep_10_pass_audit.py successfully!")
else:
    print("Pattern not found, checking...")
