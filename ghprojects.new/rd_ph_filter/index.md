---
date: '2019-01-14T12:52:04Z'
description: null
forks: 0
languages:
- TeX
- C++
layout: project
links:
- name: GitHub
  url: https://github.com/queelius/rd_ph_filter
open_issues: 0
stars: 1
tags:
- GitHub
- project
title: rd_ph_filter
---

**Stars**: 1 | **Forks**: 0 | **Open Issues**: 0

**Languages**: TeX, C++

## Contributors
- queelius (43 commits)

## README
Rate-distorted perfect hash filter
==================================

The library `rd_ph_filter`, which standards for rate-distorted perfect hash filter,
models the concept of a bernoulli set. It is a very practical implementation of
the concept.

The rate-distortion occurs in two independent ways, yielding two different types
of rate-distortion. The first distortion is given by perfectly hashing each element
of the objective set, and then storing its hash (not the perfect hash, but a
standard hash) at the index the perfect hash function assigns to it. There is a
small chance that a random element not in the objective set will hash to the same
value. This causes a type of rate distortion denoted the false positive rate.

The second kind of rate distortion occurs as a function of the rate-distortion in the
perfect hash function. If the perfect hash function fails to perfectly hash a particular
element of the objective set, then it will collide with another element in the objective
set. When this occurs, most likely it will fail to test positive for membership.
This type of rate distortion is known as the false negative rate.

There is an opportunity to store the hashes in an arbitrary whole number of bits
with something like a *packed matrix*, but we did not consider it
worth the extra cost to implement for this particular data structure.
