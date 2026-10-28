# 错解：只遍历到倒数第二个元素，漏掉最后一个（差一）
def count_greater(nums, k):
    count = 0
    for i in range(len(nums) - 1):
        if nums[i] > k:
            count += 1
    return count
