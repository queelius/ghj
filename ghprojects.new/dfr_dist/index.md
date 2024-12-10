---
date: '2023-06-16T09:56:38Z'
description: Dynamic failure rate distributions (DFR)
forks: 0
languages:
- R
layout: project
links:
- name: GitHub
  url: https://github.com/queelius/dfr_dist
- name: GitHub Pages
  url: https://queelius.github.io/dfr_dist/
open_issues: 0
stars: 0
tags:
- GitHub
- project
title: dfr_dist
---

Dynamic failure rate distributions (DFR)

**Stars**: 0 | **Forks**: 0 | **Open Issues**: 0

**Languages**: R

## Contributors
- queelius (13 commits)

## README

  - [R package `dfr.dist`: dynamic failure rate (DFR)
    distributions](#r-package-dfrdist-dynamic-failure-rate-dfr-distributions)
      - [Installation](#installation)
      - [Usage](#usage)

<!-- README.md is generated from README.Rmd. Please edit that file -->

## R package `dfr.dist`: dynamic failure rate (DFR) distributions

<!-- badges: start -->

<!-- badges: end -->

An R package for working with models in survival analysis in which the
distribution is parameterized by a very flexible failure rate function
(any function that satisfies properties like being non-negative,
integrating to infinity over the domain, and having a support of `(0,
Inf)`.

### Installation

You can install the development version of `dfr.dist` from GitHub repo
with:

``` r
# install.packages("devtools")
devtools::install_github("queelius/dfr_dist")
```

### Usage

The R packge `dfr_dist` provides an API for specifying and estimating
dynamic failure rate distributions. They can depend on the data in any
way, as the failure rate is any function of time and any set of
predictors, as long as the failure rate satsifies two key properties:

1.  It’s non-negative. It is not meaningful to have a negative failure
    rate; the failure rate can decrease some times, and even go to
    ![0](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;0
    "0"), though.

2.  At the limit as
    ![t](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;t
    "t") goes to infinity, the cumulative hazard
    ![H](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;H
    "H") also goes to infinity:   
    ![&#10; \\lim\_{t \\to \\infty} H(t, x\_1, \\ldots, x\_p) =
    \\infty,&#10;
    ](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%0A%20%5Clim_%7Bt%20%5Cto%20%5Cinfty%7D%20H%28t%2C%20x_1%2C%20%5Cldots%2C%20x_p%29%20%3D%20%5Cinfty%2C%0A%20%20
    "
 \\lim_{t \\to \\infty} H(t, x_1, \\ldots, x_p) = \\infty,
  ")  
        where ![H(t, x\_1, \\ldots, x\_p) = \\int\_{0}^t h(u, x\_1, \\ldots,
    x\_p)
    du](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;H%28t%2C%20x_1%2C%20%5Cldots%2C%20x_p%29%20%3D%20%5Cint_%7B0%7D%5Et%20h%28u%2C%20x_1%2C%20%5Cldots%2C%20x_p%29%20du
    "H(t, x_1, \\ldots, x_p) = \\int_{0}^t h(u, x_1, \\ldots, x_p) du").
    If this constraint isn’t satisfied, then the survival function is
    not well-defined, since it is defined as ![S(t) =
    \\exp\\bigl\\{-H(t)\\bigr\\}](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;S%28t%29%20%3D%20%5Cexp%5Cbigl%5C%7B-H%28t%29%5Cbigr%5C%7D
    "S(t) = \\exp\\bigl\\{-H(t)\\bigr\\}").

The `dfr_dist` object satisfies all of the requirements of an algebraic
distribution (see `algebraic.dist`) and a likelihoood model (see
`likelihood.model`).

The package is designed to be used with the `algebraic.mle` package,
which provides a framework for performing maximum likelihood estimation
(MLE).

A vignette showing how to use it is
[here](https://queelius.github.io/dfr_dist/articles/failure_rate.html).
