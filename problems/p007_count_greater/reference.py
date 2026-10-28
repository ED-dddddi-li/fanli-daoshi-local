def count_greater(nums, k):
    count = 0
    for x in nums:
        if x > k:
            count += 1
    return count
