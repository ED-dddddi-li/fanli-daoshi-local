# 错解：没有处理空列表，max()/min() 对空列表抛 ValueError（空输入）
def range_span(nums):
    return max(nums) - min(nums)
