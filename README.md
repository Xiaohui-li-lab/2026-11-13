# Information-Processing Modes Determine the Architecture and Outcome of Aggressive Wars

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Replication package for the paper:

> **Information-Processing Modes Determine the Architecture and Outcome of Aggressive Wars**  
> Xiaohui Li (Independent Researcher, Baoji, China)  
> ORCID: 0009-0003-8233-7191  
> Correspondence: danceluck@163.com

Data homepage: https://github.com/xiaohui-li-lab/

## Abstract

This repository contains all data, code, and materials needed to reproduce the results 
reported in the paper. We introduce the Information-Granularity Theory (IGT) and test it 
using (i) an agent-based model (ABM), (ii) a historical benchmark based on the Correlates 
of War (COW) and V-Dem datasets, (iii) ABM calibration to seven historical wars, and 
(iv) extensive sensitivity analyses.

## Data Requirements

Three external datasets are required. Please download them and place the CSV files in the 
`data/` directory.

| Dataset | Version | Source | Filename |
|---|---|---|---|
| COW Inter-State War Data | v4.0 | https://correlatesofwar.org/data-sets/COW-war/ | `Inter-StateWarData_v4.0.csv` |
| COW National Material Capabilities | v6.0 | https://correlatesofwar.org/data-sets/national-material-capabilities/ | `NMC_Data_v6.0.csv` |
| V-Dem | v12 Country-Year | https://v-dem.net/data/the-v-dem-dataset/ | `V-Dem-CY-Core-v12.csv` |

## Installation

```bash
# Clone the repository
git clone https://github.com/xiaohui-li-lab/2026-11-13.git
cd information-granularity-war

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt



xiaohui-li-lab/2026-1-13/
├── README.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── .gitignore
├── data/
│   ├── README.md
│   ├── Inter-StateWarData_v4.0.csv          # 需下载
│   ├── NMC_Data_v6.0.csv                     # 需下载
│   └── V-Dem-CY-Core-v12.csv                 # 需下载
├── code/
│   ├── __init__.py
│   ├── 01_build_igi.py                       # 构建 IGI 指数
│   ├── 02_real_data_analysis.py              # 真实数据回归与绘图
│   ├── 03_abm_simulation.py                  # 基于主体模型
│   ├── 04_abm_calibration.py                 # 历史案例校准
│   ├── 05_sensitivity_analysis.py            # 敏感性分析
│   ├── 06_run_all.py                         # 一键运行
│   └── utils.py                              # 工具函数
├── output/
│   ├── figure_1_concept.png                  # 由 LaTeX 生成
│   ├── figure_2_simulation.png
│   ├── figure_3_real_data.png
│   ├── figure_4_calibration.png
│   ├── figure_5_sensitivity.png
│   ├── regression_table.csv
│   ├── sensitivity_table.csv
│   └── calibration_table.csv
├── latex/
│   ├── paper_en_final.tex
│   ├── paper_en_final.pdf                    # 编译后生成
│   └── nature_cover_letter.tex
└── docs/
    ├── supplementary_materials.pdf
    └── response_to_reviewers_template.md
