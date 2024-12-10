---
date: '2024-05-15T20:40:25Z'
description: Cryptographic Hash Functions,, Random Oracles, and Lazy Computation
forks: 0
languages:
- Python
layout: project
links:
- name: GitHub
  url: https://github.com/queelius/random_oracles
open_issues: 0
stars: 0
tags:
- GitHub
- project
title: random_oracles
---

Cryptographic Hash Functions,, Random Oracles, and Lazy Computation

**Stars**: 0 | **Forks**: 0 | **Open Issues**: 0

**Languages**: Python

## Contributors
- queelius (5 commits)

## README
# Introduction to Cryptographic Hash Functions and Random Oracles

In this module, we explore the fundamental concepts of hash functions, random oracles, and lazy computation. These concepts are pivotal in the fields of cryptography and theoretical computer science, offering a robust foundation for understanding secure communications and data integrity. Through a series of Python classes, we simulate behaviors and properties that, while often theoretical, provide deep insights into the practical applications of these abstract concepts.

## Cryptographic Hash Functions

A **cryptographic hash function** is a mathematical algorithm that converts an arbitrary block of data into a fixed-size bit string, known as a *digest*. The ideal hash function has several important properties:

- **Deterministic:** The same input always produces the same output.
- **Quick computation:** The function generates the output quickly.
- **Pre-image resistance:** Given a hash output, it should be computationally infeasible to reverse it to find the original input.
- **Avalanche effect:** Small changes in the input drastically change the output.
- **Collision-resistant:** It should be difficult to find two different inputs that produce the same output.

Mathematically, a hash function can be represented as:

$$
\text{hash} : \\{0,1\\}^* \rightarrow \\{0,1\\}^n
$$

### Collision Resistance

A well-designed cryptographic hash function with an output length of \( n \) bits has a collision probability of approximately \( \frac{1}{2^n} \). For a random oracle, given its infinite output space, the probability of collision is zero. When truncated to \( n \) bits, the random oracle behaves similarly to a cryptographic hash function in terms of collision resistance.

The following Python class represents the general structure of a digest object, encapsulating these properties:

```python
class Digest:
    def __init__(self, digest):
        self._digest = bytes.fromhex(digest) if isinstance(digest, str) else digest

    def digest(self):
        return self._digest

    def hexdigest(self):
        return self.digest().hex()
```

## Random Oracles

The **random oracle model** is an abstract machine used to study the security of cryptographic protocols. It assumes the existence of a random oracle that provides truly random responses to every unique query. In practice, random oracles are simulated using hash functions, albeit imperfectly.

Mathematically, a random oracle can be represented as:

$$
\text{oracle} : \\{0,1\\}^* \rightarrow \\{0,1\\}^\infty
$$

A `RandomOracleDigest` is conceptualized in our Python framework to mimic this behavior:

```python
class OracleDigest(Digest):
    def __init__(self, input, entropy=None):
        super().__init__(input)
        if entropy is None:
            entropy = lambda : hashlib.sha256(os.urandom(32)).digest()
        self.entropy = entropy
        self.cache = {}

    def __getitem__(self, index):
        if index not in self.cache:
            self.cache[index] = self.entropy()[0]
        return self.cache[index]
```

## Lazy Computation and Infinite Digests

**Lazy computation** refers to the programming strategy of delaying the calculation of a value until it is needed. This concept is particularly useful in dealing with theoretically infinite outputs on finite machines. One can even define an algebra over the data structure, such as `truncate` and, `apply`, and so on. However, note that operations like `concat` are restricted to left-hand-side being finite and right-hand-side being potentially infinite. Essentially, any operation that does not require acccess or modification with respect to the right-hand-side is allowed.

In our framework, `LazyDigest` generates infinite outputs based on a seed value and a hash function, allowing the digest to be computed on demand:

```python
class LazyDigest(Digest):
    def __init__(self, seed, hash_fn=hashlib.sha256):
        super().__init__(seed)
        self.hash_fn = hash_fn

    def __getitem__(self, index):
        h = self.hash_fn()
        h.update(self.digest())
        h.update(str(index).encode('utf-8'))
        return h.digest()[0]
```

Through this exploration, we aim to demystify these complex ideas and illustrate their practical implications using Python, providing an interactive and engaging learning experience.

## Detailed Class Explanations

### Digest Class

The `Digest` class serves as the foundational component in our framework, abstracting the functionality of a cryptographic hash function's output. This class encapsulates the digest operations, providing a unified interface regardless of the hash function used.

```python
class Digest:
    def __init__(self, digest):
        """
        Initialize with the given digest.
        """
        self._digest = bytes.fromhex(digest) if isinstance(digest, str) else digest

    def digest(self):
        """
        Get the digest as a bytes object.
        """
        return self._digest

    def hexdigest(self):
        """
        Get the digest as a hex string.
        """
        return self.digest().hex()
```

- **Initialization:** The constructor accepts a digest, which can be either a hexadecimal string or a bytes object.
- **Digest Retrieval:** The `digest` method returns the raw bytes of the digest.
- **Hexadecimal Representation:** The `hexdigest` method provides a hexadecimal string representation of the digest.

### OracleDigest Class

The `OracleDigest` class extends `Digest` to simulate a random oracle, a theoretical construct in cryptography that provides a random response for each unique query but remains consistent for repeated queries.

```python
class OracleDigest(Digest):
    def __init__(self, input, entropy=None):
        super().__init__(input)
        if entropy is None:
            entropy = lambda: hashlib.sha256(os.urandom(32)).digest()
        self.entropy = entropy
        self.cache = {}

    def __getitem__(self, index):
        if index not in self.cache:
            self.cache[index] = self.entropy()[0]
        return self.cache[index]
```

- **Initialization:** Accepts an `input` as the seed for the random oracle. The `entropy` parameter specifies a randomness source, defaulting to a SHA-256 hash of random data from `os.urandom`.
- **Lazy Loading:** The `__getitem__` method implements lazy loading, generating random bytes when first requested and caching them for consistent future access.

### LazyDigest Class

The `LazyDigest` class embodies the principle of lazy computation to simulate an infinite digest based on a given seed and hash function.

```python
class LazyDigest(Digest):
    def __init__(self, seed, hash_fn=hashlib.sha256):
        super().__init__(seed)
        self.hash_fn = hash_fn

    def __getitem__(self, index):
        h = self.hash_fn()
        h.update(self.digest())
        h.update(str(index).encode('utf-8'))
        return h.digest()[0]
```

- **Seed and Hash Function:** Initializes with a `seed` and a `hash_fn`.
- **Lazy Byte Generation:** The `__getitem__` method generates each byte only when accessed, using the seed and index.

### LazyHexDigest Class

The `LazyHexDigest` class extends `LazyDigest` by providing hexadecimal representations of the lazily computed bytes.

```python
class LazyHexDigest(LazyDigest):
    def __getitem__(self, index):
        return super().__getitem__(index).hex()

    def hexdigest(self):
        return self
```

- **Hexadecimal Output:** Converts each byte into its hexadecimal representation for easier visualization and analysis.

### Oracle Class

The `Oracle` class simulates a random oracle by caching the outputs for given inputs, ensuring consistent results for repeated queries.

```python
class Oracle:
    def __init__(self):
        self.cache = {}

    def __call__(self, x):
        if x not in self.cache:
            self.cache[x] = OracleDigest(x)
        return self.cache[x]
```

- **Caching Mechanism:** Uses a dictionary to cache results, mimicking the random oracle's property of consistent outputs for identical inputs.
- **Integration with `OracleDigest`:** Uses the `OracleDigest` class to generate new digests.

### CryptoHash Class

The `CryptoHash` class serves as a wrapper for any cryptographic hash function, facilitating the easy generation of digests from arbitrary data inputs.

```python
class CryptoHash:
    def __init__(self, hash_fn=hashlib.sha256):
        self.hash_fn = hash_fn

    def __call__(self, x):
        return Digest(self.hash_fn(x).digest())
```

- **Flexibility in Hash Function Selection:** Allows the use of any hash function supported by Python's `hashlib`.
- **Simple Interface:** Abstracts complex cryptographic functions for easier usage.

### OracleHash Class

The `OracleHash` class approximates a random oracle by generating lazy, infinite digests using a cryptographic hash function seeded by the input.

```python
class OracleHash(CryptoHash):
    def __call__(self, x):
        return LazyDigest(self.hash_fn(x).digest(), self.hash_fn)
```

- **Extension of `CryptoHash`:** Inherits the simplicity and flexibility of `CryptoHash`.
- **Integration with `LazyDigest`:** Uses `LazyDigest` to create digests that can theoretically extend indefinitely.

## Discussion on Approximation and Finite Machines

It's important to note that while these implementations provide valuable insights, they are approximations constrained by the limitations of finite machines:

1. **Random Oracle Approximation:** The `OracleDigest` and `Oracle` classes use finite caching mechanisms, which means they cannot perfectly emulate a random oracle due to memory constraints. Additionally, each instantiation of a random oracle can diverge due to different entropy sources, illustrating the inherent randomness and

 the practical challenges of achieving idealized behavior.

2. **Lazy Computation:** The `LazyDigest` class demonstrates how infinite sequences can be generated on demand. However, it does not possess the true properties of a random oracle, as it relies on deterministic cryptographic hash functions and finite computation.

## Usage

To use these classes, you can create instances and call them with your desired inputs. Here is an example:

```python
from digest import Digest, OracleDigest, LazyDigest
from oracle import Oracle, CryptoHash, OracleHash

# Example usage of Digest
digest = Digest(hashlib.sha256(b"example input").digest())
print(digest.hexdigest())

# Example usage of OracleDigest
oracle_digest = OracleDigest(b"example input")
print(oracle_digest[0])

# Example usage of LazyDigest
lazy_digest = LazyDigest(b"example seed")
print(lazy_digest[0])

# Example usage of Oracle
oracle = Oracle()
print(oracle(b"example input")[0])

# Example usage of CryptoHash
crypto_hash = CryptoHash()
print(crypto_hash(b"example input").hexdigest())

# Example usage of OracleHash
oracle_hash = OracleHash()
print(oracle_hash(b"example input")[0])
```

## Conclusion

This project provides a clear and concise introduction to the concepts of hash functions, random oracles, and lazy computation. The provided Python classes and functions illustrate these concepts and can be used for further experimentation and learning.
