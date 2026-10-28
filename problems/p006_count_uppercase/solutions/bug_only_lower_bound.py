# 错解：只判断 c >= 'A'，漏掉上界，小写字母也被当成大写（边界值）
def count_uppercase(s):
    count = 0
    for c in s:
        if c >= "A":
            count += 1
    return count
