---
date: '2024-06-16T03:18:26Z'
description: null
forks: 0
languages:
- Python
layout: project
links:
- name: GitHub
  url: https://github.com/queelius/treeprog
open_issues: 0
stars: 0
tags:
- GitHub
- project
title: treeprog
---

**Stars**: 0 | **Forks**: 0 | **Open Issues**: 0

**Languages**: Python

## Contributors
- queelius (1 commits)

## README
# `Universal Tree Traversal`

## Introduction

There are many ways to traverse a tree. The most common ways are:

- Pre-order traversal
- Post-order traversal
- In-order traversal
- Level-order traversal

These are the most common ways to traverse a tree, but there are many other
ways to traverse a tree. For example, you can traverse a tree in a spiral
pattern, or you can traverse a tree in a zig-zag pattern. You can also
traverse a tree in a random order. There are many ways to traverse a tree,
and each way has its own advantages and disadvantages. Sometimes, you only
want to traverse a subset of the tree, or you may want to traverse the tree
upwards (parent relationships) instead of downwards (child relationships),
or even sideways (level order via sibling relationships).

## Universal Tree Traversal

Universal tree traversal is a domain-specific language (DSL) that
allows some order of traversal to be described and executed in the context of 
its tree context. The DSL is intentionally limited in scope to tree traversal
orders, but it is flexible enough to describe most meaningful tree traversals.

### Computational Model

The computational model which evaluates the DSL is not Turing complete. It is
not a general-purpose programming language, but rather a DSL for describing tree
traversal orders. We say that it is a Universal Tree Traversal (UTT) because it
can describe most meaningful tree traversal orders with a facility for
conditional traversal, payload transformation, and result collection and
aggregation.

The DSL is a declarative langauge that takes care of the details of
tree traversal for you. Because of this, a general stack-based model is
not necessary. Instead, the DSL is a list of actions applied to tree nodes
in some order as described by the actions. There is state that is maintained
in the form of a local environment for each node that situates it in the
context of the tree, but this state is not a general-purpose stack-based
model.

#### Environment Model

The environment model represents the context of a node in its tree. We populate
the node's local environment with some special values that represent the node
other relationships it has to other nodes in the tree.

To reference an environment variable, we use the `$` symbol followed by the
name of the variable. For example, `$node` is the node that the traversal
order is currently being applied to. You can store values in the environment
with the `set!` action:

```json
{
    "set!": {
        "key": "value"
    }
}
```

When you set a value in the environment, you can reference it later in the  
traversal order. Any nodes that follow this node (see `follow` action) will
be able to access these environment variables, which allows you to pass values
from one node to another in the traversal order.

These enviroment variables may be used as arguments to predicates that describe
the traversal order. When we arrive at a node, we also populate the environment
with some special values that represent the node and its relationships to other
nodes in the tree. These values are:

- `$node` is the node that the traversal order is being applied to.
- `$depth` is the depth of the node in the tree.
- `$num_children` is the number of children of the node.
- `$parent` is the parent of the node.
- `$sibling` is the sibling of the node.
- `$root` is the root of the tree.
- `$tree` is the tree that the node is in.
- `$results` is a global dictionary of results that the nodes are added to. The
  results are keyed by the value of the `result-name` argument in the `visit`
  action.

### Traversal Order Grammar

The traversal order grammar defines a JSON array of dictionaries that describe
a conditional seuence of actions that are applied to a node in the tree. The
actions are applied in order, which defines the traversal order of the tree.

The traversal order description is given by the following BNF:

```bnf
<order>         ::= "[" "]" | "[" <action> ("," <action>)* "]"
<action>        ::= <visit> | <payload> | <cond> | <follow> | <set>
<set>           ::= "{"
                        "\"set!\"" ":" <kwargs>
                    "}"
<follow>        ::= "{"
                        "\"follow\"" ":" <dir> 
                        ("," "\"select\"" ":" <select>)? 
                        ("," "\"select-order\"" ":" <select_order>)?
                    "}"
<visit>         ::= "{"
                        "\"visit\"" ":" <pred_fn> 
                        ("," "\"result-name\"" ":" <key>)? 
                        (<args>)? 
                    "}"
<cond>          ::= "{"
                        "\"cond\"" ":" "["
                            <cond_case>
                            ("," <cond_case>)*
                        "]"
                    "}"
<cond_case>     ::= "{"
                        "\"pred\"" ":" <pred_fn>
                        ("," <args>)? ","
                        "\"order\"" ":" <order>
                    "}"
<payload>       ::= "{"
                        "\"payload-map\"" ":" <payload_fn>
                        ("," <args>)?
                    "}"
<args>          ::= "\"args\"" ":" <posargs> | "\"kwargs\"" ":" <kwargs>
<posargs>       ::= "[" "]" | "[" <arg> ("," <arg>)* "]"
<arg>           ::= <value> | <env_var>
<kwargs>        ::= "{" "}" | "{" <kwarg> ("," <kwarg>)* "}"
<kwarg>         ::= <key> ":" <arg>
<env_var>       ::= "$" <key>
<pred_fn>       ::= <boolean> | "\"less?\"" | "\"eq?\"" | <key>
<selector>      ::= "\"all\"" | "\"none\"" | "\"rest\"" | "\"rand\"" | <key>
<select_order>  ::= "\"id\"" | "\"reverse\"" | "\"shuffle\"" | <key>
<dir>           ::= "\"up\"" | "\"down\""  | "\"sideways\"" | <key>
<payload_fn>    ::= "\"id\"" | "\"proj\"" | "\"rename\"" | <key>
<key>           ::= <str>
<value>         ::= "{}" | <str> | <int> | <float> | <boolean>
                | "[" <value> ("," <value>)* "]" 
                | "{" <key> ":" <value> ("," <key> ":" <value>)* "}"
<str>           ::= "\"" <char>+ "\""
<int>           ::= ("-")? <digit>+
<float>         ::= <int> "." <digit>+
<boolean>       ::= "true" | "false"
<char>          ::= <letter> | <digit> | "-" | "_" | "." | "?" | "!"
<letter>        ::= [a-z] | [A-Z]
<digit>         ::= [0-9]
```

A traversal order is a list of actions that are applied to a node in the tree.
The actions are applied in order. The actions are defined in the `action`
production. The `action` production is a dictionary with the following keys:

- `order` is a list of actions that are applied to a node in the tree.
- `visit` is an action predicate -- if the node satisfies the predicate,
   the node is added to a result list.
- `payload-map` is a function that maps the node to a new payload for
   the node. This payload map should not change the tree structure, only
   the payload of the node.
- `cond` is a conditional traversal -- if the node satisfies the predicate,
   the traversal order it is associated with is applied.
- `follow` is the direction of traversal: `up`, `down`, `sideways` (level order),
   or any other direction that is defined in the `follow` dispatch table.
- `select` is a selector that determines which nodes are selected for
   traversal. `all` selects all nodes, `none` selects no nodes, `rest`
   selects all nodes not previously selected, and any other selector that
   is defined in the `selector` dispatch table.
- `select-order` is the order in which the selected nodes are traversed.
   `identity` traverses the nodes in the order they were selected, `reverse`
   traverses the nodes in reverse order, `shuffle` traverses the nodes in a
   random order, and any other order that is defined in the `select-order`
   dispatch table.

The `args` and `kwargs` keys are used to pass arguments to the action predicates.

Some special environment variables that are automatically added to the
environment of the node are:

- `$node` is the node that the traversal order is being applied to.
- `$depth` is the depth of the node in the tree.
- `$num_children` is the number of children of the node.
- `$parent` is the parent of the node.
- `$root` is the root of the tree.
- `$results` is a global dictionary of results that the nodes are added to. The
  results are keyed by the value of the `result-name` argument in the `visit`
  action.

## Examples

Here is a simple pre-order traversal of all nodes in the tree:

```json
[ { "visit": "true", "result-name": "pre-order" }, { "follow": "down" } ]
```

If we wanted to only go to a depth of up to 2, we could use a conditional
traversal:

```json
[ { "cond": [
    { "pred" : "less?", "args" : ["$depth", 3],
      "order" : [ { "visit": "true", "result-name": "pre-order"},
                  { "follow": "down" } ]} ]} ]
```

Suppose we want to update the payloads to include a count of the number of
ancestors of the node. We can use a payload map to do this:

```json
[ { "visit": "true", "result-name": null },
  { "payload-map": "num-ancestors", "args": ["$node"] } ]
```

We see that specifying a `null` result name means that the node is not added
to the results list. This is useful when you want to update the payload of
the node without adding it to the results.

```json
[ { "visit": "is-leaf?" },
  { "payload-map": "node-stats", "args": ["$node"] },
  { "follow": "down", "select": "slice", "args": [0,-1] } ]
```
