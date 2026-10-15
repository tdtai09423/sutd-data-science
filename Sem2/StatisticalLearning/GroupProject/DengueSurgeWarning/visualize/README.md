# Visualize: kết quả theo đề 1.1 của thầy

Tạo lại (sau `cd pipeline && python run.py all`):
```bash
pipeline/.venv/bin/python visualize/make_visuals.py
```

## Thiết kế (bám theo đề)
- **Chuỗi target:** Dengue Fever (DF) theo tuần, 2012–2022. DHF để riêng (dưới 1 ca/tuần, chỉ mô tả).
- **Định nghĩa surge** (chốt trước khi fit), h = 1 là chính:
  - **A threshold:** y[t+h] > mean + 2·sd của 52 tuần trước.
  - **S seasonal p90:** y[t+h] > percentile thứ 90 của cùng mùa (±2.5 tuần) ở các năm trước (gợi ý của thầy).
  - **B growth:** y[t+h] ≥ (1+pct)·y[t] và ≥ 50 ca (week-on-week rise).
  - **A-onset / S-onset:** như A/S nhưng chỉ xét tuần mà y[t] **chưa** vượt ngưỡng, tức cảnh báo sớm thật sự.
- **Baselines:** prior, seasonal (tỷ lệ surge lịch sử theo tuần trong năm), persistence (khoảng cách hiện tại tới ngưỡng).
- **Mô hình:** logistic (cases / weather / cả hai), lasso logistic (chọn C bằng CV theo thời gian), CART depth 3,
  random forest, Poisson GLM, ridge trên log counts. Hồi quy đếm được đổi thành P(surge).
- **Validation:** rolling-origin theo tuần, expanding window, test 2017–2022, refit mỗi 4 tuần (`refit_every`),
  purge h tuần. Báo động khi P ≥ 0.2 (bỏ lỡ một surge tốn gấp 4 lần một báo động giả).
- **Metric:** PR-AUC kèm khoảng tin cậy 95% (block bootstrap 26 tuần), recall, precision, số báo động/năm,
  Brier, calibration.

## Kết quả chính (`key_results.csv`, h = 1)
| Target | Dương tính (test) | Persistence | Mô hình tốt nhất | PR-AUC [95% CI] |
|---|---|---|---|---|
| A threshold | 58 | 0.96 | logistic, cases | 0.94 [0.86, 0.98] |
| S seasonal p90 | 61 | 0.97 | ridge log counts | 0.98 [0.91, 1.00] |
| B growth | 42 | 0.17 | ridge log counts | 0.26 [0.19, 0.42] |
| A-onset | 8 | 0.30 | ridge log counts | 0.30 [0.06, 0.78] |
| S-onset | 7 | 0.51 | Poisson GLM | 0.94 [0.88, 1.00] |

## Diễn giải (dùng cho phần defence)
1. **A và S dự báo được gần như hoàn hảo, nhưng chủ yếu nhờ persistence.** Một tuần đang vượt ngưỡng thì tuần
   sau gần như chắc chắn vẫn vượt. Không mô hình nào thắng persistence một cách rõ ràng
   (`p_better_than_persistence` thấp, hình 02, 03).
2. **Giá trị thật nằm ở onset:** khi dịch *chưa* vượt ngưỡng, hồi quy đếm (Poisson GLM, ridge log)
   phát hiện các tuần chớm vượt ngưỡng S tốt hơn hẳn persistence (PR-AUC 0.94 so với 0.51 ở h = 1,
   0.64–0.74 ở h = 2–4). **Nhưng chỉ có 7–16 ca dương tính**, nên khoảng tin cậy rất rộng.
   Đây chính là ý "limited number of large outbreaks" trong đề.
3. **B growth khó:** mọi mô hình chỉ đạt PR-AUC 0.2–0.33. Ở h = 2–4, seasonal baseline ngang ngửa mô hình tốt nhất.
4. **Thời tiết đơn lẻ yếu:** gần mức prior cho A và S. Thêm thời tiết vào số ca không cải thiện A/S, chỉ giúp chút ít
   cho B ở h = 4 và S-onset ở h = 4.
5. **Mô hình đơn giản là đủ:** logistic trên số ca và hồi quy đếm ≥ random forest và CART.
6. **Trễ báo cáo 1 tuần** (hình 09): PR-AUC giảm vừa phải (A: 0.94 → 0.88 với logistic cases),
   kết luận không đổi.
7. **Chi phí báo động giả** (hình 06): với tỷ lệ 4:1, A/S có khoảng 11–13 báo động/năm với recall ≈ 0.75–0.8.
   Còn B cần khoảng 13–20 báo động/năm mà chỉ bắt được khoảng một nửa số surge.

## Danh sách hình (`figures/`)
| File | Nội dung |
|---|---|
| 01_cases_and_surge_definitions.png | Chuỗi DF + 3 định nghĩa surge + onset (vòng đen) + DHF |
| 02_pr_auc_ci_h1.png | PR-AUC kèm CI, h = 1, so với persistence và no-skill |
| 03_pr_auc_vs_persistence_all_targets.png | Heatmap PR-AUC và mức hơn/kém persistence, mọi target |
| 04_pr_auc_by_horizon.png | PR-AUC theo horizon cho từng định nghĩa |
| 05_calibration_h1.png | Reliability diagram (mô hình tốt nhất, persistence, seasonal) |
| 06_alarm_tradeoff_h1.png | Recall và số báo động/năm theo tỷ lệ chi phí 1:1 → 9:1 |
| 07_pr_auc_by_year_h1.png | Độ ổn định theo năm test (2020: serotype DENV-3) |
| 08_top_features_h1.png | Biến quan trọng (lasso, RF) |
| 09_reporting_delay_sensitivity.png | Độ nhạy khi trễ báo cáo 1 tuần |
| 10a–c_eda_*.png | Mùa vụ, tương quan có độ trễ với thời tiết |
| 11_model_best_*_h1.png | Xác suất dự báo out-of-sample của mô hình tốt nhất |

## Việc còn lại
- Chạy phân tích chính trên dataset MOH 2014–2018 + thời tiết NEA (đề yêu cầu); 2012–2022 làm robustness.
- Chạy bản cuối với `refit_every: 1` (khoảng 30 phút).
