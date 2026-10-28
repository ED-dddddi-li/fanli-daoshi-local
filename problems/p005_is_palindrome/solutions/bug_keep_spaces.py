# 错解：忘记去掉空格，带空格的回文被误判（忘记处理空格）
def is_palindrome(s):
    t = s.lower()
    return t == t[::-1]
