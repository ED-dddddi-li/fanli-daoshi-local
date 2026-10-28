# 正确解：用列表推导计数，写法与参考解不同
def count_greater(nums, k):
    return len([x for x in nums if x > k])
