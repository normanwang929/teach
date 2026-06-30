# Python 入门：变量与数据类型

> 本课程带你快速掌握 Python 的基础语法，适合零基础学习者。

---

## 什么是变量？

变量是程序中用来存储数据的容器。在 Python 中，变量不需要声明类型，直接赋值即可：

```python
name = "Alice"
age = 25
is_student = True
```

- `name` 存储了一个字符串
- `age` 存储了一个整数
- `is_student` 存储了一个布尔值

## 基本数据类型

Python 有以下基本数据类型：

- **int** — 整数，如 `42`, `-7`, `0`
- **float** — 浮点数，如 `3.14`, `-0.5`
- **str** — 字符串，如 `"hello"`, `'Python'`
- **bool** — 布尔值，`True` 或 `False`
- **list** — 列表，如 `[1, 2, 3]`
- **dict** — 字典，如 `{"name": "Alice", "age": 25}`

## 动手试试

打开 Python 交互式环境，试试下面的代码：

```python
>>> x = 10
>>> y = 20
>>> print(x + y)
30
```

## 小结

- 变量用 `=` 赋值
- Python 是动态类型语言
- 常用数据类型：int, float, str, bool, list, dict

下一讲我们将学习**控制流（if/else 和循环）**。
