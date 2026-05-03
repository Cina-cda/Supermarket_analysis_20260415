# -*- coding: utf-8 -*-
# src/inventory_advanced.py
"""进阶分析模块： 实现退货日期异常检查、库存线性插值补全"""

import pandas as pd
from src.config import START_DATE, END_DATE


def check_return_date_anomaly(sales: pd.DataFrame, returns: pd.DataFrame) -> int:
    """
    检查退货日期早于销售日期的异常记录数
    通过 sale_id 关联销售日期和退货日期，统计 return_date < sale_date 的行数
    返回：异常记录数
    """
    merged = (
        sales[['sale_id', 'sale_date']]
        .merge(returns[['sale_id', 'return_date']], on='sale_id')
    )
    anomaly_count = (merged['return_date'] < merged['sale_date']).sum()
    return anomaly_count


def interpolate_inventory(inventory: pd.DataFrame) -> pd.DataFrame:
    """
    补全每个门店-商品组合从 START_DATE 到 END_DATE 的所有日期，
    使用线性插值填充缺失的 stock_on_hand。
    返回：补全后的 DataFrame（包含所有日期，stock_on_hand 已插值）
    """
    full_date = pd.date_range(START_DATE, END_DATE, freq='D')

    def fill_dates_for_group(df):
        """对单个 (store_id, product_id) 分组，补全日期并插值"""
        store_id, product_id = df.name
        df = df.set_index('date').reindex(full_date)
        # 填充 store_id 和 product_id
        df['store_id'] = store_id
        df['product_id'] = product_id
        return df

    # 按门店和商品分组，应用补全函数
    inventory_full = (
        inventory
        .groupby(['store_id', 'product_id'])
        .apply(fill_dates_for_group)
        .reset_index(level=[0, 1], drop=True)  # 移除多余的索引层级
        .reset_index()              # 将 date 从索引变回列
    )
    # 线性插值填充 stock_on_hand
    inventory_full['stock_on_hand'] = (
        inventory_full
        .groupby(['store_id', 'product_id'])['stock_on_hand']
        .transform(lambda x: x.interpolate(method='linear'))
    )
    # 日期列更名
    inventory_full = inventory_full.rename(columns={'index': 'date'})

    return inventory_full