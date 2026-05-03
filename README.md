# 超市销售与库存分析

## 项目简介

本项目对超市销售、退货和库存数据进行全面的清洗、分析与报表生成。严格按照业务逻辑实现以下功能：

- 数据清洗：缺失值多级填充、异常值删除、退货超量截断
- 指标计算：门店每日净销售额、商品退货率、库存周转天数、促销效果评估、商品ABC分类
- 进阶分析：退货日期异常检测、库存线性插值补全（完整日期序列）
- 报告输出：生成格式化的 Excel 报告（多 Sheet、自动列宽、数字格式）

采用 **混合模式**（核心函数封装为 `.py` 模块，主流程在 Jupyter Notebook 中交互式执行），兼顾工程化复用与结果展示的便捷性。

## 项目结构
### supermarket_analysis/
### │
### ├── data/ # 原始数据（需自行放置）
#### │ ├── YYYYMMDDsales.csv
#### │ ├── YYYYMMDDreturns.csv
#### │ └── YYYYMMDDinventory.csv
### │
### ├── src/ # 核心 Python 模块
#### │ ├── config.py # 配置（路径、参数）
#### │ ├── data_loader.py # 数据加载与时间转换
#### │ ├── preprocessing.py # 缺失值、异常值处理，计算列
#### │ ├── metrics.py # 业务指标计算
#### │ ├── inventory_advanced.py # 进阶分析（退货异常、库存插值）
#### │ └── report_exporter.py # Excel 报告生成（含格式）
### │
#### ├── main_analysis.ipynb # 主 Notebook：导入模块、执行分析、展示结果
### │
### ├── outputs/ # 运行后自动生成
#### │ └── supermarket_analysis_YYYYMMDD.xlsx
### │
#### ├── requirements.txt # Python 依赖
#### ├── README.md # 本文件


## 环境要求

- Python 3.12+
- 依赖库：pandas, numpy, xlsxwriter

## 快速开始

### 1. 克隆或下载项目

### 2. 安装依赖
pip install -r requirements.txt

### 3. 准备数据
将原始数据文件放入 data/ 目录：

YYYYMMDDsales.csv

YYYYMMDDreturns.csv

YYYYMMDDinventory.csv

### 4. 运行分析
打开 main_analysis.ipynb，依次执行所有单元格（或点击 “Run All”）。

### 5. 查看结果
控制台会打印各分析步骤的中间结果。

Excel 报告保存在 outputs/ 目录下，文件名格式 supermarket_analysis_YYYYMMDD.xlsx。

#### 输出说明
Excel 文件包含以下工作表：

每日净销售额：	         各门店每日的净销售总额

商品退货率 Top5：	     退货率最高的5个商品及销售/退货数量

周转最慢 Top10 商品：	 按门店+商品计算的库存周转天数（最大）

促销效果评估：	         促销日 vs 非促销日平均日销售额对比

商品 ABC 分类：	       基于销售额累计占比的 ABC 分类

每个工作表均自动调整列宽、标题加粗、数字保留两位小数。

### 参数配置
所有可调参数集中在 src/config.py 中，例如：

START_DATE, END_DATE：库存插值的日期范围

ABC_THRESHOLDS：ABC 分类的累计占比阈值

TOP_N_RETURN、TOP_N_SLOW：Top N 数量

FLOAT_DECIMALS：Excel 数字小数位数

### 扩展与定制
如需增加新指标，可在 metrics.py 中添加函数，并在主 Notebook 中调用。

如需修改报告格式，调整 report_exporter.py 中的 write_sheet 函数。

所有分析均可通过命令行脚本自动化（例如编写 run.py 调用 src 模块）。

### 注意事项
原始数据文件必须放在 data/ 目录下，且文件名与代码中一致（或修改 config.py 中的文件名常量）。

库存插值会生成完整日期序列，计算量随数据量增长。

退货率计算时，仅考虑既有销售又有退货的商品（inner join）。

### 许可证
本项目仅供学习和交流使用。
