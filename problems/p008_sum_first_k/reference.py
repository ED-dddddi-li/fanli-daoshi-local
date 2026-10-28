def sum_first_k(nums, k):
    if k <= 0:
        return 0
    return sum(nums[:k])
