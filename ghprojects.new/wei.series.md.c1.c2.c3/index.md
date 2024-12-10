---
date: '2023-07-23T12:12:30Z'
description: Weibull series system estimation from data with censored lifetimes and
  masked component cause of failure.
forks: 0
languages:
- R
layout: project
links:
- name: GitHub
  url: https://github.com/queelius/wei.series.md.c1.c2.c3
- name: GitHub Pages
  url: https://queelius.github.io/wei.series.md.c1.c2.c3/
open_issues: 0
stars: 2
tags:
- GitHub
- project
title: wei.series.md.c1.c2.c3
---

Weibull series system estimation from data with censored lifetimes and masked component cause of failure.

**Stars**: 2 | **Forks**: 0 | **Open Issues**: 0

**Languages**: R

## Contributors
- queelius (24 commits)

## README

<!-- README.md is generated from README.Rmd. Please edit that file -->

# R package: `wei.series.md.c1.c2.c3`

A likelihood model for series systems with Weibull component lifetimes.
Accounts for right-censoring and candidate sets indicative of masked
failure causes.

## Related Publication

This library was developed to support the research presented in the
following paper:

  - “Reliability Estimation In Series Systems” -
    [GitHub](https://github.com/queelius/reliability-estimation-in-series-systems)

For detailed explanation and the scientific background behind the
methodologies implemented in this library, please refer to the paper.

<!-- badges: start -->

<!-- badges: end -->

## Installation

You can install the development version of `wei.series.md.c1.c2.c3` from
[GitHub](https://github.com/queelius/wei.series.md.c1.c2.c3) with:

``` r
# install.packages("devtools")
#devtools::install_github("queelius/wei.series.md.c1.c2.c3")
```

``` r
library(algebraic.dist)
#> Registered S3 method overwritten by 'algebraic.dist':
#>   method     from 
#>   print.dist stats
library(algebraic.mle)
library(wei.series.md.c1.c2.c3)
```

## Examples

``` r
# fit the model
fit <- mle_numerical(mle_lbfgsb_wei_series_md_c1_c2_c3(
  df = guo_weibull_series_md$data,
  theta0 = c(1,1,1,1,1,1),
  control = list(
    maxit = 1000L,
    parscale = c(1, 1000, 1, 1000, 1, 1000))))

cbind(confint(fit),
  "fit" = params(fit),
  "guo mle" = guo_weibull_series_md$mle)
#>               2.5%       97.5%        fit  guo mle
#> param1   0.5736164    1.941626   1.257621   1.2576
#> param2 352.9027030 1635.838014 994.370358 994.3661
#> param3   0.5633925    1.763536   1.163464   1.1635
#> param4 310.1187793 1507.798853 908.958816 908.9458
#> param5   0.6054160    1.656147   1.130782   1.1308
#> param6 322.5652746 1357.623486 840.094380 840.1141

# log-likelihood
c("guo log-like" = guo_weibull_series_md$loglike, "fit log-like" = loglik_val(fit))
#> guo log-like fit log-like 
#>    -228.6851    -228.6851
```

We see that they are approximately the same MLE fits.

``` r
shapes <- params(fit)[seq(1, length(params(fit)), 2)]
scales <- params(fit)[seq(2, length(params(fit)), 2)]
data.frame(
  "Component Cause" = wei_series_cause(1L:3L, shapes = shapes, scales = scales),
  "Component MTTF" = wei_mttf(shape = shapes, scale = scales))
#>   Component.Cause Component.MTTF
#> 1       0.2862058       924.8697
#> 2       0.3376112       862.1766
#> 3       0.3761829       803.5490

cat("System MTTF: ", wei_series_mttf(shapes = shapes, scales = scales))
#> System MTTF:  339.3773
```

``` r
(tq <- qwei_series(p = .825, shapes = shapes, scales = scales))
#> [1] 575.704
surv_wei_series(t = tq, shapes = shapes, scales = scales)
#> [1] 0.175
rwei_series(10L, shapes =shapes, scales = scales)
#>  [1]  95.53603 100.25772 282.05837 126.16159 425.90422  49.83648 130.02596
#>  [8] 742.51530  64.97421 147.28431
pwei_series(seq(1, 5, 1), shapes = shapes, scales = scales)
#> [1] 0.001024090 0.002293359 0.003675757 0.005136821 0.006658907
```

## Brief Overview

This package implements a likelihood model for Weibull series systems
from masked data, including functions for the log-likelihood, score, and
hessian of the log-likelihood. Analytical solutions are provided for the
log-likelihood and score functions, while the hessian is computed
numerically. The package is designed to handle two types of data: masked
component cause of failure data with exact failure time and
right-censored system lifetime data.

The masked component data should approximately satisfy certain
conditions. The conditions are as follows:

#### Condition 1

The component cause of failure is in the candidate set.

#### Condition 2

When we condition on the component cause of failure being any particular
cause in the canidate set and and the time of failure, the probability
of the given candidate set does not vary as we vary the component cause
of failure.

#### Condition 3

The masking probabilities are independent of the series system lifetime
parameter vector.

### API

As a loglikelihood model, we provide the following functions:

  - `loglik_wei_series_md_c1_c2_c3` for the log-likelihood
  - `score_wei_series_md_c1_c2_c3` for the score function
  - `hessian_wei_series_md_c1_c2_c3` for the hessian of the
    log-likelihood

For convenience, we also provide some wrappers around the `optim`
function to solve for the maximum likelihood estimates (MLE) of the
shape and scale parameters using the Nelder-Mead and simulated annealing
algorithms:

  - `mle_nelder_wei_series_md_c1_c2_c3` for the Nelder-Mead algorithm
  - `mle_sann_wei_series_md_c1_c2_c3` for the simulated annealing
    algorithm

Since we base some of our results and analysis on Guo, Szidarovszky, and
Niu (2013), we provide the data set from their paper, along with the
maximum likelihood estimates of the shape and scale parameters for the
Weibull series system. We also provide a function to solve for the MLE
using the Nelder-Mead algorithm:

  - `guo_weibull_series_md` for a model that generates data similar to
    Guo, Szidarovszky, and Niu (2013)
  - `guo_weibull_series_table_2` for the data from Table 2 in Guo,
    Szidarovszky, and Niu (2013)

We also provide a host of supporting functions and data tables, e.g., we
provide Weibull series system distribution function that honors the
established conventions in R:

  - `dwei_series` for the probability density function
  - `pwei_series` for the cumulative distribution function
  - `qwei_series` for the quantile function
  - `rwei_series` for random number generation

We also provide functions to compute the mean time to failure and the
component cause of failure for the Weibull series distribution, along
with the hazard and survival functions:

  - `wei_series_mttf` for the mean time to failure
  - `wei_series_cause` for the component cause of failure
  - `hazard_wei_series` for the hazard function
  - `surv_wei_series` for the survival function (this is normally done
    by passing lower.tail = FALSE to `pwei_series` but we provide a
    function)

Finally, we also provide some functions for working with the components
of the Weibull series system, e.g., we provide a function to compute the
hazard function for the Weibull component lifetimes:

  - `hazard_wei` for the hazard function of the Weibull component
    lifetimes
  - `wei_mttf` for the mean time to failure of the Weibull component
    lifetimes
