# 错解：只数小写元音，忘记处理大写字母（忘记处理大小写）
def count_vowels(s):
    count = 0
    for c in s:
        if c in "aeiou":
            count += 1
    return count
