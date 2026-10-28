def count_uppercase(s):
    count = 0
    for c in s:
        if "A" <= c <= "Z":
            count += 1
    return count
