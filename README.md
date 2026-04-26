# Week 9: ARIA v6.0 - Matai'an Barrier Lake Analysis

## 📋 專案概述

這是一個使用 ARIA v6.0 (Advanced Rapid Imaging and Analysis) 管道進行 Matai'an 水壩潰決災害分析的專案。專案使用 Sentinel-2 衛星影像進行變化偵測、精度評估和災害影響評估。

## 🎯 主要目標

- **光譜指數計算**: 計算 NDVI、NDWI、BSI 等光譜指數
- **變化偵測**: 使用 ΔNDVI 進行災害前後變化偵測
- **精度評估**: 基於驗證點進行定量精度評估
- **閾值優化**: 找出最佳的變化偵測閾值
- **災害影響分析**: 評估災害影響範圍和程度

## 📁 專案結構

```
week9ex/
├── week9.ipynb              # 主要分析筆記本
├── .env                     # 環境變數配置
├── data/                    # 資料目錄
│   └── validation_points.geojson  # 驗證點資料
├── output/                   # 輸出結果目錄
├── fix_validation_week9.py   # 驗證點載入修正
├── real_task3_execution.py  # 真實資料 Task 3 執行
├── env_integration.py        # 環境變數整合
└── README.md               # 本檔案
```

## 🚀 快速開始

### 1. 環境設定

確保已安裝必要的套件：

```bash
pip install numpy pandas matplotlib geopandas rasterio
pip install stackstac planetarycomputer pystac
pip install scikit-learn seaborn
```

### 2. 環境變數配置

複製並編輯 `.env` 檔案：

```env
# 研究區域邊界框
MATAIAN_BBOX=[121.20, 23.60, 121.40, 23.80]

# 事件日期範圍 (2025年)
PRE_EVENT_START=2025-06-01
PRE_EVENT_END=2025-07-15
MID_EVENT_START=2025-08-01
MID_EVENT_END=2025-09-20
POST_EVENT_START=2025-09-25
POST_EVENT_END=2025-11-15

# API 金鑰 (如需要)
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. 執行分析

#### 方法一：在 Jupyter Notebook 中執行

```python
# 1. 執行 Task 1 (光譜分析)
task1_real_results = execute_task1_with_real_data()

# 2. 載入修正的驗證點
exec(open('fix_validation_week9.py').read())

# 3. 執行 Task 3 (精度評估)
exec(open('real_task3_execution.py').read())
results = execute_real_task3_workflow(task1_real_results)
```

#### 方法二：使用整合函數

```python
# 載入環境整合
exec(open('env_integration.py').read())

# 執行完整流程
results = create_complete_task_workflow()
```

## 📊 核心功能

### 🔍 Task 1: 光譜指數與變化偵測

- **雲層遮罩**: 使用 SCL 分類進行穩健雲層偵測
- **光譜指數**: 計算 NDVI、NDWI、BSI
- **變化圖**: 生成 ΔNDVI、ΔNDWI、ΔBSI 差異圖
- **交集遮罩**: 確保所有時期的有效像素

### 📈 Task 2: 閾值優化

- **閾值掃描**: 測試多個閾值 (-0.1 到 -0.5)
- **精度指標**: 計算 F1-score、Producer's Accuracy、User's Accuracy
- **自動選擇**: 找出 F1-score 最高的最佳閾值

### 🎯 Task 3: 精度評估

- **驗證點載入**: 支援多種標註類型 (lake, stable, landslide 等)
- **混淆矩陣**: 生成 2x2 混淆矩陣
- **統計評估**: 計算整體精度、Kappa 係數等指標
- **視覺化**: 生成綜合評估圖表

## 🔧 修正與最佳化

### 驗證點修正 (`fix_validation_week9.py`)

處理驗證點中的字串標註：

```python
# 支援的標註類型
truth_mapping = {
    'lake': 1,        # 湖泊 = 變化
    'stable': 0,      # 穩定 = 無變化
    'landslide': 1,   # 山崩 = 變化
    'erosion': 1,     # 侵蝕 = 變化
    'flood': 1,       # 洪水 = 變化
    'water': 1,       # 水體 = 變化
    'land': 0,        # 土地 = 無變化
    'vegetation': 0,  # 植被 = 無變化
    'forest': 0,      # 森林 = 無變化
    'agriculture': 0, # 農業 = 無變化
    'urban': 0,       # 都市 = 無變化
}
```

### 環境變數整合 (`env_integration.py`)

- **動態日期**: 從環境變數載入日期範圍
- **雲層權重**: Mid 期間 10x 權重優先
- **場景評分**: 綜合雲層覆蓋率和日期距離評分

### 真實資料執行 (`real_task3_execution.py`)

- **真實 Sentinel-2**: 使用實際衛星影像資料
- **驗證檢查**: 確保使用真實資料而非假資料
- **綜合視覺化**: 6 個子圖的完整評估報告

## 📈 輸出結果

### 影像輸出

- `output/task1_change_detection.png` - 變化偵測圖
- `output/task1_real_composites.png` - 真實合成影像
- `output/task1_real_ndwi.png` - NDWI 水體偵測
- `output/task3_real_accuracy_assessment.png` - 精度評估圖

### 統計結果

- **變化偵測統計**: 變化像素數量和百分比
- **精度指標**: 整體精度、精確度、召回率、F1-score
- **混淆矩陣**: TP、FP、TN、FN 詳細數據
- **最佳閾值**: F1-score 最高的閾值值

## 🛠️ 故障排除

### 常見問題

1. **驗證點載入錯誤**
   ```
   Error: invalid literal for int() with base 10: 'lake'
   ```
   **解決**: 使用 `fix_validation_week9.py` 中的修正函數

2. **NameError: task1_results not defined**
   ```
   NameError: name 'task1_results' is not defined
   ```
   **解決**: 先執行 Task 1 或使用 `real_task3_execution.py`

3. **Final change map 看起來像假資料**
   **解決**: 確保使用 `task1_real_results` 而非假資料

### 除錯步驟

1. 檢查環境變數是否正確設定
2. 確認網路連線可用於 STAC API
3. 驗證驗證點檔案存在且格式正確
4. 檢查輸出目錄權限

## 📚 技術細節

### 資料來源

- **衛星**: Sentinel-2 L2A
- **解析度**: 10 公尺
- **光譜波段**: B02 (Blue), B03 (Green), B04 (Red), B08 (NIR), B11 (SWIR)
- **雲層分類**: Scene Classification Layer (SCL)

### 分析方法

- **NDVI**: (NIR - Red) / (NIR + Red)
- **NDWI**: (Green - NIR) / (Green + NIR)
- **BSI**: ((Red + SWIR) - (NIR + Blue)) / ((Red + SWIR) + (NIR + Blue))

### 精度評估

- **Producer's Accuracy**: TP / (TP + FN) - 漏報率
- **User's Accuracy**: TP / (TP + FP) - 虛警率
- **F1-Score**: 2 × (Precision × Recall) / (Precision + Recall)
- **Kappa 係數**: 一致性評估指標

## 🤝 貢獻與引用

### 主要工具

- **Planetary Computer**: Microsoft STAC API
- **GeoPandas**: 地理空間資料處理
- **Rasterio**: 檔案格式讀取
- **Stackstac**: STAC 資料堆疊
- **Scikit-learn**: 機器學習指標

### ARIA v6.0 管道

本專案實作 ARIA v6.0 管道標準：
- 穩健的雲層遮罩
- 多時相變化偵測
- 定量精度評估
- 操作決策支援

## 📞 聯絡與支援

如有問題或建議，請：
1. 檢查本 README 的故障排除部分
2. 確認所有必要套件已正確安裝
3. 驗證環境變數設定正確

---

**專案狀態**: ✅ 完整實作並測試通過  
**最後更新**: 2025-04-27  
**版本**: ARIA v6.0 - Week 9 Implementation
