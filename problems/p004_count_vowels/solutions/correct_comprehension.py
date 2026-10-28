# 正确解：用列表推导计数，写法与参考解不同
def count_vowels(s):
    return sum(1 for c in s if c in "aeiouAEIOU")
