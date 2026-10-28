# 错解：方向弄反，数成了小于 k 的个数（边界值/逻辑方向）
def count_greater(nums, k):
    count = 0
    for x in nums:
        if x < k:
            count += 1
    return count
