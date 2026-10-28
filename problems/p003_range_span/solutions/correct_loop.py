# 正确解：一次遍历同时记录最大最小，写法与参考解不同
def range_span(nums):
    if not nums:
        return 0
    lo = hi = nums[0]
    for x in nums:
        if x < lo:
            lo = x
        if x > hi:
            hi = x
    return hi - lo
