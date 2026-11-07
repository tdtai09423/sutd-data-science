# Hình và bảng tổng hợp

Tạo hình sau khi pipeline chính chạy xong:

```bash
pipeline/.venv/bin/python visualize/make_visuals.py
```

Script đọc kết quả từ `pipeline/outputs/` và `pipeline/data/processed/`, sau đó ghi hình vào
`visualize/figures/` và bảng số liệu chính vào `visualize/key_results.csv`. Hình so sánh mô hình
chỉ dùng giai đoạn development (2016-2021). Hình holdout 2022 được tách riêng; không dùng kết
quả holdout để chọn mô hình.

## Thiết kế

* **Dữ liệu:** DF theo tuần, Singapore, 2012-2022. DHF được giữ riêng vì số ca thấp.
  Thời tiết gồm mưa/nhiệt độ của trạm NEA/MSS Changi S24 và độ ẩm từ Open-Meteo.
* **Surge:** threshold A, seasonal p90 S, growth B và các biến thể onset-only A/S; horizon 1, 2,
  4 tuần.
* **Mô hình:** seasonal/persistence baselines; logistic, lasso logistic, CART, random forest,
  Poisson GLM và ridge log-count.
* **Đánh giá:** rolling-origin theo tuần, development 2016-2021, holdout cuối kỳ 2022; PR-AUC,
  recall, precision, calibration/Brier và số báo động mỗi năm. CI PR-AUC dùng bootstrap theo
  block 26 tuần.

## Kết quả chính (h = 1, `key_results.csv`)

| Target | Dương tính dev | Persistence | Mô hình tốt nhất (dev) | PR-AUC [95% CI] | 2022: dương tính, persistence / mô hình |
|---|---|---|---|---|---|
| A threshold | 43 | 0.93 | Poisson GLM | 0.93 [0.78, 0.98] | 20, 0.98 / 0.97 |
| S seasonal | 44 | 0.97 | ridge log-count | 0.98 [0.77, 1.00] | 27, 0.98 / 0.97 |
| G growth | 36 | 0.17 | ridge log-count | 0.26 [0.15, 0.40] | 8, 0.14 / 0.31 |
| A-onset | 7 | 0.30 | Poisson GLM | 0.32 [0.04, 0.80] | 2, 0.42 / 0.23 |
| S-onset | 5 | 0.26 | ridge log-count | 0.89 [0.70, 1.00] | 2, 0.58 / 1.00 |

Diễn giải:

1. Với A và S, persistence đã đạt PR-AUC khoảng 0.93–0.97, không mô hình nào thắng rõ. Đây là
   nhận biết tình hình hiện tại, chưa phải cảnh báo sớm.
2. Hồi quy đếm (count regression) có ích cho growth và S-onset, nhưng S-onset chỉ có 5 sự kiện.
3. Thời tiết đơn lẻ yếu (0.34 / 0.16 / 0.13, gần base rate). Thêm thời tiết vào số ca cũng không
   cải thiện.
4. Ví dụ dự báo sai (failure case): ở mốc 2022-07-04, mô hình báo động (P = 0.52, dự báo 1.383 ca),
   nhưng thực tế chỉ có 918 ca vì dịch đã đạt đỉnh.

## Các hình đầu ra

| File | Nội dung |
|---|---|
| `01_cases_and_surge_definitions.png` | Chuỗi DF, định nghĩa surge và DHF riêng |
| `02_pr_auc_ci_h1.png` | PR-AUC development cùng CI, horizon 1 |
| `03_pr_auc_vs_persistence_all_targets.png` | So sánh PR-AUC và persistence trên mọi target |
| `04_pr_auc_by_horizon.png` | PR-AUC theo horizon |
| `05_calibration_h1.png` | Calibration của các mô hình development |
| `06_alarm_tradeoff_h1.png` | Recall so với số báo động/năm theo cost ratio |
| `07_pr_auc_by_year_h1.png` | Mức ổn định theo năm; 2022 được đánh dấu riêng |
| `08_top_features_h1.png` | Hệ số lasso và mức quan trọng RF |
| `09_reporting_delay_sensitivity.png` | Nhạy cảm với giả định trễ báo cáo 1 tuần |
| `10a-c_eda_*.png` | Mùa vụ, tương quan trễ, ca bệnh-thời tiết |
| `11_model_best_*_h1.png` | Xác suất dự báo theo thời gian của mô hình tốt nhất trên development |
| `12_final_test_holdout_h1.png` | Mô hình được chọn trên development so với baselines ở 2022 |

Diễn giải kết quả, số liệu CI, giới hạn và cảnh báo về việc đã xem các exploratory run đến
2022 cần được đọc cùng báo cáo chính; không suy luận hiệu quả triển khai chỉ từ các hình.
