#!/usr/bin/env python3
"""
金融术语数据转换脚本
将万条金融标准术语.csv转换为系统标准格式
"""

import csv
import os
from pathlib import Path

def convert_financial_terms():
    """转换金融术语文件"""
    
    # 文件路径
    input_file = "万条金融标准术语.csv"
    output_file = "backend/data/financial_terms_full.csv"
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 读取输入文件并转换
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # 写入标准头部
        writer.writerow(['conceptId', 'fsn', 'domainId', 'active', 'effectiveTime', 'moduleId', 'definitionStatusId'])
        
        concept_id = 1000001
        
        for row in reader:
            if len(row) >= 1 and row[0].strip():  # 确保有内容
                term = row[0].strip()
                if term and term != 'FINTERM':  # 跳过类型标识符
                    writer.writerow([
                        concept_id,
                        term,
                        'finance',
                        1,
                        '20240101',
                        '900000000000012004',
                        '900000000000074008'
                    ])
                    concept_id += 1
    
    print(f"转换完成！共处理了 {concept_id - 1000001} 个金融术语")
    print(f"输出文件: {output_file}")

if __name__ == "__main__":
    convert_financial_terms() 