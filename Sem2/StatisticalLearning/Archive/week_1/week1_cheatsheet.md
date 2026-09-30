# Cheatsheet - Week 1: Statistical Learning for Data Science

> Phạm vi: Introduction to Statistical Learning và Statistics Review. Ký hiệu theo slide; dùng `x` cho giá trị quan sát và `X` cho biến ngẫu nhiên.

## 1. Bức tranh lớn

**Statistical learning** là học từ dữ liệu. Một quy trình điển hình:

`đặt câu hỏi -> thu thập dữ liệu -> chọn biểu diễn/mô hình -> fit -> đánh giá trên dữ liệu mới -> diễn giải và ra quyết định`.

| Statistical Learning | Machine Learning |
|---|---|
| Nhấn mạnh mô hình hóa bất định, diễn giải, thiết kế khảo sát/thí nghiệm và chất lượng dữ liệu. | Thường nhấn mạnh hiệu năng dự báo, thuật toán và dữ liệu quy mô lớn; có thể dùng mô hình "hộp đen". |
| Hai lĩnh vực chồng lấp và bổ sung cho nhau. Trong môn học này, ta đứng ở giữa hai cách nhìn. | |

**Dữ liệu quyết định giới hạn của mô hình.** Cần cân nhắc fairness, privacy, consent, rò rỉ dữ liệu, quyền được quên và việc sử dụng tác phẩm/dữ liệu để huấn luyện generative AI.

## 2. Chọn loại bài toán học

| Paradigm | Dữ liệu có gì? | Mục tiêu | Ví dụ |
|---|---|---|---|
| Supervised learning | Features/input `X` và nhãn/response `Y` | Học quan hệ để dự báo `Y` | giá nhà, spam |
| Regression | `Y` định lượng | Dự đoán một số thực | giá nhà, PSA |
| Classification | `Y` định tính/nhãn lớp | Dự đoán lớp | spam/không spam, chữ số |
| Unsupervised learning | Chỉ có `X`, không có `Y` | Khám phá cấu trúc, cluster, latent representation, giảm chiều | phân khúc khách hàng, gene expression |
| Semi-supervised | Ít dữ liệu có nhãn, nhiều dữ liệu không nhãn | Tận dụng cả hai loại | gán nhãn ảnh đắt đỏ |
| Active learning | Có pool không nhãn | Chủ động chọn điểm nào cần gán nhãn | hỏi chuyên gia cho ca khó nhất |
| Online learning | Dữ liệu/prediction đến liên tục | Cập nhật theo thời gian | click stream |
| Reinforcement learning | Hành động ảnh hưởng trạng thái/dữ liệu tương lai | Tối ưu phần thưởng dài hạn | điều khiển/khuyến nghị |
| Generative modeling | Học phân phối/cấu trúc dữ liệu | Sinh text, ảnh... từ prompt | LLM, image generation |

**Câu hỏi chẩn đoán:** Có nhãn `Y` không? Nếu có, `Y` là số hay nhãn? Nếu không, ta muốn tìm cấu trúc nào?

## 3. Regression và Empirical Risk Minimization (ERM)

Với dữ liệu huấn luyện `(x_i, y_i), i = 1, ..., n`, mô hình tuyến tính đơn:

`y_i ≈ beta_0 + beta_1 x_i`.

- Residual/sai số tại điểm `i`: `D_i = |y_i - beta_0 - beta_1 x_i|`.
- **Squared loss / empirical risk:**

  `R_n(beta_0, beta_1) = (1/n) sum_i (y_i - beta_0 - beta_1 x_i)^2`.

- **Least squares** chọn `beta_0, beta_1` làm nhỏ nhất `R_n`:

  `beta_hat_1 = sum_i (x_i - x_bar)(y_i - y_bar) / sum_i (x_i - x_bar)^2`

  `beta_hat_0 = y_bar - beta_hat_1 x_bar`.

### Loss không phải chỉ có squared loss

| Loss/metric | Ý nghĩa chính |
|---|---|
| Squared error | Phạt mạnh lỗi lớn; dẫn đến least squares. |
| Least absolute deviation: `sum |D_i|` | Ít nhạy outlier hơn; thường không có nghiệm đóng đơn giản. |
| RMSE | Cùng đơn vị với `Y`; là căn bậc hai của trung bình squared error. |
| Relative error | Hợp lý khi độ lớn tương đối quan trọng. |
| Huber, quantile loss | Lựa chọn robust hoặc khi cần dự báo quantile. |

**Đừng đồng nhất “linear” với “least squares”.** Ta có thể đổi dạng hàm `f(x)` (polynomial, log, tree, random forest, neural network) và/hoặc đổi loss. Mô hình tổng quát: `y = f(x) + epsilon`.

**Mục tiêu cuối không phải training error:** cần **out-of-sample/generalization error** - lỗi trên dữ liệu mới cùng cơ chế sinh dữ liệu.

## 4. Classification

Với hai lớp BLUE/ORANGE có thể mã hóa `y in {0, 1}`. Một cách đơn giản là fit điểm số `Y_hat(x)`, rồi threshold:

`G_hat(x) = BLUE nếu Y_hat(x) <= 0.5; ORANGE nếu Y_hat(x) > 0.5`.

### k-Nearest Neighbors (k-NN)

- `N_k(x)`: tập `k` hàng xóm gần nhất của `x`.
- Với nhãn 0/1: `Y_hat(x) = (1/k) sum_{i in N_k(x)} y_i`.
- Phân lớp bằng threshold 0.5.
- `k` nhỏ: boundary linh hoạt, dễ overfit. `k` lớn: boundary mượt hơn, có thể underfit.

### Nhóm mô hình và loss thường gặp

- Generative: LDA, QDA, Naive Bayes.
- Discriminative: logistic regression, probit/link functions, SVM, tree, k-NN.
- Loss: 0-1 loss, hinge loss, cross-entropy; đa lớp thường dùng softmax/cross-entropy (liên hệ KL loss).

### Overfitting

Mô hình quá linh hoạt có thể học cả tín hiệu lẫn nhiễu: training error thấp nhưng test error cao. Đánh giá phải tách dữ liệu train/test (và sau này dùng validation/cross-validation); độ phức tạp mô hình là một trade-off, không phải mặc định “càng phức tạp càng tốt”.

## 5. Probability vs. Statistics

- **Probability:** xuất phát từ một mô hình xác suất đã cho, suy ra tính chất của biến ngẫu nhiên/dữ liệu mô phỏng.
- **Statistics:** xuất phát từ dữ liệu thực, đặt giả định để nối dữ liệu với mô hình xác suất, rồi kết luận về population.
- **Learning:** dùng dữ liệu để hiểu hiện tượng hoặc dự báo; không phải lúc nào cũng cần giả định xác suất tường minh.

Khung cơ bản trong thống kê:

1. Giả sử `X_1, ..., X_n` là i.i.d. từ phân phối chưa biết `F`.
2. Quan sát realization `x_1, ..., x_n`.
3. Suy luận về `F`, tham số của `F`, hoặc các functional như mean/median/variance.

`i.i.d.` = independent and identically distributed: độc lập và cùng phân phối. Đây là **giả định**, cần đánh giá tính hợp lý theo cách dữ liệu được sinh/thu thập.

## 6. Ký hiệu và descriptive statistics

| Đối tượng population (random) | Từ mẫu (statistic) | Ý nghĩa |
|---|---|---|
| `mu_X = E[X]` | `x_bar = (1/n) sum x_i` | mean |
| `sigma_X^2 = Var(X)` | `s_x^2 = (1/(n-1)) sum (x_i - x_bar)^2` | variance |
| `sigma_X` | `s_x = sqrt(s_x^2)` | standard deviation |
| `sigma_XY = E[(X-E[X])(Y-E[Y])]` | `s_xy = (1/(n-1)) sum (x_i-x_bar)(y_i-y_bar)` | covariance |
| `rho_XY = sigma_XY/(sigma_X sigma_Y)` | `r_xy = s_xy/(s_x s_y)` | correlation |

- **Random variable** dùng chữ hoa (`X`); **realization/observation** dùng chữ thường (`x`).
- **Parameter**: đại lượng population cố định nhưng chưa biết, ví dụ `theta`, `mu`, `p`.
- **Statistic**: hàm của dữ liệu ngẫu nhiên, ví dụ `X_bar`.
- **Estimate**: giá trị statistic sau khi đã quan sát một mẫu, ví dụ `x_bar`.

> Mẫu variance trong slide dùng mẫu số `n - 1`; đừng nhầm với MLE variance của Normal, vốn có mẫu số `n`.

## 7. Statistical inference

### Parametric và non-parametric

- **Parametric:** giả sử họ phân phối (Normal, Exponential, Binomial...), rồi ước lượng parameter. Có thể theo frequentist hoặc Bayesian.
- **Non-parametric:** không khóa dữ liệu vào một họ tham số cố định; ước lượng trực tiếp từ dữ liệu nhiều hơn.

Ba mục tiêu cốt lõi:

1. **Point estimation:** một giá trị `theta_hat`.
2. **Interval estimation:** khoảng thể hiện độ bất định.
3. **Hypothesis testing:** kiểm tra dữ liệu có mâu thuẫn đủ mạnh với một giả thuyết không.

### Chất lượng estimator

Với estimator `theta_hat_n` cho parameter `theta`:

- Bias: `Bias(theta_hat_n) = E[theta_hat_n] - theta`.
- Unbiased nếu bias bằng 0.
- Standard error: `se(theta_hat_n) = sqrt(Var(theta_hat_n))`.
- Mean squared error: `MSE(theta_hat_n) = E[(theta_hat_n - theta)^2]`.
- Phân rã quan trọng: `MSE = Bias^2 + Variance`.
- Consistency: `theta_hat_n -> theta` khi `n -> infinity` (weak: in probability; strong: almost surely). Một điều kiện đủ trong slide: bias và standard error đều tiến về 0.

**Diễn giải:** estimator không bias chưa chắc tốt nếu variance lớn; estimator hơi bias có thể có MSE nhỏ hơn. Đây là phiên bản inference của bias-variance trade-off.

## 8. Maximum Likelihood Estimation (MLE)

Giả sử mật độ/xác suất một điểm là `f(x | theta)` và mẫu i.i.d. `x_1, ..., x_n`.

- Likelihood: `L(theta) = product_i f(x_i | theta)`.
- MLE: `theta_hat = argmax_theta L(theta)`.
- Thường tối ưu log-likelihood `ell(theta) = log L(theta) = sum_i log f(x_i | theta)` vì product thành sum.
- Giải `d ell(theta)/d theta = 0`, kiểm tra miền tham số và điều kiện cực đại (ví dụ đạo hàm bậc hai).

### Ví dụ Bernoulli

Nếu `X_i ~ Bernoulli(p)`, với `x_i in {0,1}`:

`L(p) = product p^{x_i}(1-p)^{1-x_i} = p^{n x_bar}(1-p)^{n - n x_bar}`

=> `p_hat_MLE = x_bar` (tỷ lệ mẫu).

## 9. LLN, CLT, confidence interval và hypothesis test

### Luật số lớn (LLN)

Với Bernoulli i.i.d., `X_bar -> p` (in probability). Vì vậy tỷ lệ mẫu là estimator hợp lý cho `p` khi `n` lớn, nhưng LLN không tự cho biết độ gần ở mẫu hữu hạn.

### Central Limit Theorem (CLT)

Với Bernoulli khi `n` đủ lớn:

`sqrt(n) (X_bar - p) / sqrt(p(1-p)) -> N(0,1)`

xấp xỉ: `X_bar ~ Normal(p, p(1-p)/n)`.

### Confidence interval (CI) cho tỷ lệ

CI xấp xỉ `(1-alpha)100%`:

`p in [x_bar - z_(alpha/2) sqrt(p(1-p)/n), x_bar + z_(alpha/2) sqrt(p(1-p)/n)]`.

Vì `p(1-p) <= 1/4`, khoảng bảo thủ trong slide:

`p in [x_bar - z_(alpha/2)/(2 sqrt(n)), x_bar + z_(alpha/2)/(2 sqrt(n))]`.

Với 95%, `z_(0.025) = 1.96`. Công thức xấp xỉ CLT không đáng tin ở mẫu rất nhỏ; khi đó cân nhắc phương pháp exact/bounds (slide nhắc Hoeffding bound).

**Diễn giải đúng 95% CI theo frequentist:** nếu lặp lại quy trình lấy mẫu và dựng khoảng rất nhiều lần, khoảng 95% các khoảng sẽ chứa `p`. Không nói rằng parameter cố định có “95% xác suất” nằm trong khoảng sau khi đã quan sát mẫu.

### Hypothesis test hai phía cho `H_0: p = 1/2`

Ở mức `alpha`, xấp xỉ CLT cho quy tắc bác bỏ:

`|x_bar - 1/2| > z_(alpha/2)/(2 sqrt(n))`.

- `alpha` là mức ý nghĩa: xác suất xấp xỉ bác bỏ sai `H_0` khi `H_0` đúng (Type I error).
- **Reject `H_0`** không đồng nghĩa đã chứng minh `H_1` đúng tuyệt đối.
- **Fail to reject `H_0`** không đồng nghĩa `H_0` đúng; có thể sample/power chưa đủ.

Ví dụ slide: 80/124 quay phải, `x_bar = 0.645`; ngưỡng 5% xấp xỉ `1.96/(2 sqrt(124)) ≈ 0.088`. Vì `|0.645 - 0.5| = 0.145 > 0.088`, bác bỏ `H_0` ở mức 5%.

## 10. Ví dụ German tank: tư duy đánh giá estimator

Serial number được giả sử Uniform rời rạc trên `{1, ..., N}` (slide mô tả `{0, ..., N}` nhưng code lấy mẫu `1:T`); từ sample không hoàn lại, so sánh nhiều estimator `N_hat`.

Điểm cần học không phải thuộc từng estimator mà là:

1. Từ **cùng một dữ liệu**, có nhiều cách ước lượng parameter.
2. Cần đánh giá **bias**, **variance/SE**, và **MSE**, không chỉ xem một lần chạy.
3. Simulation lặp lại nhiều mẫu cho thấy phân phối sampling của estimator.
4. Estimator maximum thường underestimate `N`; estimator điều chỉnh theo cỡ mẫu có thể giảm bias nhưng tăng variance.

## 11. Checklist giải bài Week 1

1. Viết rõ target và đơn vị quan sát; phân biệt `X` với `x`.
2. Xác định paradigm: supervised/unsupervised; regression/classification nếu có nhãn.
3. Nêu giả định dữ liệu (đặc biệt i.i.d. và family distribution nếu có).
4. Viết model/estimator và loss hoặc likelihood.
5. Tính estimate; kiểm tra miền tham số và đơn vị.
6. Đánh giá: training vs test error cho prediction; bias/SE/MSE/CI/test cho inference.
7. Diễn giải bằng câu trả lời cho câu hỏi thực tế, kèm giới hạn/độ bất định.

## 12. Các lỗi dễ nhầm

- Nhầm correlation với causation.
- Gọi `x_bar` là parameter: `x_bar` là statistic/estimate; `mu` mới là parameter population.
- Chỉ báo training error rồi khẳng định model tốt.
- Dùng CLT mù quáng khi mẫu quá nhỏ hoặc quan sát không độc lập.
- Diễn giải CI như xác suất của parameter cố định.
- Không phân biệt **estimate** (số sau khi quan sát) và **estimator** (hàm ngẫu nhiên của sample).
- Bỏ qua data collection: dữ liệu lệch, chất lượng thấp hoặc thiếu consent không được “sửa” hoàn toàn bằng mô hình.
