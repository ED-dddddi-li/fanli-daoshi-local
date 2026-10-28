# 正确解：用 str.isupper 判断，写法与参考解不同
def count_uppercase(s):
    return sum(1 for c in s if c.isupper())
