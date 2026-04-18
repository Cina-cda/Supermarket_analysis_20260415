# -*- coding: utf-8 -*-
# src/metrics.py
"""核心指标模块： 计算每日净销售额、退货率、库存周转、促销效果、ABC分类"""

import pandas as pd
import numpy as np
from src.config import ABC_THRESHOLDS, TOP_N_RETURN, TOP_N_SLOW, START_DATE, END_DATE


def daily_net_sales(sales: pd.DataFrame) -> pd.DataFrame:
    """
    计算各门店每日净销售额
    返回: DataFrame 列 ['store_id', 'sale_date', 'daily_net_sales']
    """
    result = (
        sales.groupby(['store_id', 'sale_date'])['net_sales']
        .sum()
        .reset_index(name='daily_net_sales')
    )
    return result


def product_return_rate(sales: pd.DataFrame, returns: pd.DataFrame, top_n: int = TOP_N_RETURN) -> pd.DataFrame:
    """
    计算商品退货率，返回退货率最高的 top_n 个商品
    返回: DataFrame 列 ['product_id', 'total_sales_qty', 'total_return_qty', 'return_rate']
    """
    # 每个商品总销售数量
    sales_qty = sales.groupby('product_id')['quantity'].sum().reset_index(name='销售数量')
    # 每个商品总退货数量
    return_qty = returns.groupby('product_id')['return_quantity'].sum().reset_index(name='退货数量')
    # 合并
    merged = pd.merge(sales_qty, return_qty, on='product_id', how='inner')
    merged['return_rate'] = (merged['退货数量'] / merged['销售数量'] * 100).round(2)
    merged = merged.sort_values('return_rate', ascending=False).head(top_n)
    # 格式化输出
    merged['return_rate'] = merged['return_rate'].astype(str) + '%'
    merged.rename(columns={'销售数量': 'total_sales_qty', '退货数量': 'total_return_qty'}, inplace=True)
    return merged[['product_id', 'total_sales_qty', 'total_return_qty', 'return_rate']]


def inventory_turnover(sales: pd.DataFrame, inventory: pd.DataFrame, top_n: int = TOP_N_SLOW) -> pd.DataFrame:
    """
    计算库存周转天数（按门店+商品），返回周转最慢的 top_n 个商品
    使用月末库存均值作为平均库存，全年销售总数量 / 平均库存 = 周转次数，周转天数 = 365 / 周转次数
    返回: DataFrame 包含 store_id, product_id, 平均库存, 全年销量, 周转次数, 周转天数
    """
    # 辅助函数：计算单个门店-商品组合的平均库存（月末均值）
    def avg_inventory_for_group(df):
        df = df.set_index('date').sort_index()
        # 重采样到月末，取最后一个有效值
        monthly = df['stock_on_hand'].resample('ME').last()
        # 填充缺失（前向后向）
        monthly = monthly.ffill().bfill()
        return monthly.mean()

    avg_inv = (
        inventory.groupby(['store_id', 'product_id'])
        .apply(avg_inventory_for_group, include_groups=False)
        .reset_index(name='平均库存')
    )
    # 计算每个门店-商品全年总销量
    annual_sales = sales.groupby(['store_id', 'product_id'])['quantity'].sum().reset_index(name='全年销量')
    # 合并
    merged = pd.merge(avg_inv, annual_sales, on=['store_id', 'product_id'], how='inner')
    merged['周转次数'] = merged['全年销量'] / merged['平均库存']
    merged['周转天数'] = 365 / merged['周转次数']
    # 排序取 top_n（周转天数最大）
    result = merged.sort_values('周转天数', ascending=False).head(top_n)
    return result


def promotion_effect(sales: pd.DataFrame) -> pd.DataFrame:
    """
    促销效果评估：比较促销日（discount > 0）与非促销日（discount == 0）的平均每日净销售额
    返回: DataFrame 列 ['store_id', 'net_sales促销日', 'net_sales非促销日', '是否有效']
    """
    # 计算促销日日均销售额（先按日聚合再求平均）
    promo_daily = sales[sales['discount'] > 0].groupby(['store_id', 'sale_date'])['net_sales'].sum().reset_index()
    promo_avg = promo_daily.groupby('store_id')['net_sales'].mean().reset_index(name='net_sales促销日')
    # 非促销日日均销售额
    non_promo_daily = sales[sales['discount'] == 0].groupby(['store_id', 'sale_date'])['net_sales'].sum().reset_index()
    non_promo_avg = non_promo_daily.groupby('store_id')['net_sales'].mean().reset_index(name='net_sales非促销日')
    # 合并
    result = pd.merge(promo_avg, non_promo_avg, on='store_id', how='outer').fillna(0)
    result['是否有效'] = result.apply(lambda row: '有效' if row['net_sales促销日'] > row['net_sales非促销日'] else '无效', axis=1)
    return result


def abc_classification(sales: pd.DataFrame, thresholds: list = None) -> pd.DataFrame:
    """
    ABC 分类：基于商品全年净销售额累计占比
    thresholds: [A类上限, B类上限]，默认 [0.7, 0.9]
    返回: DataFrame 列 ['product_id', '销售额', '类别']
    """
    if thresholds is None:
        thresholds = ABC_THRESHOLDS
    # 计算每个商品总销售额
    product_sales = sales.groupby('product_id')['net_sales'].sum().reset_index(name='销售额')
    product_sales = product_sales.sort_values('销售额', ascending=False)
    # 累计占比
    product_sales['累计销售额'] = product_sales['销售额'].cumsum()
    total = product_sales['销售额'].sum()
    product_sales['累计消费占比'] = product_sales['累计销售额'] / total
    # 打标签
    product_sales['类别'] = 'B 类'  # 默认
    product_sales.loc[product_sales['累计消费占比'] <= thresholds[0], '类别'] = 'A 类'
    product_sales.loc[product_sales['累计消费占比'] > thresholds[1], '类别'] = 'C 类'
    return product_sales[['product_id', '销售额', '类别']]