---
date: '2020-12-18T00:13:12Z'
description: Homomorphic computational extensions
forks: 0
languages:
- C++
layout: project
links:
- name: GitHub
  url: https://github.com/queelius/homomorphic_computational_extensions
- name: GitHub Pages
  url: https://queelius.github.io/homomorphic_computational_extensions/
open_issues: 0
stars: 0
tags:
- GitHub
- project
title: homomorphic_computational_extensions
---

Homomorphic computational extensions

**Stars**: 0 | **Forks**: 0 | **Open Issues**: 0

**Languages**: C++

## Contributors
- queelius (27 commits)

## README
Homomorphic computational extensions
================
Alex Towell
3/5/2022

We consider homomorphisms which are based on computational concerns which are used to
transform inefficient or lossy computations over some original domain `T` into a
conceptually equivalent group `T*` over a restricted set of operations.

If the original problem can be solved using these restricted operations, then we may
transform `T` into `T*` and efficiently perform the computations.
Sometimes, the entire solution cannot be transformed back to `T`, but the restricted
set of functions or operations may still be sufficient, e.g., evaluating
`a + c < b + c` even though `a+c` or `b+c` may not be in the domain of `T`.

See the [documentation](http://queelius.github.io/homomorphic_computational_extensions/)
for more.

Given the depth and specificity of your project, the README.md for your GitHub repository should reflect the theoretical underpinnings and overarching conceptual framework guiding the development of mathematical objects like `lg<T>`. Here's a draft that captures the essence of your work, using appropriate mathematical notation and terminology to cater to an informed audience.

---

# Conceptual Framework for Computational Homomorphisms

## Overview

This repository explores the development and implementation of mathematical objects designed to address computational inefficiencies, precision loss, and the potential for overflow and underflow in numerical computations. Central to our approach is the application of homomorphisms from algebraic structures like rings and groups into computationally efficient domains, facilitating operations that are inherently problematic in the original computational basis.

## Theoretical Foundation

Our work is rooted in the mathematical concepts of **rings**, **groups**, **homomorphisms**, and **approximate algorithms**. By leveraging these foundational principles, we aim to transform operations over some domain \(D\) into a conceptually equivalent group \(G\) over a restricted set of operations. This transformation, guided by computational homomorphisms, allows for the efficient execution of operations that are either inefficient or prone to loss in the original domain.

### Computational Homomorphisms

Given a type \(T\) that models a ring or group with operations \(\oplus\) and \(\otimes\), we define a transformation into a domain \(D'\) where these operations can be efficiently computed through a restricted computational basis \(B\). This transformation not only aims to preserve the algebraic structure but also to mitigate computational issues such as overflow, underflow, and significant precision loss.

## Implementation of Homomorphic Objects

Having laid the theoretical foundation, here we proceed to briefly cover a few
choice imlementations of the concept. These impleentations are not exhaustive, but
work well together to demonstrate the concept and its potential.

### Log Domain Implementation: `lg<T>`

The `lg<T>` class maps multiplication operations into addition within the logarithmic domain, effectively addressing computational limitations in the original domain. We simply map a value to its logarithm, and then define
a restricted computational basis for this value type. In particular, we allow for
comparison predicates, multiplication (which is addition under the hood), division
(which is subtraction under the hood), and exponentiation (which is multiplication
under the hood).

The `lg<T>` class is designed to facilitate efficient computations by leveraging the properties of logarithms to transform multiplication operations into addition. This transformation not only mitigates the risk of overflow and underflow but also enables the use of efficient addition-based operations within the log domain.

```cpp
auto a = lg<double>(3); // store: log(3)
auto b = lg<double>(4); // store: log(4)
auto c = a * b // c = lg<double>{12} // store: log(3) + log(4) = log(12)
auto d = lg<double>(100) // store: log(100)
auto e = d / c // store: log(100) - log(12) = log(100/12) = log(8.33)
assert(a < b)
assert(e < d)
```

If we have a lot of values to multiply, we can map them all to their logarithms
and then efficiently do the equivalent computation in the log-domain. This also
avoids underflows or overflows that may occur in the original domain.

To get at the stored logarthm, we provide a method `value()`:

```cpp
auto x = a.value() // returns log(3)
```
This is not normally what you want, and it may even leak the abstraction, but
we provide it anyway.

```cpp
std::cout << a.value(); // outputs "exp(" << a.value() << ")\n";
```

So, `lg<T>(x)` maps `x` to the log-domain. We can then map the result back to the
original domain `T` by simply exponentiating the stored value. We provide
a conversion operator to do this: `operator T()`.

```cpp
std::cout << a; // outputs "exp(" << a.value() << ")";
std::cout << (double)a; // outputs 3.0
```

We may not be able to map the value back to the original domain, although
often we can because only the intermedate results of the computation may have
caused an overflow or underflow in the origional domain, but the final result
may not. In this case, we can simply map the final result in `lg<T>` back to
the original domain `T` to retrieve the exact result.

We also efficiently support exponentiation and a few other operations:

```cpp
auto f = exp(a) // f = e^a, in `a` we stored log(3), in `f` we store: exp(log(3)) = 3
```

Notice that exponentiation may result in an overflow or underflow in the
transformed log-domain. For instance, if we have stored the result of a very
large number that doesn't fit into the origional domain but it does fit in
the log domain, then exponentiating it may result undoes the transformation,
resulting in an overflow or underflow again. This is fine -- `lg<T>` is
designed to make multiplication and division efficient, and it does so
without causing overflows or underflows, but it does not guarantee that
exponentiation will not cause overflows or underflows.

We can also not efficiently support addition or subtraction in the log-domain:

```cpp
auto g = a + b
```

Howe do we implement this? Conceptually, we can do the following:

1. Take the exponetial of the values stored in `a` andn `b`:

    `exp(log(3)) * exp(log(4)) = 3 * 4 = 12`

2. Store the result: `lg<double>(12)`

However, both step 1 and step 2 can result in overflows or underflows. We can
detect whether it will result in an overflow or underflow prior to
doing the operation, so we see that addition and subtraction are partial functions
in the log-domain. We can still define them, but they may not be defined for
all inputs. More importantly, even if we can do the operation without an overflow
or underflow, it is not a very efficient operation. Thus, we have chosen to
restrict the computational basis of `lg<T>` to only support multiplication,
division, predicates, 


We also support logarithms and exponentiation:

```cpp
auto h = log(a) // we already store log(3) in `a`, so we store:
                // log(log(3)) or log((double)a)

auto i = exp(a) // we already store log(3) in `a`, so we store:
                  // exp(log(3)) = (double)a.
```

### Exponential Domain Implementation: `exp<T>`


Previously, in `lg<T>`, we mapped `x` to `log(x)` and then defined multiplication
in terms of `lg<T>` as addition in the log-domain. We can also map `x` to `exp(x)`
and then define addition in terms of `expo<T>` as multiplication in the exp-domain:

```cpp
auto a = expo<double>(3); // store: exp(3)
auto b = expo<double>(4); // store: exp(4)
auto c = a + b // c = expo<double>{12} // store: exp(3) * exp(4)
```

### Log-Exp-Sum

If we have `lg<T>` and `exp<T>`, then we can define `log_exp_sum<T>` which is a type that


#### Approximate Algorithms

Here, we also see an opportunity to explore the development of approximate algorithms
that can model computations outside of its restricted computational basis \(B\).
It can do so without converting back to the original domain \(D\), but often with
some loss of precision or efficiency.

In the log-exp-sum basis, we can do so-called softmax or softmin operations, which
approximate the maximum or minimum of a set of numbers, respectively. These operations
are useful in machine learning and optimization algorithms, and can be computed
efficiently in the log-exp-sum basis.

We can wrap the output of such an approximate algorithm in a type that can support estimating
the error of the approximation, and can be converted back to the original domain \(D\).
Different kinds of opoerations may thus be performed on the result of this approximate
algorithm, such as comparing it to another value, or adding it to another value,
while propagating and updating the error estimates, e.g.,
`a < b` where either `a` or `b` is the result of the softmax operation. In this case,
since softmax result provides an upper bound on the maximum of the set of numbers, we
know that if `a` is a softmax result (and the true value of the operation is latent)
and `b` is exact, then if `a < b` is true, then we know that the latent value of the
softmax result is less than `b`, and so it should return `true` with probability of
being incorrect `0` and `false` with probability of being incorrect that is a
funtion of the error estimate of `a`. If both `a` and `b` are softmax results, then
both softmax values represent latent values and the error estimate becomes more
complicated, but can still be estimated.

We formalize the value of the operation `a < b` with the error estimate as a type
`bernoulli<bool>` which we formalize elsewhere in anohher C++ library,
`bernoulli_data_types`. See the [documentation](http://queelius.github.io/bernoulli_data_types/)
for more.   

## Future Directions

Our ongoing work will focus on expanding the library of mathematical objects and exploring their applications across various computational domains. We are particularly interested in the potential for these objects to enhance computational efficiency, precision, and robustness in fields ranging from numerical analysis to artificial intelligence.

### Contributions

We welcome contributions from researchers and practitioners interested in advancing the state of computational mathematics through the exploration of homomorphic transformations and their applications. Whether through theoretical insights, new mathematical objects, or practical implementations, your contributions can help shape the future of computational efficiency and precision.
