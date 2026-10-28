# 判断是否严格递增

给定一个整数列表 `nums`，判断它是否**严格递增**（每一项都比前一项大），返回布尔值 `True` 或 `False`。

- 严格递增表示相邻两项满足前 < 后；如果出现相等，就不是严格递增。
- 空列表和只有一个元素的列表，约定返回 `True`。
- 列表长度 0 到 20，每个元素在 -5 到 5 之间，可能有重复，可能有负数。

示例：

- `is_strictly_increasing([1, 2, 3])` 返回 `True`
- `is_strictly_increasing([1, 2, 2])` 返回 `False`
- `is_strictly_increasing([3, 1])` 返回 `False`
- `is_strictly_increasing([])` 返回 `True`
