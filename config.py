# -*- coding: utf-8 -*-
# src/config.py
"""配置文件：定义路径、参数、常量，并自动创建所需目录"""

import os
from pathlib import Path

# ---------- 路径配置 ----------
# 项目根目录（config.py 位于 src 目录下，需取父目录）
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
SALES_FILE = DATA_DIR / "20260415sales.csv"
RETURNS_FILE = DATA_DIR / "20260415returns.csv"
INVENTORY_FILE = DATA_DIR / "20260415inventory.csv"

# 输出目录
OUTPUT_DIR = PROJECT_ROOT / "outputs"
EXCEL_FILE_PREFIX = "supermarket_analysis"  # 文件名会加上日期

# 自动创建目录
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- 分析参数 ----------
# 库存周转分析参数
START_DATE = '2022-01-01'
END_DATE = '2022-12-31'

# ABC 分类阈值（累计占比）
ABC_THRESHOLDS = [0.7, 0.9]  # A类 ≤70%，70%< B类 ≤90%，C类 >90%

# 退货率Top N
TOP_N_RETURN = 5

# 周转最慢Top N
TOP_N_SLOW = 10

# ---------- Excel 格式 ----------
# 数字保留小数位数
FLOAT_DECIMALS = 2

# 列宽最大限制
MAX_COL_WIDTH = 30

# 是否包含索引列（通常为False，除非特殊要求）
EXCEL_INCLUDE_INDEX = False