# 错解：双指针循环条件差一，少比较最靠中间的一对，相邻两字符不同时漏判（差一）
def is_palindrome(s):
    t = s.replace(" ", "").lower()
    i, j = 0, len(t) - 1
    while i < j - 1:
        if t[i] != t[j]:
            return False
        i += 1
        j -= 1
    return True
