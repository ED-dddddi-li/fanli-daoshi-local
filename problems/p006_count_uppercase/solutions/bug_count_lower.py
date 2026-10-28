# 错解：数成了小写字母的个数，判断条件弄反了（忘记处理大小写）
def count_uppercase(s):
    return sum(1 for c in s if c.islower())
