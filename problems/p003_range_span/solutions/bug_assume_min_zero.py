# 错解：默认最小值是 0，直接返回最大值，最小值非 0（含负数）时出错（负数）
def range_span(nums):
    if not nums:
        return 0
    return max(nums)
