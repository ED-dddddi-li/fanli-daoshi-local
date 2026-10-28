# 错解：忘记转小写，大小写不同的回文被误判（忘记处理大小写）
def is_palindrome(s):
    t = s.replace(" ", "")
    return t == t[::-1]
