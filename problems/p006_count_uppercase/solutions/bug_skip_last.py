# 错解：只遍历到倒数第二个字符，漏掉最后一个（差一）
def count_uppercase(s):
    count = 0
    for i in range(len(s) - 1):
        if "A" <= s[i] <= "Z":
            count += 1
    return count
