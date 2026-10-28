def range_span(nums):
    if not nums:
        return 0
    return max(nums) - min(nums)
