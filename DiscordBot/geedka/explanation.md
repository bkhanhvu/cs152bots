# Geedka

## What is this?

Geedka is a basic language in which you can specify the structure of a moderation flow.
It is minimal, and intentionally as simple as possible.

The name *Geedka* comes from the Somali word for "tree".

## Geedka syntax

Geedka statements are one line (TODO: allow multiline and comments),
with a separate part per each section of a moderation flow node.

There are several kinds of supported nodes:

* Messages -- a simple message with text shown to the user
* Selections -- a dropdown with several options
* Switches -- a message with several buttons
* Yes/No -- a message with yes/no options (shorthand for a binary)

TODO:
* User input boxes (modals)

There is also one special feature:
* Terminals -- the end of a reporting flow.
        This is manually implemented by the technical team.
        All reporting flows must end in a terminal


## Geedka syntax

Note that the brackets are merely for ease of reading
-- they are not part of the language syntax.

Geedka is not sensitive to whitespace,
so you can indent however much or little you would like.
However, it is likely bad style to not indent.
Additionally, Geedka is sensitive to newlines --
multiline node specifications are on the TODO list but low priority.

### Messages
`m|[your message here]`

### Selections
`s|[selection description]`

`       option1|option2|` and so on

`               [node specification for child generated at option1] `
and so on

### Switches
`w|[switch description]`

`       option1|option2|` and so on

`               [node specification for child generated at option1] `
and so on


### Yes/No Selections
`y|[question]`

Note that the options for a yes/no selection do not need to be enumerated,
so all of its children follow immediately after it.

### Input boxes (modals)
`i|[question]`

`       input box name1|input box name2|` and so on

### Terminals
`t`

### Ordering
The description file for Geedka should be ordered such that the children of a node
follow the description of a node in the order in which they should appear,
excepting the children of the children.

Leading or trailing whitespace does not matter, so it can be inserted to clarify relationships between nodes.

## An example

Suppose we want to represent the following moderation flow:

```
        +-----------------------------+
        | Let's play a guessing game. |
        +-----------------------------+
                       |
        +----------------------------+
        | What is my favorite color? |
        |          (switch)          |
        +----------------------------+
           |           |          |
       +-----+     +-------+  +------+
       | Red |     | Green |  | Blue |
       +-----+     +-------+  +------+
          /           |             \
         /            |              \
   +--------+   +----------+  +----------------------+
   | Wrong! |   | Correct! |  | Close, but no cigar. |
   +--------+   +----------+  +----------------------+
```

We would represent this in Geedka as follows:

```
m|      Let's play a guessing game
w|      What is my favorite color?
        Red | Green | Blue
        m|Wrong!
                t
        m|Correct!
                t
        m|Close, but no cigar.
                t
```

## How to use the Geedka tool

There are a small number of steps
that need to be carried out to use to the tool.
1. Once you have written a config file (it should be called `config.geedka`),
navigate to the `geedka` directory in terminal.
2. Then, run `make` to generate the necessary files.
3. Finally, run `make run` to run the program.

Additionally, you can run `make clean` to remove all the generated files.

