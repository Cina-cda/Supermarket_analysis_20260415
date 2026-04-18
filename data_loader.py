# -*- coding: utf-8 -*-
# src/data_loader.py
"""数据加载模块： 取三个 CSV 并转换日期列为 datetime"""

import pandas as pd
from src.config import SALES_FILE, RETURNS_FILE, INVENTORY_FILE

# 单独加载
def load_sales() -> pd.DataFrame:
    """读取销售数据，将 sale_date 转换为 datetime"""
    df = pd.read_csv(SALES_FILE)
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    return df


def load_returns() -> pd.DataFrame:
    """读取退货数据，将 return_date 转换为 datetime"""
    df = pd.read_csv(RETURNS_FILE)
    df['return_date'] = pd.to_datetime(df['return_date'])
    return df


def load_inventory() -> pd.DataFrame:
    """读取库存数据，将 date 转换为 datetime"""
    df = pd.read_csv(INVENTORY_FILE)
    df['date'] = pd.to_datetime(df['date'])
    return df

# 批量加载
def load_all_data():
    """一次性加载所有数据，返回元组 (sales, returns, inventory)"""
    return load_sales(), load_returns(), load_inventory()