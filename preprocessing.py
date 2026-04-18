# -*- coding: utf-8 -*-
# src/preprocessing.py
"""数据预处理模块： 进行缺失值填充、异常值处理、添加计算列"""

import pandas as pd


def clean_sales(sales: pd.DataFrame) -> pd.DataFrame:
    """
    处理 sales 表：
        1. discount 缺失填充为 0
        2. 删除 quantity <= 0 或 unit_price <= 0 的行
        3. 添加计算列 net_sales = quantity * unit_price * (1 - discount)
    """
    df = sales.copy()
    # 填充折扣缺失
    df['discount'] = df['discount'].fillna(0)
    # 删除异常行
    df = df[(df['quantity'] > 0) & (df['unit_price'] > 0)]
    # 添加净销售额列
    df['net_sales'] = df['quantity'] * df['unit_price'] * (1 - df['discount'])
    return df


def clean_returns(sales: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    """
    处理 returns 表：
        1. 删除 return_quantity 缺失或 <=0 的行
        2. 填充 refund_amount 缺失：
            - 优先通过 sale_id 关联 sales 表的 unit_price 计算
            - 无法关联时用该商品当天所有销售的平均单价（按 return_date 和 product_id 分组）
            - 若当天无销售则用全局平均单价
        3. 添加 return_value 列（等于 refund_amount）
    """
    df = returns.copy()
    # 删除无效退货数量
    df = df[df['return_quantity'].notna() & (df['return_quantity'] > 0)]

    # 构建 price_map (sale_id -> unit_price)
    price_map = sales[['sale_id', 'unit_price']].drop_duplicates('sale_id').set_index('sale_id')['unit_price']
    df['sales表中的单价'] = df['sale_id'].map(price_map)
    df['关联sale表填充的退款额'] = df['sales表中的单价'] * df['return_quantity']

    mask = df['关联sale表填充的退款额'].isna()
    if mask.any():
        # 计算每日每商品平均单价
        daily_avg = sales.groupby(['sale_date', 'product_id'])['unit_price'].mean().reset_index(name='平均单价')
        # 合并需要填充的行
        merged = (
            df.loc[mask, ['return_date', 'product_id', 'return_quantity']]
            .merge(daily_avg, left_on=['return_date', 'product_id'], right_on=['sale_date', 'product_id'], how='left')
        )
        merged['用当天的平均单价填充的退款额'] = merged['平均单价'] * merged['return_quantity']
        global_avg = sales['unit_price'].mean()
        if pd.isna(global_avg):
            global_avg = 0
        merged['用当天的平均单价填充的退款额'] = merged['用当天的平均单价填充的退款额'].fillna(global_avg * merged['return_quantity'])
        df.loc[mask, '关联sale表填充的退款额'] = merged['用当天的平均单价填充的退款额'].values

    df['refund_amount'] = df['refund_amount'].fillna(df['关联sale表填充的退款额'])
    df = df.drop(columns=['sales表中的单价', '关联sale表填充的退款额'])

    # 添加 return_value 列（等于 refund_amount）
    df['return_value'] = df['refund_amount']

    return df


def handle_return_exceeds_sales(sales: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    """
    处理退货数量超过销售数量的异常：
        通过 sale_id 关联 sales 表，若 return_quantity > quantity 则截断为 quantity，
        并重新计算 refund_amount = return_quantity * unit_price
    """
    # 合并销售信息
    returns_with_sales = returns.merge(
        sales[['sale_id', 'quantity', 'unit_price']],
        on='sale_id',
        how='left'
    )
    valid_mask = returns_with_sales['quantity'].notna()
    exceed_mask = valid_mask & (returns_with_sales['return_quantity'] > returns_with_sales['quantity'])
    if exceed_mask.any():
        returns_with_sales.loc[exceed_mask, 'return_quantity'] = returns_with_sales.loc[exceed_mask, 'quantity']
        returns_with_sales.loc[exceed_mask, 'refund_amount'] = (
            returns_with_sales.loc[exceed_mask, 'return_quantity'] * returns_with_sales.loc[exceed_mask, 'unit_price']
        )
        returns_with_sales.loc[exceed_mask, 'return_value'] = returns_with_sales.loc[exceed_mask, 'refund_amount']
    # 只保留原 returns 的列，顺序不变
    return returns_with_sales[returns.columns]


def clean_inventory(inventory: pd.DataFrame) -> pd.DataFrame:
    """
    处理 inventory 表：
        删除 stock_on_hand < 0 的行
    """
    df = inventory.copy()
    df = df[df['stock_on_hand'] >= 0]
    return df


def preprocess_all(sales: pd.DataFrame, returns: pd.DataFrame, inventory: pd.DataFrame):
    """
    执行全部预处理流程，返回清洗后的三个 DataFrame
    """
    # 清洗销售表
    sales_clean = clean_sales(sales)
    # 清洗退货表（先填充缺失退款金额，再处理超过销售数量的情况）
    returns_clean = clean_returns(sales_clean, returns)
    returns_clean = handle_return_exceeds_sales(sales_clean, returns_clean)
    # 清洗库存表
    inventory_clean = clean_inventory(inventory)
    return sales_clean, returns_clean, inventory_clean