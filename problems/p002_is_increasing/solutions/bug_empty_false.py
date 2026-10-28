# 错解：空列表错误地返回 False，没按约定返回 True（空输入）
def is_strictly_increasing(nums):
    if len(nums) == 0:
        return False
    for i in range(len(nums) - 1):
        if nums[i] >= nums[i + 1]:
            return False
    return True
