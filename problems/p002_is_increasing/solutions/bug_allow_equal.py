# 错解：用 > 判断，允许相邻相等，重复元素时误判为递增（重复元素）
def is_strictly_increasing(nums):
    for i in range(len(nums) - 1):
        if nums[i] > nums[i + 1]:
            return False
    return True
