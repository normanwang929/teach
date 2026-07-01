> **课程简介：**
> 欢迎来到《Python基础入门》！本课程专为零基础或刚接触编程的学员设计。我们将以简洁明快的方式，带你走进Python的世界。Python作为一门优雅、易读且功能强大的编程语言，广泛应用于数据科学、Web开发、自动化运维和人工智能等领域。通过本课程约1-2小时的学习，你将掌握Python的核心语法、基本数据结构、流程控制以及函数定义，为后续的深入学习打下坚实基础。本课程内容参考了官方文档、廖雪峰老师及菜鸟教程等权威资料，确保你学到的知识既标准又实用。

---

## 第一章 初识Python与环境搭建

### 1.1 认识Python与安装环境

- **学习目标：**
  - 了解Python语言的特点与优势
  - 学会在本地计算机安装Python解释器
  - 掌握使用命令行或终端运行Python代码
  - 能够编写并运行第一个Python程序

- **讲义：**

  Python由吉多·范罗苏姆于1989年发明，是一种高级、解释型、面向对象的编程语言。它的设计哲学强调代码的可读性和简洁性，使用缩进（通常为4个空格）来定义代码块，而非像C语言那样使用大括号。这种设计使得Python代码看起来像是一篇伪代码，非常适合初学者入门。Python拥有一个庞大且活跃的社区，提供了数以万计的第三方库，几乎可以解决任何领域的问题。从简单的脚本到复杂的机器学习模型，Python都能胜任。

  要开始学习Python，首先需要安装Python解释器。访问Python官方网站（https://www.python.org/），在Downloads页面选择对应你操作系统的最新版本（如3.12.x或3.13.x）。安装时，请务必勾选“Add Python to PATH”选项，这样你就可以在命令行中直接使用`python`命令。安装完成后，打开终端（macOS/Linux）或命令提示符（Windows），输入`python --version`，如果显示版本号，则说明安装成功。你还可以使用`pip --version`检查包管理工具pip是否已安装，pip用于安装第三方库。

  除了纯文本编辑器（如VS Code、Sublime Text、Notepad++），初学者也可以使用集成开发环境（IDE），如PyCharm、Thonny或Jupyter Notebook。IDE提供了代码补全、调试等功能，能显著提高开发效率。本课程推荐使用VS Code并安装Python扩展。

  现在，让我们编写第一个程序。在任何编辑器中新建一个文件，命名为`hello.py`，输入以下代码：
  ```python
  print("Hello, World!")
  ```
  保存文件后，在终端中进入该文件所在目录，运行 `python hello.py`，你将看到输出：
  ```
  Hello, World!
  ```
  恭喜你，你已经成功运行了第一个Python程序！`print()`是一个内置函数，用于将括号内的内容输出到控制台。`"Hello, World!"`是一个字符串，用双引号括起来。

  为了更高效的交互式学习，Python还提供了一个交互式解释器。在终端直接输入`python`（不带文件名），就会进入交互模式，提示符为`>>>`。你可以直接输入代码并立即看到结果。例如：
  ```python
  >>> print("Hello from interactive mode!")
  Hello from interactive mode!
  >>> 1 + 2
  3
  ```
  交互模式非常适合测试小段代码或学习新语法。按`exit()`或`Ctrl+D`（macOS/Linux）/`Ctrl+Z`（Windows）可以退出。

- **代码示例：**
  ```python
  # 第一个Python程序
  print("Hello, World!")

  # 在交互模式中计算
  # >>> 2 * 3
  # 6
  # >>> "Python" + " is fun"
  # 'Python is fun'
  ```

### 1.2 基础语法与变量

- **学习目标：**
  - 理解Python的注释、缩进和语句规则
  - 掌握变量的定义与赋值
  - 熟悉基本数据类型：整数、浮点数、字符串、布尔值
  - 了解类型转换与输入输出函数

- **讲义：**

  Python的语法规则非常清晰。首先，注释用于解释代码，不会被解释器执行。单行注释以`#`开头，多行注释可以用三个单引号`'''`或三个双引号`"""`包裹。其次，缩进是Python的灵魂。同一代码块（如`if`、`for`、函数体）内的语句必须具有相同的缩进级别。通常使用4个空格，不建议使用Tab键，因为不同环境下Tab的显示长度可能不同。最后，Python语句通常以换行结束，不需要分号。如果一行代码过长，可以使用反斜杠`\`进行续行，或者将表达式放在括号、方括号或花括号内自动续行。

  变量是存储数据的容器。在Python中，变量不需要声明类型，直接赋值即可创建。例如：
  ```python
  name = "Alice"
  age = 25
  height = 1.68
  is_student = True
  ```
  这里，`name`是字符串类型，`age`是整数类型，`height`是浮点数类型，`is_student`是布尔类型。Python是动态类型语言，变量的类型可以改变（但不推荐随意改变）。

  基本数据类型包括：
  - **整数 (int)**：如 `10`, `-3`, `0`
  - **浮点数 (float)**：如 `3.14`, `-0.5`, `1.0`。注意，浮点数运算可能存在精度问题（如 `0.1 + 0.2` 不等于 `0.3`），这是计算机底层二进制表示导致的。
  - **字符串 (str)**：用单引号、双引号或三引号括起来的文本。如 `'Hello'`, `"World"`, `"""多行文本"""`。字符串可以使用`+`拼接，`*`重复。
  - **布尔值 (bool)**：只有两个值 `True` 和 `False`，常用于逻辑判断。

  类型转换可以使用内置函数：`int()`、`float()`、`str()`、`bool()`。例如：
  ```python
  # 字符串转整数
  num_str = "123"
  num_int = int(num_str)
  print(num_int + 1)  # 输出 124
  ```

  输入输出是程序与用户交互的基本方式。`input()`函数用于从键盘获取输入，它总是返回一个字符串。`print()`函数用于输出，可以同时输出多个值，用逗号分隔，默认以空格隔开。例如：
  ```python
  user_name = input("请输入你的名字：")
  print("你好，", user_name, "！欢迎学习Python。")
  ```

- **代码示例：**
  ```python
  # 变量与数据类型
  course = "Python基础"
  duration = 2  # 小时
  version = 3.12
  is_beginner = True

  print("课程：", course)
  print("时长：", duration, "小时")
  print("版本：", version)
  print("是否适合新手：", is_beginner)

  # 类型转换
  age_str = input("请输入你的年龄：")
  age_int = int(age_str)
  print("明年你将是", age_int + 1, "岁。")
  ```

---

## 第二章 数据结构与流程控制

### 2.1 列表、元组与字典

- **学习目标：**
  - 掌握列表的创建、索引、切片及常用方法
  - 理解元组的不可变特性及其应用场景
  - 学会使用字典存储键值对数据
  - 了解集合的基本概念

- **讲义：**

  数据结构是组织和管理数据的方式。Python内置了多种高效的数据结构。

  **列表 (list)** 是最常用的序列类型，用方括号`[]`表示，元素之间用逗号分隔。列表中的元素可以是不同类型，且可以修改（可变）。例如：
  ```python
  fruits = ["苹果", "香蕉", "橙子"]
  numbers = [1, 2.5, "three", True]  # 混合类型
  ```
  - **索引**：从0开始。`fruits[0]` 返回 `"苹果"`，`fruits[-1]` 返回最后一个元素 `"橙子"`。
  - **切片**：`列表[start:stop:step]`，返回一个新的子列表。`fruits[1:3]` 返回 `["香蕉", "橙子"]`。
  - **常用方法**：`append()` 添加元素到末尾，`insert()` 在指定位置插入，`remove()` 删除第一个匹配元素，`pop()` 弹出并返回指定位置元素，`sort()` 排序（需元素类型一致），`len()` 获取长度。

  **元组 (tuple)** 与列表类似，但用圆括号`()`表示，且**不可变**：创建后不能修改其元素。元组通常用于存储不应被修改的数据，如函数的多个返回值、数据库记录等。例如：
  ```python
  point = (3, 4)
  # point[0] = 5  # 错误！元组不能修改
  ```
  元组可以解包：`x, y = point`，将`x`赋值为3，`y`赋值为4。

  **字典 (dict)** 用于存储键值对，用花括号`{}`表示。键必须是不可变类型（如字符串、数字、元组），值可以是任意类型。字典是无序的（Python 3.7+保持插入顺序）。例如：
  ```python
  student = {"name": "小明", "age": 18, "score": 95.5}
  print(student["name"])  # 输出 "小明"
  student["grade"] = "A"  # 添加新键值对
  ```
  常用方法：`keys()` 返回所有键，`values()` 返回所有值，`items()` 返回键值对元组，`get(key, default)` 安全获取值。

  **集合 (set)** 用花括号或`set()`创建，元素无序且唯一，常用于去重和集合运算。例如：
  ```python
  unique_numbers = {1, 2, 2, 3, 3, 3}  # 实际为 {1, 2, 3}
  ```

- **代码示例：**
  ```python
  # 列表操作
  shopping_list = ["牛奶", "面包", "鸡蛋"]
  shopping_list.append("苹果")
  print("购物清单：", shopping_list)

  # 元组解包
  coordinates = (10, 20)
  x, y = coordinates
  print(f"坐标：({x}, {y})")

  # 字典操作
  book = {"title": "Python入门", "price": 49.9}
  print("书名：", book["title"])
  book["author"] = "张三"
  print("完整信息：", book)
  ```

### 2.2 条件语句与循环

- **学习目标：**
  - 掌握`if`、`elif`、`else`构建条件分支
  - 理解逻辑运算符（and, or, not）的用法
  - 学会使用`for`循环遍历序列
  - 掌握`while`循环及`break`、`continue`控制语句

- **讲义：**

  流程控制让程序能够根据条件做出不同决策，或重复执行某段代码。

  **条件语句**使用`if`、`elif`、`else`关键字。注意每个分支后要有冒号，并且代码块需要缩进。例如：
  ```python
  score = 85
  if score >= 90:
      grade = "A"
  elif score >= 80:
      grade = "B"
  elif score >= 70:
      grade = "C"
  else:
      grade = "D"
  print(f"成绩等级：{grade}")
  ```
  逻辑运算符`and`、`or`、`not`可以组合多个条件。`and`要求所有条件为真，`or`要求至少一个为真，`not`取反。例如：
  ```python
  age = 20
  has_id = True
  if age >= 18 and has_id:
      print("允许进入")
  ```

  **`for`循环**用于遍历任何可迭代对象（如列表、字符串、字典的键）。基本语法：
  ```python
  for item in iterable:
      # 执行代码
  ```
  结合`range()`函数可以生成数字序列。`range(stop)`生成0到stop-1，`range(start, stop, step)`生成指定范围。例如：
  ```python
  for i in range(5):  # 0,1,2,3,4
      print(i)
  ```

  **`while`循环**在条件为真时重复执行代码块。必须确保循环条件最终变为假，否则会形成无限循环。例如：
  ```python
  count = 0
  while count < 5:
      print("计数：", count)
      count += 1
  ```

  **循环控制**：`break`立即退出整个循环，`continue`跳过当前迭代的剩余语句，进入下一次迭代。例如：
  ```python
  for num in range(10):
      if num == 5:
          break  # 遇到5就停止
      if num % 2 == 0:
          continue  # 偶数跳过
      print(num)  # 输出：1, 3
  ```

- **代码示例：**
  ```python
  # 猜数字游戏
  import random
  target = random.randint(1, 10)
  guess = None
  while guess != target:
      guess = int(input("猜一个1-10之间的数字："))
      if guess < target:
          print("太小了！")
      elif guess > target:
          print("太大了！")
  print("恭喜你猜对了！")
  ```

---

## 第三章 函数与模块

### 3.1 函数的定义与使用

- **学习目标：**
  - 理解函数的定义、参数与返回值
  - 掌握位置参数、默认参数、关键字参数
  - 了解变量的作用域（局部与全局）
  - 学会编写简单的自定义函数

- **讲义：**

  函数是组织好的、可重复使用的代码块，用于实现单一或相关联的功能。使用函数可以提高代码的模块性、可读性和可维护性。Python使用`def`关键字定义函数，基本语法：
  ```python
  def 函数名(参数列表):
      """文档字符串（可选）"""
      # 函数体
      return 返回值
  ```
  例如，定义一个计算两个数平均值的函数：
  ```python
  def average(a, b):
      """计算两个数的平均值"""
      result = (a + b) / 2
      return result

  avg = average(10, 20)
  print(avg)  # 输出 15.0
  ```

  **参数类型**：
  - **位置参数**：调用时按顺序传递。如 `average(10, 20)`。
  - **默认参数**：在定义时给参数一个默认值，调用时可以省略。注意默认参数必须指向不可变对象（如`None`、数字、字符串），避免陷阱。例如：
    ```python
    def greet(name, greeting="你好"):
        print(f"{greeting}，{name}！")
    greet("小明")  # 输出：你好，小明！
    greet("小红", "Hello")  # 输出：Hello，小红！
    ```
  - **关键字参数**：调用时通过参数名指定，可以忽略顺序。如 `greet(greeting="嗨", name="小华")`。

  **返回值**：函数使用`return`语句返回结果。如果没有`return`，函数默认返回`None`。一个函数可以返回多个值，实际是返回一个元组。例如：
  ```python
  def min_max(numbers):
      return min(numbers), max(numbers)

  min_val, max_val = min_max([3, 1, 4, 1, 5, 9])
  print(min_val, max_val)  # 输出 1 9
  ```

  **变量作用域**：在函数内部定义的变量是局部变量，只在函数内有效。在函数外部定义的变量是全局变量。函数内部可以读取全局变量，但修改全局变量需要使用`global`关键字。例如：
  ```python
  count = 0  # 全局变量
  def increment():
      global count
      count += 1
  increment()
  print(count)  # 输出 1
  ```

- **代码示例：**
  ```python
  # 计算圆的面积
  import math
  def circle_area(radius):
      """计算圆的面积"""
      return math.pi * radius ** 2

  area = circle_area(5)
  print(f"半径为5的圆面积为：{area:.2f}")

  # 多返回值函数
  def divide(a, b):
      quotient = a // b
      remainder = a % b
      return quotient, remainder

  q, r = divide(10, 3)
  print(f"商：{q}, 余数：{r}")
  ```

### 3.2 模块与包

- **学习目标：**
  - 理解模块的概念及其作用
  - 掌握`import`语句的多种用法
  - 学会使用标准库中的常用模块
  - 了解如何创建和使用自己的模块

- **讲义：**

  模块是一个包含Python定义和语句的文件，文件名就是模块名加上`.py`后缀。模块使得代码逻辑更加清晰，便于维护和复用。Python拥有一个庞大的标准库，提供了处理文件、网络、日期、数学等功能的模块。

  **导入模块**使用`import`语句，常见方式有：
  - `import 模块名`：导入整个模块，使用时需加上模块名作为前缀。如 `import math`，然后使用 `math.sqrt(16)`。
  - `from 模块名 import 特定函数`：导入模块中的特定函数，可以直接使用函数名。如 `from math import sqrt`，然后使用 `sqrt(16)`。
  - `from 模块名 import *`：导入模块所有公开内容（不推荐，可能导致命名冲突）。
  - `import 模块名 as 别名`：给模块起一个简短的别名。如 `import numpy as np`。

  **常用标准库模块示例**：
  - `math`：数学函数，如`sqrt`、`sin`、`pi`