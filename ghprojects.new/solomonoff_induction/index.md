---
date: '2024-02-15T19:28:46Z'
description: null
forks: 0
languages:
- Python
- Jupyter Notebook
layout: project
links:
- name: GitHub
  url: https://github.com/queelius/solomonoff_induction
open_issues: 0
stars: 0
tags:
- GitHub
- project
title: solomonoff_induction
---

**Stars**: 0 | **Forks**: 0 | **Open Issues**: 0

**Languages**: Python, Jupyter Notebook

## Contributors
- queelius (10 commits)

## README
# Markov chains

A first-order Markov chain is a conditional probability distribution of the form
$$
    P(X_k = x_k | X_{k-1} = x_{k-1}),
$$
where $x_j \in X$, $X$ is the support of $X_1,X_2,\ldots$.
In this context, we refer to $X$ as the set of *tokens* that may be observed.

An $n$-th order Markov chain models
$$
    P(X_k = x_k | x_{k-1}, x_{k-2}, \ldots, x_{k-n + 1}).
$$

We can model this with a first-order Markov chain with $|X|^n$ states, where
each state has up to $|X|$ non-zero transition probabilities,
$$
    P(S_k = s_k | S_{k-1} = s_{k-1})
$$
where $s_1,s_2,\ldots \in X^n$ but we still do state transitions on $x_1,x_2,\ldots$.
Some observations:

1. As the token set $X$ increases in size (cardinality), the number of states grows
   by $|X|^n$, e.g., if $n=2$ then it grows quadradically.
2. As the order $n$ increases, the number of states grows exponentially.
3. As the order $n$ increases, the number of state transitions stays *constant*, $O(|X|)$.
4. As the order $n$ increases, the Markov chain's transition matrix becomes increasingly sparse,
   with a maximum density of $|X|^{1-n}$ non-zero entries (as $n \to \infty$, the density
   goes to $0$).
