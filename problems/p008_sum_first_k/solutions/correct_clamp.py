# 正确解：把 k 限制在 [0, 长度] 后累加前若干项，写法与参考解不同
def sum_first_k(nums, k):
    m = max(0, min(k, len(nums)))
    total = 0
    for i in range(m):
        total += nums[i]
    return total
