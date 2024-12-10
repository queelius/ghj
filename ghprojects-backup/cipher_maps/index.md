---
author: Alex Towell
date: '2019-01-14T16:34:53Z'
description: No description available.
email: lex@metafunctor.com
forks: 0
languages:
- TeX
layout: ghproject
links:
- name: GitHub
  url: https://github.com/queelius/cipher_maps
open_issues: 0
stars: 0
tags:
- GitHub
- GitHub Project
title: cipher_maps
---

# cipher_maps
No description available.

[GitHub Link](https://github.com/queelius/cipher_maps)

**Stars**: 0 | **Forks**: 0 | **Open Issues**: 0

**Languages Used**: TeX

## README
Universal function Bernoulli approximators
================

# Oblivious maps

A set is an unordered collection of distinct elements, typically from
some implicitly understood universe. A countable set is a *finite set*
or a *countably infinite set*. A *finite set* has a finite number of
elements, such as
![\\{ 1, 3, 5 \\}](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5C%7B%201%2C%203%2C%205%20%5C%7D "\{ 1, 3, 5 \}"),
and a *countably infinite set* can be put in one-to-one correspondence
with the set of natural numbers,
![\\{1,2,3,4,5,\ldots\\}](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5C%7B1%2C2%2C3%2C4%2C5%2C%5Cldots%5C%7D "\{1,2,3,4,5,\ldots\}").
The cardinality of a set
![\mathbb{A}](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Cmathbb%7BA%7D "\mathbb{A}"),
denoted by
![\|\mathbb{A}\|](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%7C%5Cmathbb%7BA%7D%7C "|\mathbb{A}|"),
is a measure on the number of elements in the set, e.g.,
![\|\\{a,b\\}\|=2](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%7C%5C%7Ba%2Cb%5C%7D%7C%3D2 "|\{a,b\}|=2").

A map represents a *many*-to-*one* relationship. A map that associates
elements in
![\mathbb{X}](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Cmathbb%7BX%7D "\mathbb{X}")
to elements in
![\mathbb{Y}](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Cmathbb%7BY%7D "\mathbb{Y}")
has a type denoted by
![\mathbb{X}\mapsto\mathbb{Y}](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Cmathbb%7BX%7D%5Cmapsto%5Cmathbb%7BY%7D "\mathbb{X}\mapsto\mathbb{Y}").
For a map of type
![X \mapsto Y](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;X%20%5Cmapsto%20Y "X \mapsto Y"),
we denote
![X](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;X "X")
the *input* and
![Y](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;Y "Y")
the output. Typically, it is relatively easy to find which output is
associated with a given input, but the inverse operation, determining
which inputs are associated with a given output is computationally
harder. Of course, this is not necessarily the case, and mathematically
the map is just a one-to-many relation over
![X \times Y](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;X%20%5Ctimes%20Y "X \times Y").

For instance, Table depicts a function over a finite domain of
![n](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;n "n")
elements, where each input
![x \in X](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;x%20%5Cin%20X "x \in X")
is associated with a single output
![y \in Y](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;y%20%5Cin%20Y "y \in Y"),
i.e.,
![y = f(x)](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;y%20%3D%20f%28x%29 "y = f(x)").

The input does not need to be a simple set like natural numbers, but
rather can be any type of set, such as a set of pairs as given in .

Since we are interested in constructing maps in computer memory, we must
have some way to represent them. One technique may be given by the
following table.

The oblivious map is given by the following definition.
\begin{definition} The *oblivious Bernoulli map* is a specialization of
the Bernoulli map. We denote an oblivious map of
![f](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;f "f")
by
![f^\* = (f,\mathcal{C})](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;f%5E%2A%20%3D%20%28f%2C%5Cmathcal%7BC%7D%29 "f^* = (f,\mathcal{C})")
where
![\mathcal{C}](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Cmathcal%7BC%7D "\mathcal{C}")
is the subset of the computational basis of
![f](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;f "f")
which
![f^\*](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;f%5E%2A "f^*")
provides. An oblivious Bernoulli map satisifes the following conditions:

-   The function
    ![f^\* : X \mapsto Y](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;f%5E%2A%20%3A%20X%20%5Cmapsto%20Y "f^* : X \mapsto Y")
    is a Bernoulli map of
    ![f](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;f "f").

-   If an element of
    ![x \in X](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;x%20%5Cin%20X "x \in X")
    is not in the domain of definition,
    ![f(x)](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;f%28x%29 "f(x)")
    is a random oracle over
    ![Y](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;Y "Y")

-   A particular mapping
    ![y = f^\*(x)](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;y%20%3D%20f%5E%2A%28x%29 "y = f^*(x)")
    may only be learned by applying
    ![f^\*](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;f%5E%2A "f^*")
    to
    ![x](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;x "x").

In an *oblivious map*, a mapping (row in the table) is only learned upon
request.

Observe that
![f^\*](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;f%5E%2A "f^*")
is an oblivious value. Typically, we are also interested in functions in
which the domain and codomain also represent oblivious values, i.e.,

![f^\* : X^\* \mapsto Y^\*](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;f%5E%2A%20%3A%20X%5E%2A%20%5Cmapsto%20Y%5E%2A "f^* : X^* \mapsto Y^*")

where
![X^\* = (X,\mathcal{C}\_1)](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;X%5E%2A%20%3D%20%28X%2C%5Cmathcal%7BC%7D_1%29 "X^* = (X,\mathcal{C}_1)"),
![Y^\* = (Y,\mathcal{C}\_2)](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;Y%5E%2A%20%3D%20%28Y%2C%5Cmathcal%7BC%7D_2%29 "Y^* = (Y,\mathcal{C}_2)"),
and
![f^\* = (f,\mathcal{C}\_3)](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;f%5E%2A%20%3D%20%28f%2C%5Cmathcal%7BC%7D_3%29 "f^* = (f,\mathcal{C}_3)").

It may be the case that
![X^\*](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;X%5E%2A "X^*")
is a set of oblivious integers that, say, only supports testing equality
and addition. Of course, once we have addition, we may also implement
multiplication, powers, and many other operations.

By , the space complexity of the Bernoulli map with an error rate
![\operatorname{error\\\_rate}(\hat{f}, x)](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Coperatorname%7Berror%5C_rate%7D%28%5Chat%7Bf%7D%2C%20x%29 "\operatorname{error\_rate}(\hat{f}, x)")
is given by the following theorem.
## Abstract data type

A *type* is a set and the elements of the set are called the *values* of
the type. An *abstract data type* is a type and a set of operations on
values of the type. For example, the *integer* abstract data type is the
set of all integers and a set of standard operations (computational
basis) such as addition, subtraction, and multiplication.

A *data structure* is a particular way of organizing data and may
implement one or more abstract data types. An *immutable* data structure
has static state; once constructed, its state does not change until it
is destroyed. Let
![\hat{f} : X \mapsto Y](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Chat%7Bf%7D%20%3A%20X%20%5Cmapsto%20Y "\hat{f} : X \mapsto Y")
model the concept of a Bernoulli approximation of
![f : X \mapsto Y](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;f%20%3A%20X%20%5Cmapsto%20Y "f : X \mapsto Y").
Then,

-   ![\hat{f}(x)](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Chat%7Bf%7D%28x%29 "\hat{f}(x)")

    Returns a value in
    ![Y](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;Y "Y").

-   ![\operatorname{error\\\_rate(\hat{f},x)](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Coperatorname%7Berror%5C_rate%28%5Chat%7Bf%7D%2Cx%29 "\operatorname{error\_rate(\hat{f},x)").

    Returns the *error rate* of
    ![\hat{f}](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5Chat%7Bf%7D "\hat{f}")
    applied to
    ![x](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;x "x"),
    i.e.,

    ![\Pr\\{\hat{f}(x) = f(x)} = \operatorname{error\\\_rate(\hat{f},x)](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;%5CPr%5C%7B%5Chat%7Bf%7D%28x%29%20%3D%20f%28x%29%7D%20%3D%20%5Coperatorname%7Berror%5C_rate%28%5Chat%7Bf%7D%2Cx%29 "\Pr\{\hat{f}(x) = f(x)} = \operatorname{error\_rate(\hat{f},x)")

    for every
    ![x \in \operatorname{dom}(f)](https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D&space;%5Cbg_white&space;x%20%5Cin%20%5Coperatorname%7Bdom%7D%28f%29 "x \in \operatorname{dom}(f)").
