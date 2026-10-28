# 错解：排序后用倒数第一减正数第二（应减第一个），差一取错了最小值（差一）
def range_span(nums):
    if not nums:
        return 0
    s = sorted(nums)
    return s[-1] - s[1]
