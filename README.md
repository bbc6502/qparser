# qparser
A Query Parser

<a href="https://github.com/bbc6502/qparser/actions">
    <img src="https://github.com/bbc6502/qparser/workflows/CI/badge.svg" alt="Build Status">
</a>
<a href="https://pypi.org/project/bbc6502/">
    <img src="https://badge.fury.io/py/qparser.svg" alt="Package version">
</a>

Usage
=====

    from qparser import query 
    terms = query("bob AND alice")

Syntax
======

    query = and | or | not | near | has | sequence | exact | token
    and = query "AND" query | "{" query { query } "}"
    or = query "OR" query | "[" query { query } "]"
    not = "NOT" query | "!" query
    has = "HAS" query
    near = query "NEAR" query
    sequence = query { query } | "(" query { query } ")"
    exact = "'" query { query } "'" | '"' query { query } '"'
    token = character { character }
    character = ! ( "AND" | "OR" | "NOT" | "NEAR" | "HAS" | "!" | "{" | "}" | "(" | ")" | "[" | "]" | "'" | '"' | space )
    space = " "

Examples
========

| Query                         | Matches                                             |
|-------------------------------|-----------------------------------------------------|
| bob AND alice                 | Bob sent a message to Alice                         |
| bob OR alice                  | Alice received a message                            |
| bob NOT alice                 | Bob sent a message                                  |
| bob NEAR alice                | Bob and Alice corresponded                          |
| bob HAS movie                 | Bob, Alice, and Carol went to the movies            |
| bob AND alice AND carol       | Bob and Alice sent a message that Carol intercepted |
| a message AND alice           | Bob sent a message to Alice                         |
| [ bob alice ] AND carol       | Alice didn't send the message to Carol              |
| bob sent AND alice received   | Bob sent a message that Alice received              |
