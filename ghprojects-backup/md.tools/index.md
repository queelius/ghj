---
author: Alex Towell
date: '2022-01-29T20:41:28Z'
description: Masked data tools
email: lex@metafunctor.com
forks: 0
languages:
- R
layout: ghproject
links:
- name: GitHub
  url: https://github.com/queelius/md.tools
- name: GitHub Pages
  url: https://queelius.github.io/md.tools/
open_issues: 0
stars: 0
tags:
- GitHub
- GitHub Project
title: md.tools
---

# md.tools
Masked data tools

[GitHub Link](https://github.com/queelius/md.tools)

**Stars**: 0 | **Forks**: 0 | **Open Issues**: 0

**Languages Used**: R

[GitHub Pages](https://queelius.github.io/md.tools/)

## README

<!-- README.md is generated from README.Rmd. Please edit that file -->

# R package: `md.tools`

<!-- badges: start -->
<!-- badges: end -->

A miscellaneous set of tools for working with *masked data* and common
features of masked data. The tool set takes inspiration from functional
programming, with inputs and outputs defined over masked data frames of
type `tbl_md` (or just data frames), making it consistent with the
*tidyverse* way of doing things.

We provide a set of simple functions on masked data frames, which may be
used to compose more complicated functions, particularly when using the
pipe operator `%>%`.

#### Installation

You can install the development version of `md.tools` from
[GitHub](https://github.com/queelius/md.tools) with:

``` r
# install.packages("devtools")
#devtools::install_github("queelius/md.tools")
```

We load the libraries `md.tools` and `tidyverse` with:

``` r
library(tidyverse)
library(md.tools)
```

## Matrices

A lot of space in `md.tools` is devoted to working with matrices encoded
in the columns of data frames. We could directly store matrices in a
column, but we prefer to work with columns defined over primitive types
like `boolean`.

Consider the `boolean` matrix `C` of size `10`-by-`3`:

``` r
n <- 5
m <- 3
C <- matrix(sample(c(T,F), size=m*n, replace=TRUE), nrow=n)
```

We may represent this in a data frame of 5 rows with the columns `c1`,
`c2`, and `c3` with:

``` r
md <- md_encode_matrix(C,"c")
print(md)
#> # A tibble: 5 × 3
#>   c1    c2    c3   
#>   <lgl> <lgl> <lgl>
#> 1 FALSE TRUE  TRUE 
#> 2 TRUE  TRUE  TRUE 
#> 3 TRUE  TRUE  TRUE 
#> 4 FALSE FALSE FALSE
#> 5 FALSE FALSE FALSE
```

We may also decode a matrix stored in a data frame with:

``` r
print(all(C == md_decode_matrix(md,"c")))
#> [1] TRUE
```

We may want to work with a Boolean matrix as a list. The function
`md_boolean_matrix_to_list` uses the following transformation:

If we have a $n$-by-$m$ Boolean matrix, then if the $(j,k)$-element is
`TRUE`, the $j$-th vector in the list contains the integer $k$.

We can show the `md` with the candidate set as a set of integers with:

``` r
md %>% md_boolean_matrix_to_charsets("c", "candidate set")
#> # A tibble: 5 × 4
#>   c1    c2    c3    `candidate set`
#>   <lgl> <lgl> <lgl> <chr>          
#> 1 FALSE TRUE  TRUE  {2, 3}         
#> 2 TRUE  TRUE  TRUE  {1, 2, 3}      
#> 3 TRUE  TRUE  TRUE  {1, 2, 3}      
#> 4 FALSE FALSE FALSE {}             
#> 5 FALSE FALSE FALSE {}
```

We allow converting between three representations: lists of integer
vectors, Boolean vectors, and lists of charsets (sets represented with
strings, e.g., “{ 1, 2 }”. Thus, the inverse of
`md_boolean_matrix_to_list` is just `md_list_to_boolean_matrix` and so
on.

## Decorators

We now consider some data frame transformations that adds additional
columns with information that may be inferred from what is already in
the data frame. For this reason, we have chosen to call them
*decorators*.

In a masked data frame, we may have a column `k` that stores the failed
component. We simulate failed components and mark them as *latent* with:

``` r
md <- md %>%
  mutate(k=sample(1:m,n,replace=TRUE)) %>%
  md_mark_latent("k")
print(md)
#> Latent variables:  k 
#> # A tibble: 5 × 4
#>   c1    c2    c3        k
#>   <lgl> <lgl> <lgl> <int>
#> 1 FALSE TRUE  TRUE      1
#> 2 TRUE  TRUE  TRUE      1
#> 3 TRUE  TRUE  TRUE      2
#> 4 FALSE FALSE FALSE     3
#> 5 FALSE FALSE FALSE     3
```

We may additionally have a candidate set encoded by the Boolean columns
`c1`,…,`cm`, in which case we may infer whether the candidate set
*contains* the failed component `k` with:

``` r
md <- md %>% md_set_contains("c", "k", "contains")
print(md)
#> Latent variables:  k 
#> # A tibble: 5 × 5
#>   c1    c2    c3        k contains
#>   <lgl> <lgl> <lgl> <int> <lgl>   
#> 1 FALSE TRUE  TRUE      1 FALSE   
#> 2 TRUE  TRUE  TRUE      1 TRUE    
#> 3 TRUE  TRUE  TRUE      2 TRUE    
#> 4 FALSE FALSE FALSE     3 FALSE   
#> 5 FALSE FALSE FALSE     3 FALSE
```

We see that there is a new column, `contains`, that tells us whether the
candidate set actually contains the failed component. No new information
is given by this column, it only presents what information that is
already there in a potentially more conventient format.

Given the same data frame and candidate set, we may determine the
*cardinality* of the candidate sets with:

``` r
md <- md %>% md_set_size("c")
print(md)
#> Latent variables:  k 
#> # A tibble: 5 × 6
#>   c1    c2    c3        k contains size_c
#>   <lgl> <lgl> <lgl> <int> <lgl>     <int>
#> 1 FALSE TRUE  TRUE      1 FALSE         2
#> 2 TRUE  TRUE  TRUE      1 TRUE          3
#> 3 TRUE  TRUE  TRUE      2 TRUE          3
#> 4 FALSE FALSE FALSE     3 FALSE         0
#> 5 FALSE FALSE FALSE     3 FALSE         0
```

We may *unmark* a column variable as latent with:

``` r
md <- md %>% md_unmark_latent("k")
print(md)
#> # A tibble: 5 × 6
#>   c1    c2    c3        k contains size_c
#>   <lgl> <lgl> <lgl> <int> <lgl>     <int>
#> 1 FALSE TRUE  TRUE      1 FALSE         2
#> 2 TRUE  TRUE  TRUE      1 TRUE          3
#> 3 TRUE  TRUE  TRUE      2 TRUE          3
#> 4 FALSE FALSE FALSE     3 FALSE         0
#> 5 FALSE FALSE FALSE     3 FALSE         0
```

The latent variable specification is metadata about the masked data
frame, but it does not necessarily impose any requirements on algorithms
applied to it.

More generally, a masked data frame may have a lot more metadata about
it, and we provide some tools for working with them. However, for the
most part, you are expected to handle the metadata yourself. The
metadata is stored in the *attributes*, and so underneath the hood, a
masked data frame is just a data frame and may be treated as one.

## Metadata

To read and write data frames for sharing with others, including
yourself, we prefer to work with plaintext files like CSV files, where
each row corresponds to some set of measurements of some experimental
unit.

However, we may also want to store *metadata* about the experiment that
generated the data, or we may wish to store more information about the
experimental units that does not naturally fit into the data frame
model.

To store metadata, we take the general approach of storing JSON
(Javscript Object Notation) in the *comments* of the tabular data file
(like CSV), where a comment by default is anything after the `#`
character on a line.

``` r
data <- md_read_csv_with_meta("./data-raw/exp_series_md_1.csv")
#> Rows: 1000 Columns: 8
#> ── Column specification ────────────────────────────────────────────────────────
#> Delimiter: ","
#> dbl (5): t, k, t1, t2, t3
#> lgl (3): x1, x2, x3
#> 
#> ℹ Use `spec()` to retrieve the full column specification for this data.
#> ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.
print(data)
#> Latent variables:  k t1 t2 t3 
#> # A tibble: 1,000 × 8
#>          t     k      t1      t2     t3 x1    x2    x3   
#>      <dbl> <dbl>   <dbl>   <dbl>  <dbl> <lgl> <lgl> <lgl>
#>  1 0.144       2 0.281   0.144   0.266  TRUE  TRUE  FALSE
#>  2 0.0105      1 0.0105  0.0141  0.0633 TRUE  FALSE TRUE 
#>  3 0.0363      2 0.105   0.0363  0.545  TRUE  TRUE  FALSE
#>  4 0.00972     1 0.00972 0.251   0.0960 TRUE  FALSE TRUE 
#>  5 0.0377      3 0.0937  0.0943  0.0377 TRUE  FALSE TRUE 
#>  6 0.0958      3 0.283   0.391   0.0958 FALSE TRUE  TRUE 
#>  7 0.169       3 0.197   1.01    0.169  FALSE TRUE  TRUE 
#>  8 0.270       3 0.322   0.371   0.270  FALSE TRUE  TRUE 
#>  9 0.299       3 0.390   0.401   0.299  TRUE  FALSE TRUE 
#> 10 0.00794     2 0.524   0.00794 0.120  FALSE TRUE  TRUE 
#> # ℹ 990 more rows
```

We may view all of the metadata stored in `data` with:

``` r
meta <- attributes(data)
meta["row.names"] <- NULL
print(meta)
#> $class
#> [1] "tbl_md"     "tbl_df"     "tbl"        "data.frame"
#> 
#> $names
#> [1] "t"  "k"  "t1" "t2" "t3" "x1" "x2" "x3"
#> 
#> $comment
#> [1] "this is a simulation test."
#> 
#> $param
#> [1] 3 4 5
#> 
#> $components
#>        family param
#> 1 exponential     3
#> 2 exponential     4
#> 3 exponential     5
#> 
#> $candidate_conditions
#> [1] "C1" "C2" "C3"
#> 
#> $latent
#> [1] "k"  "t1" "t2" "t3"
#> 
#> $observable
#> [1] "t"  "x1" "x2" "x3"
#> 
#> $num_comp
#> [1] 3
#> 
#> $sample_size
#> [1] 1000
```

Note that we removed the `row.names` attribute, since it’s quite long
and uninformative.

A lot of the metadata for `data` has to do with how the data was
generated. In particular, we see this data is the result of a simulation
for a series system with $3$ exponentially distributed component
lifetimes parameterized by $\lambda = (3,4,5)'$ and a candidate model
consistent with conditions $C_1$, $C_2$, and $C_3$ for series systems
with a masked component cause of failure in the form of candidate sets.
