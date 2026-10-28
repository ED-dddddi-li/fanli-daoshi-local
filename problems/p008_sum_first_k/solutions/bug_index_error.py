# 错解：用下标循环到 k，当 k 超过列表长度时越界抛 IndexError（边界值/空输入）
def sum_first_k(nums, k):
    total = 0
    for i in range(k):
        total += nums[i]
    return total
