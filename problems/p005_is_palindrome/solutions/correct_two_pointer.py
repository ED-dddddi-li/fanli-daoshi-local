# 正确解：双指针从两端向中间比较，写法与参考解不同
def is_palindrome(s):
    t = s.replace(" ", "").lower()
    i, j = 0, len(t) - 1
    while i < j:
        if t[i] != t[j]:
            return False
        i += 1
        j -= 1
    return True
