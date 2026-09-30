# Week 1 Teaching Guide - Statistical Learning for Data Science

## Problem Type 2 - Identify the learning paradigm

### Core knowledge

| Paradigm | Data available | Goal | Example |
|---|---|---|---|
| Supervised learning | Features `X` and response/label `Y` | Predict `Y` from `X` | price or spam prediction |
| Regression | Numeric `Y` | Predict a number | house value |
| Classification | Categorical `Y` | Predict a class | spam/not spam |
| Unsupervised learning | Inputs `X`, no `Y` | Find patterns, clusters, or latent structure | customer grouping |
| Semi-supervised learning | Few labelled, many unlabelled examples | Use both sets | image labelling |
| Active learning | Unlabelled pool and labelling access | Choose which points to label | send hard cases to an expert |
| Online learning | Data arrive continually | Update over time | streaming predictions |
| Reinforcement learning | Actions influence future state/input | Maximise long-run reward | control |
| Generative modelling | Data distribution/structure | Generate text, images, etc. | prompt-based generation |

Start every question with: **Is there a target `Y`? If yes, is it numeric or categorical?**

### Practice

1. **A bank predicts next month's spending amount. What is the task?**  
   **Answer:** Supervised regression.

2. **A music service groups listeners without known group labels. What is the task?**  
   **Answer:** Unsupervised learning, typically clustering.

3. **A system selects which images should be sent to an expert for labels. What is the task?**  
   **Answer:** Active learning.

---

## Problem Type 3 - Explain Statistical Learning, Machine Learning, and responsible data use

### Core knowledge

Statistical Learning and Machine Learning overlap and complement each other.

- **Statistical Learning** traditionally emphasises uncertainty, interpretability, sampling, experiments, surveys, and data collection.
- **Machine Learning** often emphasises predictive algorithms, computation, large data, and potentially black-box models.

Applications in the slides include image recognition, spam filtering, recommendation, autonomous vehicles, healthcare/sports/market analytics, anomaly detection, NLP, and generative AI.

### Practice

1. **Is a highly accurate black-box model automatically best?**  
   **Answer:** No. The decision may require interpretation, uncertainty, fairness, privacy, and robust data collection as well as accuracy.

2. **Name one issue a purely algorithmic workflow can overlook.**  
   **Answer:** Sampling/data-collection design, uncertainty quantification, consent, or group-level harms.

---

## Problem Type 4 - Fit regression, choose loss, and reason about generalisation

### Core knowledge

For data `(x_i,y_i)`, simple linear regression is

`y_i = beta_0 + beta_1 x_i + epsilon_i`.

The residual magnitude is `D_i = |y_i-beta_0-beta_1x_i|`. Least squares is **Empirical Risk Minimisation (ERM)** with

`R_n(beta_0,beta_1) = (1/n) sum_i (y_i-beta_0-beta_1x_i)^2`.

With `x_bar` and `y_bar`, the estimates are

`beta_hat_1 = sum_i (x_i-x_bar)(y_i-y_bar) / sum_i (x_i-x_bar)^2`

`beta_hat_0 = y_bar-beta_hat_1x_bar`.

The fitted line passes through `(x_bar,y_bar)`. The slope is the estimated change in fitted mean response for a one-unit increase in `x`.

The general relation is `y=f(x)+epsilon`: `f` may be linear, polynomial, logarithmic, a tree, random forest, or neural network. A loss should match the goal:

- Squared loss strongly penalises large errors.
- Absolute loss `sum |D_i|` is more robust to outliers but has no comparable simple closed-form solution.
- Other choices include relative error, RMSE, Huber loss, and quantile loss.

The target is **out-of-sample/generalisation error**, not only training error.

### Practice

1. **For `(1,2),(2,3),(3,5)`, find the fitted line.**  
   **Answer:** `x_bar=2`, `y_bar=10/3`, `S_xx=2`, `S_xy=3`; hence `y_hat=1/3+1.5x`.

2. **Why might absolute loss be preferable with extreme outliers?**  
   **Answer:** Its penalty grows linearly, so a single large residual has less influence than under squared loss.

3. **Why is the slope undefined if all `x_i` are equal?**  
   **Answer:** The denominator `sum (x_i-x_bar)^2` is zero; there is no variation in `x` to estimate a slope.

---

## Problem Type 5 - Classify observations and diagnose overfitting

### Core knowledge

For two classes BLUE and ORANGE, encode `y=0` and `y=1`. A simple threshold classifier predicts

`G_hat = BLUE` if `Y_hat <= 0.5`, otherwise `G_hat = ORANGE`.

For **k-nearest neighbours**, let `N_k(x)` be the set of `k` closest points. With 0/1 labels,

`Y_hat(x)=(1/k)sum_(i in N_k(x))y_i`, then apply the threshold.

The slides list LDA, QDA, Naive Bayes, logistic/probit regression, trees, SVMs, and k-NN. Common classification losses include 0-1, hinge, cross-entropy, and multiclass softmax/KL-related losses.

Flexible decision boundaries can fit complicated class structure, but can also fit noise. A model with low training error and high test error is **overfitting**. Some error can remain even for the best boundary when class distributions overlap.

### Practice

1. **If `Y_hat(x)=0.42`, what class is predicted using the stated rule?**  
   **Answer:** BLUE.

2. **The three nearest labels are `1,0,1`. What does 3-NN predict?**  
   **Answer:** The average is `2/3`, so class 1/ORANGE.

3. **Model A has training/test errors `1%/18%`; Model B has `4%/7%`. Which is preferred for new data?**  
   **Answer:** Model B; it has lower generalisation error. Model A overfits.

4. **Does lower training error prove a better model?**  
   **Answer:** No. Evaluate on independent unseen data with a relevant performance measure.

---

## Problem Type 6 - Use probability/statistics notation and descriptive statistics

### Core knowledge

**Probability** begins with a model and derives random behaviour. **Statistics** begins with real data, makes assumptions, and uses probability to infer properties of an unknown population distribution `F`.

A standard framework assumes `X_1,...,X_n` are i.i.d. from unknown `F`, then observes `x_1,...,x_n`.

- Random variable: uppercase `X,Y,Z`.
- Observation/realisation: lowercase `x,y,z`.
- Parameter: fixed but unknown population value.
- Statistic/estimator: function of the random sample.
- Estimate: numerical value of that statistic after observing data.

| Quantity | Population | Sample statistic |
|---|---|---|
| Mean | `mu_X=E[X]` | `x_bar=(1/n)sum x_i` |
| Variance | `sigma_X^2=Var(X)` | `s_x^2=(1/(n-1))sum(x_i-x_bar)^2` |
| Standard deviation | `sigma_X` | `s_x=sqrt(s_x^2)` |
| Covariance | `sigma_XY=E[(X-E[X])(Y-E[Y])]` | `s_xy=(1/(n-1))sum(x_i-x_bar)(y_i-y_bar)` |
| Correlation | `rho_XY=sigma_XY/(sigma_Xsigma_Y)` | `r_xy=s_xy/(s_xs_y)` |

### Practice

1. **In `X_i~Bernoulli(p)`, identify the parameter, estimator, and estimate of `p`.**  
   **Answer:** Parameter: `p`; estimator: `X_bar`; estimate: observed `x_bar`.

2. **Why does the displayed sample variance use `n-1`?**  
   **Answer:** It is the usual unbiased sample-variance estimator when the mean is estimated from the sample.

3. **Does correlation imply causation?**  
   **Answer:** No. It only measures association.

---

## Problem Type 7 - Assess a point estimator: bias, variance, MSE, and consistency

### Core knowledge

Inference may be **parametric** (assume a Normal, Exponential, Binomial, etc. family) or **non-parametric** (do not impose one specific parametric family). Its main tasks are point estimation, interval estimation, and hypothesis testing.

For an estimator `theta_hat_n` of parameter `theta`:

- `Bias(theta_hat_n)=E[theta_hat_n]-theta`.
- It is unbiased if bias is zero.
- `se(theta_hat_n)=sqrt(Var(theta_hat_n))`.
- `MSE(theta_hat_n)=E[(theta_hat_n-theta)^2]`.
- `MSE = Bias^2 + Variance`.

Weak consistency means `theta_hat_n -> theta` in probability; strong consistency means almost-sure convergence. A sufficient condition in the slides is that bias and standard error both tend to zero as `n` grows.

### Practice

1. **If `E[theta_hat]=theta+2` and `Var(theta_hat)=9`, find bias and MSE.**  
   **Answer:** Bias `=2`; MSE `=2^2+9=13`.

2. **Can a biased estimator have lower MSE than an unbiased one?**  
   **Answer:** Yes, if its variance reduction outweighs squared bias.

3. **If bias and standard error converge to zero, what follows?**  
   **Answer:** The estimator is weakly consistent under the theorem in the slides.

---

## Problem Type 8 - Construct a maximum likelihood estimator (MLE)

### Core knowledge

For density/mass `f(x|theta)` and i.i.d. observations `x_1,...,x_n`,

`L(theta)=f(x_1,...,x_n|theta)=product_i f(x_i|theta)`.

The MLE maximises the likelihood of the observed data. Usually optimise

`ell(theta)=log L(theta)`, because logarithms convert products to sums and preserve the maximiser. Differentiate, solve the first-order condition, check boundaries, and verify a maximum where needed.

For `X_i~Bernoulli(p)`,

`L(p)=product_i p^(x_i)(1-p)^(1-x_i)=p^(n x_bar)(1-p)^(n-n x_bar)`,

so `p_hat_MLE=x_bar`.

For `X_i~Normal(mu,sigma^2)`,

- `mu_hat_MLE=x_bar`;
- `sigma2_hat_MLE=(1/n)sum_i(x_i-x_bar)^2`.

The Normal variance MLE uses denominator `n`, so it is biased; do not confuse it with the `n-1` sample variance.

### Practice

1. **For Bernoulli data `1,1,1,0,1`, find the MLE of `p`.**  
   **Answer:** `p_hat=4/5`.

2. **Why use log-likelihood?**  
   **Answer:** It turns products into sums and gives the same maximiser.

3. **Is likelihood itself a posterior probability distribution over `theta`?**  
   **Answer:** No. With data fixed, it is a function of `theta`, not a normalised probability distribution over `theta`.

---

## Problem Type 9 - Compare estimators using the German tank problem and R simulation

### Core knowledge

The German tank problem models serial numbers as a discrete uniform population with upper limit `N`. Candidate estimators in the slides include:

1. `x_bar+3s`
2. `2x_bar-1`
3. `x_(n)` (sample maximum)
4. `x_(n)+x_(1)-1`
5. `((n+1)/n)x_(n)-1`

The point is to compare estimators through their sampling distributions: bias, variability, and MSE. A single observed sample cannot establish that one estimator is generally best.

For the slide sample `588,601,126,699,464,468,258,440,275,320`, the estimates displayed are approximately `960, 847, 699, 824, 768`; the slide states true `N=735`.

R simulation repeats samples. Across simulations, `mean(estimates)` estimates the estimator's expected value, `sd(estimates)` its variability, and `mean(estimates)-N` its empirical bias. A histogram shows the sampling distribution.

### Practice

1. **Why does the sample maximum usually underestimate `N`?**  
   **Answer:** A finite sample may miss the largest population serial numbers.

2. **Is the closest estimate in one simulation necessarily the best estimator?**  
   **Answer:** No. Compare expected bias, variance, and MSE over repeated samples.

3. **What does `mean(estimates)-N` estimate in a simulation?**  
   **Answer:** Empirical bias.

---

## Problem Type 10 - Build and interpret a confidence interval for a proportion

### Core knowledge

For independent `X_i~Bernoulli(p)`, the sample proportion `X_bar` estimates `p`. LLN says `X_bar` converges in probability to `p`. For large `n`, CLT says

`sqrt(n)(X_bar-p)/sqrt(p(1-p)) -> Normal(0,1)`,

so `X_bar` is approximately `Normal(p,p(1-p)/n)`.

An approximate `(1-alpha)100%` interval is

`X_bar +/- z_(alpha/2)sqrt(p(1-p)/n)`.

Since `p(1-p)<=1/4`, the conservative interval in the slides is

`X_bar +/- z_(alpha/2)/(2sqrt(n))`.

For 80 right turns in 124 couples, `x_bar=80/124=0.645`. At 95%, `z_(0.025)=1.96`, giving the conservative interval approximately `[0.56,0.73]`.

Correct interpretation: if the sampling-and-interval procedure were repeated many times, about 95% of resulting intervals would contain the fixed parameter. It is not a 95% probability statement about the fixed parameter after the data are observed. Use CLT carefully for very small samples; the slides mention Hoeffding bounds as a further option.

### Practice

1. **What is `x_bar` for 80 successes in 124 trials?**  
   **Answer:** Approximately `0.645`.

2. **What is the conservative 95% margin for `n=124`?**  
   **Answer:** `1.96/(2sqrt(124))`, approximately `0.088`.

3. **Give the correct interpretation of a 95% confidence interval.**  
   **Answer:** About 95% of intervals from repeated use of the same procedure cover the fixed true parameter.

---

## Problem Type 11 - Conduct and interpret a two-sided proportion test

### Core knowledge

For the head-turning study, test `H_0:p=1/2` against `H_1:p != 1/2`. At level `alpha`, the slide's CLT rule rejects `H_0` if

`|X_bar-1/2| > z_(alpha/2)/(2sqrt(n))`.

With `n=124`, `x_bar=0.645`, and `alpha=0.05`:

- observed deviation: `|0.645-0.5|=0.145`;
- threshold: `1.96/(2sqrt(124))≈0.088`;
- conclusion: reject `H_0` at the 5% level.

`alpha` is the intended probability of Type I error, rejecting a true null under the assumptions. Rejecting `H_0` is evidence against it, not absolute proof of an alternative. Failing to reject is not accepting `H_0`.

The slides also name Student's t distribution/t-test, chi-squared distribution and independence test, and F distribution/F-test as topics to explore. The t distribution is heavier-tailed than Normal and has degrees of freedom; F is non-negative and has two degrees-of-freedom parameters.

### Practice

1. **Should `H_0:p=0.5` be rejected in the head-turning example at 5%?**  
   **Answer:** Yes, because `0.145>0.088`.

2. **What does “fail to reject `H_0`” mean?**  
   **Answer:** There is insufficient evidence against `H_0` at that level; it does not prove `H_0` true.

3. **What is a Type I error?**  
   **Answer:** Rejecting a true null hypothesis.

---

## Problem Type 12 - Critique i.i.d. assumptions, fairness, privacy, and ethics

### Core knowledge

`i.i.d.` means independent and identically distributed. It is a modelling assumption, not an automatic property of a dataset. Repeated measurements on one person, time dependence, distribution drift, and non-representative sampling can violate it.

Models are only as good as their data. Ask whether privacy is protected, consent is adequate, data leaks are addressed, groups are represented fairly, and harms/benefits are distributed acceptably. These concerns affect data validity, model generalisation, and whether deployment is appropriate.

### Practice

1. **Why can daily purchases from the same ten customers violate i.i.d.?**  
   **Answer:** The same customer's behaviour and adjacent days may be dependent, and the distribution can change over time.

2. **A model has high overall accuracy but poor performance for an under-represented group. What should be checked?**  
   **Answer:** Group-level performance, representation, label quality, sampling, decision harms, privacy, and a suitable fairness goal.

3. **Can better optimisation alone repair an unrepresentative dataset?**  
   **Answer:** No. The data-collection and representation process must also be addressed.

---

## Final revision checklist

A student should be able to:

1. Identify the paradigm from a verbal scenario.
2. Write the least-squares objective and calculate a simple fitted line.
3. Distinguish training error from test/generalisation error.
4. Explain k-NN and classify from neighbouring labels.
5. Distinguish random variables, observations, parameters, estimators, statistics, and estimates.
6. Calculate/compare bias, variance, MSE, and consistency.
7. Recall or derive Bernoulli MLE and distinguish MLE variance from unbiased sample variance.
8. Build and correctly interpret a large-sample confidence interval.
9. State hypotheses and make a reject/fail-to-reject decision.
10. Explain why i.i.d., data quality, fairness, privacy, and ethics matter.
