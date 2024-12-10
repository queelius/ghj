---
date: '2023-06-03T05:48:59Z'
description: Likelihood model framework
forks: 0
languages:
- R
- HTML
layout: project
links:
- name: GitHub
  url: https://github.com/queelius/likelihood.model
- name: GitHub Pages
  url: https://queelius.github.io/likelihood.model/
open_issues: 0
stars: 1
tags:
- GitHub
- project
title: likelihood.model
---

Likelihood model framework

**Stars**: 1 | **Forks**: 0 | **Open Issues**: 0

**Languages**: R, HTML

## Contributors
- queelius (20 commits)

## README
Likelihood model
================

# R package: `likelihood.model`

The R package `likelihood.model` is designed for specifying and using
likelihood models for statistical inference.

The basic likelihood model is a concept that, in order for your object
to satisfy, must implement a number of generic functions/methods. The
package provides a class, `likelihood_contr_model`, which implements
these functions and serves as a flexible framework for specifying
likelihood models based on the idea of independent likelihood
contributions for different types of observations, e.g., right-censored
versus exact observations.

The package is designed to be used with the
[`algebraic.mle`](https://github.com/queelius/algebraic.mle) package,
which provides a framework for performing maximum likelihood estimation
(MLE).

## Installation

You can install the development version of `likelihood.model` from
[GitHub](https://github.com/queelius/likelihood.model) with:

``` r
if (!require(devtools)) {
    install.packages("devtools")
}
devtools::install_github("queelius/likelihood.model")
```

See the [package website](https://queelius.github.io/likelihood.model/)
for more information.
