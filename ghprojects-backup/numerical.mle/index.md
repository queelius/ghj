---
author: Alex Towell
date: '2023-05-06T22:02:22Z'
description: Numerical MLE solvers
email: lex@metafunctor.com
forks: 0
languages:
- R
layout: ghproject
links:
- name: GitHub
  url: https://github.com/queelius/numerical.mle
- name: GitHub Pages
  url: https://queelius.github.io/numerical.mle/
open_issues: 0
stars: 0
tags:
- GitHub
- GitHub Project
title: numerical.mle
---

# numerical.mle
Numerical MLE solvers

[GitHub Link](https://github.com/queelius/numerical.mle)

**Stars**: 0 | **Forks**: 0 | **Open Issues**: 0

**Languages Used**: R

[GitHub Pages](https://queelius.github.io/numerical.mle/)

## README

<!-- README.md is generated from README.Rmd. Please edit that file -->

# R package: `numerical.mle`

<!-- badges: start -->

<!-- badges: end -->

A set of numeric MLE solvers.

This is very early alpha. I just started this project and it is not
ready for use yet. I just took a bunch of numerical code from
`algebraic.mle` and put it in this separate package. I will be adding
more numerical solvers and more examples in the future. Most of the code
probably does not even work yet, since I haven’t tested it.

## Installation

You can install `numerical.mle` from
[GitHub](https://github.com/queelius/numerical.mle) with:

``` r
install.packages("devtools")
devtools::install_github("queelius/numerical.mle")
```

## API

A set of methods for fitting log-likelihood functions to data. We
provide various adapters for log-likelihood functions, including penalty
adapters (for constrained MLEs) and transformation adapters (for
transformed MLEs).

The object representing a fitted model is a type of `mle` object, the
maximum likelihood estimator of the model with respect to observed data.
We use the R package for this purpose. (See
[here](https://github.com/queelius/algebraic.mle)).

The API mostly consists of generic methods with implementations for
various `mle` type objects. For a full list of functions, see the
[function
reference](https://queelius.github.io/numerical.mle/reference/index.html)
for `numerical.mle`.

## Examples

### Fitting a linear regression model

``` r
library(numerical.mle)
library(algebraic.mle)
```
