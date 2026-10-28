# 正确解：用 zip 比较相邻两项，写法与参考解不同
def is_strictly_increasing(nums):
    return all(a < b for a, b in zip(nums, nums[1:]))
