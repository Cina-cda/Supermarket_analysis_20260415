# -*- coding: utf-8 -*-
# src/report_exporter.py
"""Excel 报告导出模块： 生成多 sheet 格式化 Excel 文件"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from src.config import OUTPUT_DIR, EXCEL_FILE_PREFIX, FLOAT_DECIMALS, MAX_COL_WIDTH, EXCEL_INCLUDE_INDEX


def export_analysis(
    daily_net_sales_df: pd.DataFrame,
    top_return_df: pd.DataFrame,
    top_slow_turnover_df: pd.DataFrame,
    promotion_effect_df: pd.DataFrame,
    abc_class_df: pd.DataFrame
) -> Path:
    """
    将分析结果写入 Excel 文件，每个结果写入不同的 sheet，并应用格式。
    返回保存的文件路径。
    """
    # 生成文件名（当日日期）
    today = datetime.now().strftime('%Y%m%d')
    filename = f"{EXCEL_FILE_PREFIX}_{today}.xlsx"
    filepath = OUTPUT_DIR / filename

    # 使用 xlsxwriter 引擎
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        workbook = writer.book
        # 定义格式
        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top'})
        float_format = workbook.add_format({'num_format': f'0.{FLOAT_DECIMALS}'})

        def write_sheet(df: pd.DataFrame, sheet_name: str, index: bool = EXCEL_INCLUDE_INDEX):
            """写入一个 sheet 并自动调整列宽、设置数字格式"""
            df.to_excel(writer, sheet_name=sheet_name, index=index)
            worksheet = writer.sheets[sheet_name]
            # 确定需要处理的列数（包括索引列）
            start_col = 0
            num_cols = len(df.columns)
            if index:
                # 索引列作为第一列
                idx_name = df.index.name or ''
                idx_len = max(len(str(idx_name)), df.index.astype(str).map(len).max()) + 2
                worksheet.set_column(0, 0, min(idx_len, MAX_COL_WIDTH))
                start_col = 1
            # 处理数据列
            for i, col in enumerate(df.columns):
                col_letter = start_col + i
                # 计算列宽
                max_len = max(len(str(col)), df[col].fillna('').astype(str).map(len).max()) + 2
                # 判断是否为数值列，应用数字格式
                col_fmt = float_format if pd.api.types.is_numeric_dtype(df[col]) else None
                worksheet.set_column(col_letter, col_letter, min(max_len, MAX_COL_WIDTH), col_fmt)
            # 设置标题行格式
            worksheet.set_row(0, None, header_format)

        # 写入各个 sheet（根据 notebook 要求）
        write_sheet(daily_net_sales_df, '每日净销售额', index=False)
        write_sheet(top_return_df, '商品退货率Top5', index=False)
        write_sheet(top_slow_turnover_df, '周转最慢Top10商品', index=False)
        write_sheet(promotion_effect_df, '促销效果评估', index=False)
        write_sheet(abc_class_df, '商品ABC分类', index=False)

    return filepath