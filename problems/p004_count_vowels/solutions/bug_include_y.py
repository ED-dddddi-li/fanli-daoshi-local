# 错解：把 y 也当成元音，多算了（边界值：把非元音当元音）
def count_vowels(s):
    count = 0
    for c in s.lower():
        if c in "aeiouy":
            count += 1
    return count
