# Visualize: kết quả chạy trên dữ liệu thật (Iteration 0 → 3)

Tạo lại toàn bộ (sau khi chạy `cd pipeline && python run.py all`):
```bash
pipeline/.venv/bin/python visualize/make_visuals.py
```

## Dữ liệu
- Ca bệnh: MOH Weekly Infectious Disease Bulletin, Dengue Fever + DHF, 574 tuần (2012-W01 → 2022-W52), không thiếu tuần nào.
- Thời tiết: Open-Meteo (Singapore), gộp theo tuần, 2011-06 → 2026-10.
- Năm dịch lớn: 2013, 2014, 2019, **2020 (đỉnh 1792 ca/tuần)**, 2022. Năm thấp: 2017, 2018, 2021.

## Cấu hình đã chốt (config.yaml)
| | Định nghĩa | Tham số | Prevalence h=1/2/4 |
|---|---|---|---|
| A threshold | y[t+h] > mean + k·sd của 52 tuần trước | k = 2.0 (1.5 cho ~23%) | 0.19 / 0.19 / 0.20 |
| B growth | y[t+h] ≥ (1+pct[h])·y[t] và ≥ 50 ca | pct = 0.25 / 0.30 / 0.45 | 0.12 / 0.17 / 0.18 |

CV: rolling-origin theo năm, test 2017–2022, purge h tuần. Metric chính: PR-AUC (mức no-skill = prevalence).

## Kết quả chính (`key_results.csv`)
| Target | Mô hình tốt nhất | PR-AUC | Baseline "z-score tuần hiện tại" |
|---|---|---|---|
| A, h=1 | Poisson GLM → alarm | 0.94 | **0.96** |
| A, h=2 | Poisson GLM → alarm | 0.86 | **0.92** |
| A, h=4 | Logistic (chỉ biến ca bệnh) | 0.82 | **0.85** |
| B, h=1 | Poisson GLM → alarm | 0.29 | (prior 0.11) |
| B, h=2 | Random forest | 0.27 | (prior 0.15) |
| B, h=4 | Lasso logistic | 0.33 | (prior 0.21) |

## Diễn giải
1. **Target A gần như "persistence"**: tuần đang vượt ngưỡng thì vài tuần sau vẫn vượt. Một quy tắc ngây thơ
   (cảnh báo khi z-score tuần hiện tại cao) thắng mọi mô hình. → Muốn A có ý nghĩa cảnh báo sớm, cần đổi
   thành **"onset"**: y[t] chưa vượt ngưỡng nhưng y[t+h] vượt (bước tiếp theo đề xuất).
2. **Target B khó**: mọi mô hình chỉ hơn baseline một chút (PR-AUC 0.27–0.33 so với 0.11–0.21); ROC-AUC ~0.62–0.66.
   Tăng trưởng ngắn hạn rất nhiễu.
3. **Thời tiết đơn lẻ không có tín hiệu** cho A (PR-AUC = prevalence), có chút tín hiệu cho B ở h=4
   (khớp với độ trễ sinh học muỗi/virus ~2–3 tháng; tương quan mạnh nhất ở lag 10–12 tuần, xem 04b).
4. Mô hình đơn giản (logistic chỉ dùng lag ca bệnh, Poisson GLM) ≥ mô hình phức tạp (RF, GBM, tree).
   Tree depth-3 kém nhất nhưng có luật dễ đọc (`pipeline/outputs/tables/tree_rules.txt`).
5. Ở ngưỡng p ≥ 0.5, nhiều classifier cho target B không bao giờ báo động (recall = 0) → cần chọn ngưỡng
   theo tỷ lệ báo động / tối ưu F1 trên tập train.

## Danh sách hình (`figures/`)
| File | Nội dung |
|---|---|
| 01_cases_and_surge_labels.png | Chuỗi ca bệnh 2012–2022 + tuần được gán surge theo A và B |
| 02_pr_auc_heatmap.png | PR-AUC của mọi mô hình × target (bảng tổng hợp chính) |
| 03_pr_auc_by_horizon.png | PR-AUC theo horizon, so với no-skill và baseline persistence |
| 04a_eda_seasonality.png | Mùa vụ theo tuần trong năm |
| 04b_eda_weather_lag_corr.png | Tương quan ca bệnh với thời tiết theo lag |
| 04c_eda_cases_vs_weather.png | Ca bệnh và thời tiết theo thời gian |
| 05_pr_auc_by_year.png | PR-AUC theo từng năm test (độ ổn định) |
| 06_top_features_h2.png | Biến quan trọng nhất (lasso và RF), h=2 |
| 07a/07b_best_model_*.png | Xác suất dự báo của mô hình tốt nhất trên giai đoạn test |

## Việc tiếp theo đề xuất
- Thêm target A-onset (loại tuần đã đang vượt ngưỡng) và baseline persistence vào `modeling.py`.
- Chọn ngưỡng báo động theo dữ liệu train thay vì cố định 0.5.
- Negative binomial GLM (statsmodels) thay Poisson do overdispersion.
