# 错解：切片差一，多取了一个元素（前 k+1 个）（差一）
def sum_first_k(nums, k):
    if k <= 0:
        return 0
    return sum(nums[:k + 1])
