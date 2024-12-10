---
author: Alex Towell
date: '2023-06-12T19:18:49Z'
description: Likelihood model for series systems with masked component cause of failure
  and other censoring mechanisms
email: lex@metafunctor.com
forks: 0
languages:
- R
layout: ghproject
links:
- name: GitHub
  url: https://github.com/queelius/likelihood.model.series.md
open_issues: 0
stars: 1
tags:
- GitHub
- GitHub Project
title: likelihood.model.series.md
---

# likelihood.model.series.md
Likelihood model for series systems with masked component cause of failure and other censoring mechanisms

[GitHub Link](https://github.com/queelius/likelihood.model.series.md)

**Stars**: 1 | **Forks**: 0 | **Open Issues**: 0

**Languages Used**: R

## README

<!-- README.md is generated from README.Rmd. Please edit that file -->

# R Package: `likelihood.model.series.md`

This is an R package for estimating the parameters of a series system
model from masked data. It provides a flexible and intuitive interface
for specifying the model and performing maximum likelihood estimation.

This R package provides a set of functions for generating MLEs for the
lifetime parameters of the components in a series systems and other
related characteristics from data that *masks* the component cause of
failure, and also the system lifetime.

Masked data comes in a variety of forms:

1.  The system lifetime can be masked in three related ways. Right
    censoring occurs when the system under observation is only known to
    have survived for some minimum length of time. Left censoring occurs
    when the system under observation is only know to have survived for
    some maximum length of time. Finally, interval censoring occurs when
    the system under observation is only known to have survived between
    some minimum and maximum length of time.
    
    In the unmasked situation, we know precisely how long the system
    under observation survived.

2.  Regardless of how the series system lifetime is masked, the lifetime
    of the components may be masked in any of the ways described in item
    (1). There is, additionally, another kind of masking we would like
    to consider. What if we do not observe any of the component
    lifetimes, and instead are only given a (potentially masked) series
    system lifetime, and a *candidate set* of component indexes which
    plausibly contains the failed component index.
    
    For a series system of
    ![m](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;m
    "m") components, the candidate sets are subsets of
    ![\\{1,\\ldots,m\\}](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5C%7B1%2C%5Cldots%2Cm%5C%7D
    "\\{1,\\ldots,m\\}").

## Installation

You can install the development version from GitHub with:

``` r
devtools::install_github("queelius/likelihood.model.series.md")
```

## Usage

This package provides a comprehensive framework for maximum likelihood
estimation (MLE) of series system parameters from masked data.

It is based on a likelihood contribution model, where each kind of
masking of component failures in a series system of some kind and number
of components is handled by a set of likelihood contributions. The
likelihood contributions are then combined to form the likelihood model
for the kind of data and series system under consideration.

In general, masking models may characaterized by satisfy any (or none)
of the following conditions:

Condition 1: The probability that the failed component is in the
candidate set is 1.

Condition 2: Given a candidate set of potential causes of failure, when
we condition on the component cause being any one of the components in
the candidate set at the given system failure time, the probability of
the candidate set is uniform.

Condition 3: The distribution of candidate sets conditioned on a system
failure time and a component cause of failure is independent of the
system parameter vector.

We provide several kinds of masking models, including:

1.  Uninformed candidate sets that satisfy conditions 1, 2, and 3.

2.  Candidate sets with relaxed conditions, e.g., informed candidate
    sets.

Together, these masking models provide a flexible framework for handling
a wide variety of masking situations.

We also provide a method for analyzing the sensitivity of a likelihood
model to violations of the masking assumptions. This is done by
providing a set of likelihood models that are constructed by relaxing
the masking assumptions in various ways. The likelihood models are then
compared using the likelihood ratio test.

Other kinds of data and censoring are handled separately by the general
likelihood model as detailed in
[likelihood.model](https://github.com/queelius/likelihood.model). This
is the general framework for adding various kinds of contributions to
the likelihood model. This package is focused on providing contributions
for masking. The `likelihood.model` package provides a robust API to
work with likelihood models, e.g., for finding MLEs, bootstrapping
confidence intervals, and so on.

We also provide for data imputation, synthetic (implicit prior) data,
and so on. These are often based on the conditions the model assumes,
and so are provided in this package.

# API

When we construct a likelihood contribution model, we so so by
specifying the contributions of each observation type. For example, if
we have a series system with three components, and we observe the system
lifetime and the lifetimes of the first two components, we would specify
the likelihood contributions as follows:

``` r
my_model <- likelihood_contr_model$new(
  obs_type = function(df) {
    ifelse(df$right_censoring,
           "exact_fail_time_with_cand_set_c1_c2_c3",
           "right_censored")
  },

  logliks = list(
    ...
  )
)
```

Now, we may call, for instance, `fit(my_model, data)` to fit the model.
We provide a default method for `fit` based on MLE, but you can also
provide your own method, e.g., based on a customized algorithm for
efficiently finding estimates for a particular type of series system for
particular types of data.

Regardless of the outcome, ideally it will return an `mle`-like object
(from the [algebraic.mle](https://queelius.github.io/algebraic.mle)
package), in which case a host of additional methods are available to
you, such as `predict`, `confint`, `sample`, etc. This object makes it
easy to perform various analyses on your fitted model.

``` r
aic(fit)
bias(fit)
vcov(fit)
predict(fit, new_data)
confint(fit)
sample(fit, method = "asymptotic", n = 1000)
```

Note that the `likelihood.model.series.md` package provides a number of
likelihood contributions for common observation types. These are
described in the package documentation. You can also provide your own
likelihood contributions, and we provide a number of functions to make
this easier.

# Assumptions

Some of the models in this package make explicit assumptions about the
data. We provide various functions to help you check these assumptions,
to impute data that satisfies these assumptions, and to generate fake
data that satisfies these assumptions.

Sometimes, we generate fake data to create an implicit prior
distribution for the parameters.

# Model Selection

We provide some wrappers for model selection, such as AIC, BIC, and so
on. We also provide specializations and constraint functions for the
parameters.

For example, we may have a strong belief that the components are Weibull
distributed, and furthermore, that they are more or less on the same
scale with slight differences in shape. In this case, we can simplify
the model by assuming ![\\lambda\_1 = \\cdots =
\\lambda\_m](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Clambda_1%20%3D%20%5Ccdots%20%3D%20%5Clambda_m
"\\lambda_1 = \\cdots = \\lambda_m") and then only fitting
![\\hat\\lambda](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Chat%5Clambda
"\\hat\\lambda") and ![\\hat k\_1, \\ldots, \\hat
k\_m](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Chat%20k_1%2C%20%5Cldots%2C%20%5Chat%20k_m
"\\hat k_1, \\ldots, \\hat k_m"), reducing a
![2m](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;2m
"2m") parameter model to a simpler
![m+1](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;m%2B1
"m+1") parameter model. This is not an unrealistic assumption, since if
a series system is well-designed, then the components should be more or
less on the same scale (i.e., have approximately the same MTTF).

# Bootstrapping Statistics of the MLE and Likleihood Mode

To estimate various characteiristcs, such as the bias, BCa confidence
intervals, etc, then bootstraping may be used. The
`likelihood.md.series.systems` package relies upon the bootstrapping
functionality in `boot` and `likelihood.model`, but provide special
functions and methods that are particular to the masked data series
system context.

# Parametric Models

A *general series system* model, and other kinds of series systems, are
also handled by external libraries, such as the [Dynamic Failure
Rate](https://github.com/queelius/dfr_dist) library, which can be used
to construct hazard functions for components that may depend on
predictors, including time, any other covariates.

# Documentation

For more detailed information on how to use this package and what each
function does, please refer to the package documentation. The
series\_system function and its parameters are described in detail
there.

# Contributing

Contributions are welcome\! Please open an issue or submit a pull
request on GitHub if you find any bugs or if you’d like to suggest
improvements.
