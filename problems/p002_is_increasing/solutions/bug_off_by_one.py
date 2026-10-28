# 错解：循环范围差一，访问 nums[i+1] 越界，非空列表会抛 IndexError（差一）
def is_strictly_increasing(nums):
    for i in range(len(nums)):
        if nums[i] >= nums[i + 1]:
            return False
    return True
