# 测试 Ruff 检查
import os, sys  # 多个导入在同一行（I001）
def bad_function():  # 函数名不符合 snake_case（N802）
    x = 1
    y = 2
    print("line too long" * 50)  # 行太长（E501）
    unused_var = 3  # 未使用的变量（F841）
