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

Lower priority to implement:
* Binaries -- a message with two buttons (effectively shorthand for a switch)
* Yes/No -- a message with yes/no options (shorthand for a binary)
* User input boxes

There are also two special features:
* Data collections --
        a description added to a node which states that the user's choices are
        added to the ticket for the report.
* Terminals -- the end of a reporting flow. This must be manually implemented.
        All reporting flows must end in a terminal


## Geedka syntax

Note that the brackets are merely for ease of reading
-- they are not part of the language syntax.

### Messages
`m|[your message here]`

### Selections
`s|[number of options]|[selection description]`

`       option1|option2|` and so on

### Switches
`w|[number of options]|[switch description]`

`       option1|option2|` and so on

### Data collections
`d|[normal node description]`

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
w|3|    What is my favorite color?
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

