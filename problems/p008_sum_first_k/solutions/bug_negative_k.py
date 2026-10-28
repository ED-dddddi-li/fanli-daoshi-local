# 错解：没处理 k<=0，负数 k 会让切片从末尾倒着截取，结果出错（负数/边界值）
def sum_first_k(nums, k):
    return sum(nums[:k])
