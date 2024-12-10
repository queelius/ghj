---
date: '2019-01-15T18:39:47Z'
description: 'Encrypted Search: A Probabilistic Estimator of Confiidentiality'
forks: 0
languages:
- HTML
- TeX
- C++
- CSS
- JavaScript
- Roff
layout: project
links:
- name: GitHub
  url: https://github.com/queelius/encrypted_search_probabilistic_estimator_conf
- name: GitHub Pages
  url: https://queelius.github.io/encrypted_search_probabilistic_estimator_conf/
open_issues: 0
stars: 0
tags:
- GitHub
- project
title: encrypted_search_probabilistic_estimator_conf
---

Encrypted Search: A Probabilistic Estimator of Confiidentiality

**Stars**: 0 | **Forks**: 0 | **Open Issues**: 0

**Languages**: HTML, TeX, C++, CSS, JavaScript, Roff

## Contributors
- queelius (7 commits)

## README
## Encrypted Search: A Probabilistic Estimator of Confidentiality

This repository contains research on measuring the confidentiality of encrypted
search systems against an adversary that observes hidden queries to infer plaintext queries.

This paper is written in Bookdown and provides output options for PDF (pdfbook)
and HTML (gitbook).

### Abstract
We propose a confidentiality measure for plaintext queries against an adversary that observes corresponding hidden queries. An adversary employs a plaintext attack to infer a mapping from hidden to plaintext queries. We apply the estimator to an encrypted search system that maintains a minimum confidentiality level. A bootstrap method estimates the sampling distribution of confidentiality over query histories. This provides a probabilistic assessment of confidentiality, like the chance that an adversary infers over 70% of queries. We also propose mapping entropy to a lower bound on confidentiality.

### Contents

- `pdfbook/paper.pdf`: PDF version of the full paper
- `gitbook/index.html`: HTML version of the full paper
- `docs/`: Copy of `gitbook` directory, for GitHub Page hosting at: ...
- `src/`: C++ simulation of Zipf study.
- `data/`: Experimental results on confidentiality (Zipf simulation)

