# 判断是否回文

给定一个字符串 `s`，判断它是否为**回文**，返回布尔值 `True` 或 `False`。判断时：

- **忽略大小写**：`A` 和 `a` 视为相同。
- **忽略空格**：比较前先去掉所有空格。
- 空字符串、以及去掉空格后为空的字符串，约定返回 `True`。
- 字符串长度 0 到 15，只包含字母 `a`、`b`、`A`、`B` 和空格。

示例：

- `is_palindrome("abba")` 返回 `True`
- `is_palindrome("Abba")` 返回 `True`
- `is_palindrome("a b a")` 返回 `True`
- `is_palindrome("ab")` 返回 `False`
