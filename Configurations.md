*The following introduction to Chainweb and configurations is a bit heads down:
More natural way would be to start with a Chainweb and the braiding rules. From
there one would define when a chains is mineable and how a Chainweb is computed.
One would next identify the mining language and show in a next step that this
language is regular. Constructing the finite omega automaton for that language
would lead the notion of configurations as the states of this automaton. The
fact that configurations abstract over the block height would then be a Theorem,
that one would have to proof.*

*Construction of the language would probably work best by translating the
braiding rules into an temporal logic formula (or maybe process algebra) and
constructing the alternating automaton for that. Or by constructing concurrent
NDAs and compositing those synchronously.*

# Chain Graph

We assume that the reader knows what a Chainweb is. In the following we quickly
recall a few basic notions and fix some notion.

Let $\newcommand{\Chains}{\mathcal{C}} \Chains$ be a set of chains in a
Chainweb with chain graph $\newcommand{\Graph}{\mathcal{G}}
\newcommand{\Edges}{\mathcal{E}} \Graph = (\Chains, \Edges)$.[^graphtypes]

[^graphtypes]: We generally distinguish between the chain graph and the Chainweb
graph. The vertexes of the former is the set of all chains and it defines the
dependencies between chains and constrains the braiding of a Chainweb. The
vertex that of the latter are all the blocks in a Chainweb and it represents the
direct dependencies between blocks.

A chain graph is a undirected regular graph with a good expansion. We generally
require that a chain graph is connected. When possible graphs are selected that
are optimal solutions for the degree-diameter problem. If an optimal solution is
not known for the required size, either one of the best known solutions is
selected. For graphs with many vertices/chains one may also uniformly pick
random regular graphs until a graph with a low diameter is found. (With high
probability the first or second candidate will have the required properties.)
When available chain graphs are also chosen to have a high level of
self-symmetries.

Usually, we assume the chain graph to be simple (no self loops). However, in 
some circumstances it is useful to include loops for each vertex. Sometimes
we may also represented the graph as directed graph with symmetric edge
relation.

We denote the (symmetric) adjacency matrix of $\Graph$ as
$\mathcal{M}(\Graph)$. When clear from the context we often identify
the graph with its matrix and just write $\Graph$ for both.

For a Chainweb we let $\mathcal{B}$ denote the set of blocks.

# Cut

Intuitively a *Cut* of a Chainweb is a set of blocks, one from each chain, that
can occur concurrently as state of consensus.

A *cut* is a selection of blocks with
1.  exactly one block from each chain such that
2.  blocks from neighboring chains are braided correctly and are at most one
    block apart in height.

Formally, a cut $C : \Chains \to \mathcal{B}$ is a mapping from chains to
blocks such that for each $c \in \Chains$
it holds that
1.  $chain(C(c)) = c$ (block are mapped from their respective chain) and
2.  for all $d \in \Chains$ with $\{c,d\} \in \Edges$ it holds that
    1.  $parent_d(C(c)) = C(d)$, or
    2.  $C(c) = parent_c(C(d))$, or
    3.  $parent_d(C(c)) = parent(C(d))$ and $parent(C(c)) = parent_c(C(d))$.
 
In the following we only consider correctly braided Chainwebs without forks. In
that case the second can be simplified to

$$
\newcommand{\abs}[1]{\left|#1\right|}
\abs{height(C(c)) - height(C(d))} \leq 1\,.
$$

# Configuration

Configurations form an equivalence relation on the cuts of a Chainweb. A
configuration abstracts from blocks and considers only on the relative height
differences of the blocks in a cut.

Given a cut $C$ the corresponding configuration is defined as the (skew
symmetric) square matrix $Conf(C)$, with

$$
Conf(C) = \left(height(C(c)) - height(C((d)))\right)_{c,d \in \Chains}\,.
$$

We call this representation of configurations *height difference matrices*.
Because Chainweb graphs are are connected, a single row (or column) of a height
difference matrix of a configuration determines all other rows (or column). By
pivoting on the the difference with respect to a single chain we can
represent a configuration as a *height difference vector*. Wlg.\ we will
pivot on chain 0 when use this representation.

Later we are also going to introduce other equivalent representations of
configurations.

From now on we are going to ignore Cuts and use the variable $C$ to denote a
configuration.

Not all height difference matrixes or height difference vectors represent a
configuration of a Chainweb. Actually, the chain graph determines the set of
configurations. For a chain graph $\Graph$ we denote the set of all
possible configurations of Chainwebs that use that graph with
$\newcommand{\Confs}{\Gamma}\Confs(\Graph)$. We just write $\Confs$ when
$\Graph$ is irrelevant or clear from the context.

In the following we are first investigating different ways to characterize the
set of configurations $\Confs(\Graph)$ for a given chain graph
$\Graph$. After that we are going to investigate properties of the
configurations and also how the configurations of a given Chainweb affect
certain properties of the Chainweb.

# Mining and Mineability

We start by characterizing the set of configurations semantically.

Given a height difference matrix or height difference vector, mining a chain
increases all entries of the respective row and decreases all entries of the
respective column. The values on the diagonal remain unchanged, i.e. are always
zero. For a configuration $C$ and a chain $c \in \Chains$ we define

$$
mine(C, c) = (D_{i,j})\,\text{ with }
\begin{cases}
    D_{i,j} + 1\, &\text{for } i\neq j \wedge i = c\,, \\
    D_{i,j} - 1\, &\text{for } i\neq j \wedge j = c\,, \\
    D_{i,j} &\text{otherwise}\,.
\end{cases}
$$

We say that a chain $c$ is blocked on a adjacent chain $d$ in a configuration
$C$, if and only if $\{c, d\} \in \Chains$ and the entry of $d$ in row $c$
is larger than zero, or, generally, if in any row the entry for $d$ is larger
than the entry for $c$.

A chain $c$ is mineable in a configuration $C$ if $c$ if is not blocked by any
(adjacent) chains. Formally, for any pivot row $p \in \Chains$

$$
mineable(C, c)\, \text{ iff }\, \forall d \in \Chains, \{c, d\} \in
\Edges \rightarrow C_{p, c} \leq C_{p, d}\,.
$$

For difference height matrix representation the definition can be simplified
by using the adjacent chains $d$ as respective pivot:

$$
mineable(C, c)\, \text{ iff }\, \forall d \in \Chains, \{c, d\} \in
\Edges \rightarrow C_{c, d} \leq 0\,.
$$

We overload the name $mineable$ and use it also to designate the set of chains
that are mineable in a configuration $C$:

$$
mineable(C) = \{c \in \Chains \mid mineable(C,c)\}
$$

For configurations $C, D$ and a chain $c \in \Chains$ we say that $C$ is a
$c$-predecessor of $D$, denoted as $C \prec^c D$, if and only if $mine(C,d) =
D$. Note that $c$ is unique in this defintion. We can thus also omit $c$ and
define $\prec \subseteq \Confs \times \Confs$ as $C \prec D$ if and only there
exists $c$ such that $C \prec^c D$. We call $D$ a ($c$-)successor of $C$ if
and only if $C \prec D$ ($C \prec^c D$, respectively).

We define reachability on configurations as the reflexive and transitive closure
over $\prec$. A configuration $D$ is reachable from a configuration $C$ if and
only if $C = D$ or there exist a configuration $E$ such that $C \prec E$ and $D$
is reachable from $E$.

For a sequence $c_0, \dots, c_{n-1}\,n \in \mathbb{N}$ of chains and
configurations $C$ and $D$ we say that $D$ is $c_0\dots c_{n-1}$-reachable from
$C$, denoted as $C \prec^{c_0\dots c_{n-1}} D$, if and only if there exist $C_i,
\dots, C_n$ for each $0 \leq i < n$ it holds that $C = C_0$, $D = C_n$, and $C_i
\prec^{c_i} C_{i+1}$.

The configuration $\bold{0}$, where all chains are at the same height, is the
unique configuration in which all chains are mineable.

$\bold{0} = \left(0_{i,j}\right)_{i,j \in \Chains}$

Finally, we define the set of configurations $\Confs(\Graph)$ of a Chainweb
with a given chain graph as the set of all configurations that are reachable
from configuration $\bold{0}$. As mentioned before we omit the graph when it is
irrelevant or clear from the context and just write $\Confs$ or just assume
assume that a configuration is a reachable configuration.

# Configuration Transition System

The transition system on the set $\Confs(\Graph)$ of all reachable
configurations of a chain graph is the tuple $(\Confs(\Graph), \prec)$, where
$\Confs(\Graph)$ is the set of states and $\prec$ is the transition relation.

One important property of this transition system is that the transition graph is
strongly connected, i.e. each state can be reached from each state. To see this,
note that each reachable configuration is mineable and the configuration
$\bold{0}$ can be reached from each state.[^note0] (Note that each state can be reached
from $\bold{0}$ by definition of $\Confs(\Graph)$.) We
can thus omit the initial configuration from the definition of the transition
system.

[^note0]: This is a bold claim that needs to be proven. We provide a proof below
(based on the automaton of the mining language). We could also do a more direct
(semantic) proof based on the height differences: each reachable configuration
must represent a partial order on the chains (TODO proof) and must thus of a
topological sorting. (the converse is not true, TODO proof) By definition the
lowest chain in this sorting is mineable. Note that this property is obvious for
Cuts, due to the absolute height values. So, it might be easier to proof 
certain properties of a Chainweb directly for Cuts.

Another property is that the degree of the transition graph is bounded by the
number of chains $\abs{\Chains}$. This follows directly from the definition of
$mineable$. There is exactly one successor configuration for each mineable chain.

We also note that the absolute values of the height differences between chains
are bounded by the length of the shortest path between the respective chains in
$\Graph$. For adjacent chains the absolute values are bounded by one, which
follows from the definition of $mine$ and $\bold{0}$. In general the diameter of
$\Graph$ is a bound all absolute values in the height difference matrix of a
configuration. Because $\Graph$ is connected it follows that $\Confs(\Graph)$ is
finite. We will formalize and prove this property later on.

## Labeled Transition Systems

We can collect additional properties of configurations of a Chainweb by 
labeling the transition system and observing the values of the labels.

The most straightforward labeling is to label each transition with the respective
chain that facilitates this transition: $(\Confs(\Graph), \Chains, \prec^\cdot)$,
where $\Confs(Graph)$ again is the set of states, $\Chains$ is that set of labels,
and $\prec^\cdot$ is the ternary transition relation.
Each run of this labeled transition system records the sequence of mined chains
and the (infinite) set of all possible (infinite) runs represents the set of all
orders in which chains can be mined.

Other interesting labelings include is sets of mineable chains in the source
configuration or just the count of mineable chains.

We can use those labeled transition systems, for instance, to investigate
whether for a given chain graph, all chains are mineable equally often, or
whether some chains are mineable more often than others. The answer to this
question may inform possible strategies for miners or of block rewards in a
blockchain based on Chainweb consensus. We also like to compute the histogram of
the number of mineable chains over all configurations. We will explorer different
ways to measure these properties further down.

# Language of a Chain Graph

Above we noted that the configuration transition system is finite and that it
can be labeled to record the sequence of mined chains that lead from one
configuration to another. This implies that the set of all sequences chains that
can be mined in a Chainweb for a given chain graph is a language that can be
recognized by a finite automaton.

We are now going formalize that language which leads to a syntactic
characterization of the set of configurations for a given chain graph and their
properties.

For a pair of adjacent chains $a,b \in Chains$, $\{a,b\} \in \Edges$, each of
$a$ and $b$ can be ahead at most one step of the the other chain. This means
that each word of the language must satisfy that
*   if an $a$ happens first there must be a $b$ before there can be another $a$
    and, conversely,
*   if a $b$ happens first there must be an $a$ before $b$ can happen again.
*   In between any other chain can occur.
This is is expressed by the following regular expression:

$$
    \underbrace{(\overline{a|b})}_{\text{any other chain}}
    \mid
        \underbrace{(a(\overline{a|b})^*b)}_{\substack{
            \text{if $a$ is first it} \\
            \text{is followed by $b$} \\
            \text{before another $a$}
        }}
        \mid
        \underbrace{(b(\overline{a|b})^*a)}_{\substack{
            \text{if $b$ is first it} \\ 
            \text{is followed by $a$} \\
            \text{before another $b$}
        }}
$$

Note that this expression does not accept the empty word. This pattern repeats
infinitely often, resulting in the following $\omega$-regular expression:

$$
\left((\overline{a|b})|(a(\overline{a|b})^*b)|(b(\overline{a|b})^*a)\right)^\omega
$$

The overall language must satisfy the respective expression for each edge in the
graph. The $\omega$-language $\def\lang#1{\mathcal{L}({#1})} \lang{\Graph}$ is
the intersection of the languages for all edges in $\Graph$:

$$
\bigcap_{(a,b) \in \Edges}
\left((\overline{a|b})|(a(\overline{a|b})^*b)|(b(\overline{a|b})^*a)\right)^\omega
$$

Example for a word in $\lang{\Graph}$:

$$
a b c a c b b a a c c b b\\
$$

Accordingly, the Büchi automaton for $\lang{\Graph}$ is constructed as the
alternating Büchi automaton that for each edge $(a,b) \in \Edges$ contains the
following subautomaton.

```tikz
\documentclass[crop,tikz]{standalone}
\usetikzlibrary {math,automata,positioning}
\begin{document}
  \begin{tikzpicture}[shorten >=1pt,auto,initial text=]
    \node[state,initial,accepting] (q_0) {$ab_=$};
    \node[state] (q_1) [above=of q_0] {$ab_>$};
    \node[state] (q_2) [below=of q_0] {$ab_<$};
    \path[->]
      (q_0)
        edge [bend left] node {$a$} (q_1)
        edge [bend left] node [swap] {$b$} (q_2)
        edge [loop right] node {$\overline{a|b}$} ()
      (q_1)
        edge [bend left] node {$b$} (q_0)
        edge [loop right] node {$\overline{a|b}$} ()
      (q_2)
        edge [bend left] node {$a$} (q_0)
        edge [loop right] node {$\overline{a|b}$} ()
      ;
  \end{tikzpicture}
\end{document}
```

Note that each conjunctive component is itself deterministic.

> (Alternatively, we could define the language temporal logic formula, or
> algebraically, e.g. through as a sub-monoid of the trace monoid implied by the
> dependency relation on chains.)

*Theorem*: The language is non-empty.

*Proof*: Let $\{c_0, \dots, c_{n-1}\} = \Chains$, then the word $(c_0\dots
c_{n-1})^\omega$ where all chains appear in turn is accepted by the alternating
Büchi automaton for $\lang{\Graph}$.

*Theorem*: The automaton can not deadlock.

*Proof*:

TODO:
*   Is above automaton minimal?
*   what is the minimal BDFA?
*   What is the minimal BNFA?
*   Is the language starfree?
*   characterize the language via its safety and liveness properties.

*Theorem*: In this automaton any of the accepting states could be used as
singleton Büchi acceptance condition while still accepting the same language. In
other words each accepting run visits each accepting state infinitely often.

*Theorem*: The $\lang{\Graph}$ is exactly the language produced by the
configuration transition system. (TODO, define that language via a Moore
automaton over the configuration transition system.)

*Theorem*: The states of the automaton are exactly the configurations, i.e. they
encode the height difference between chains.

TODO: 
*   Consider quotient languages for interesting properties, like number
    of mineable chains, set of mineable chains, and possibly other properties.

> What would be the minimal automaton that preserves the number of
> mineable chains for each state? There are transitions that do not change
> the number of mineable chains. How can we characterize those?

## Remarks

Note that the definition of a configuration and the mining function does not
depend on the graph.

Only the definition of mineability is constrained by the chain graph $\Graph$.

It is a non-trivial problem to determine or count the reachable
configurations for a given Graph.
Another interesting question is what connected graph would maximize the
number of configurations.

We are particularly interested in graphs that maximize the (out-)degree
of the configuration transition graph, because that determines
how many chains are mineable in concurrently.

A more fundamental question is the class of languages that
can be defined in this way through graphs.

### Trace Monoid

Configurations can be seen as a partial trace Monoid over the alphabet
of chains. The dependency graph is obtained from the chain by building
the tensor product with a pair graph $G_{TM} = (V_{TM}, E_{TM})$ with
$V_{TM} = \Chains \times \{0,1\}$ and

$$
\left((c, i),(d, j)\right) \in E_{TM} \text{ iff } i \neq j \wedge
\begin{cases}
  c = d\, \text{ or }\\
  (c, d) \in \Edges\,.
\end{cases}
$$

The independency relation is defined as the complement of the
dependency graph. The trace monoid for configurations is
then defined over the language $(c_0, \dots, c_1, \dots)^*$.

TODO: what properties of configurations does the trace automaton
preserve? Does it preserve the number of mineable chains? That would be
very useful but seems to be wrong.

# Configuration Markov Chain

Each transition to a new configuration corresponds to exactly one mineable
chain. In a Chainweb the overall hash power is evenly distributed over all
mineable chains. For the purpose of this document we also assume that the
overall hash power is constant.

We can therefore assign to each outgoing transition in the configuration
automaton a probability, where the probabilities for the outgoing transitions of
a given configuration are uniformly distributed.

TODO: define $P$

Each configuration that is reachable from the empty configuration can also reach
the empty configuration. (Note, that the state space of the Markov chain is
defined to only contain configurations that are reachable from the initial
configuration.) From this is follows that the Markov chains is irreducible.

To see this, note that mining a particular chain can only block this chain
itself. It may unblock neighboring chains, but it can not cause any other chain
to become blocked. As a consequence the empty configuration can be reached at
any point by stopping to mine on chains that are furthest ahead and letting
other chains catch up until all chains are at the same height.

This also directly implies that all reachable configurations are mineable.
Another reason is that

Representation of Configurations as DAGs:

In particular, the entries for neighboring vertexes are either 1, -1, or 0 and 
$Conf(C) \mathcal{M}(\Graph)$ contains only entries of those values.

TODO: the conf is determined by the entries for neighboring nodes. Only one
value (0 or 1) per pair is needed.

A chain is mineable if it is not ahead of any direct neighbor chain. Each
configuration corresponds to an acyclic directed subgraph of $\Graph$ (the
reverse is not true). A chain is mineable when there are no incoming edges.

A configuration can be obtained from another configuration by mining a mineable
chain. A chain is mined by

*   removing all incoming edges of the chain and
*   adding outgoing edges for each edge in $\Graph$ that is not in the
    configuration.

Note that if the original graph was acyclic, then the resulting graph is
acyclic, too, because the source of all new edges has no incoming edges. Hence,
the result of mining a mineable chain on a configuration is indeed a
configuration.

Since, there are only finitely many configurations, we obtain a finite automaton
that models the transition between configurations.

The empty configuration is the unique configuration in which all chains are
mineable. This configuration is defined as the initial configuration.

Each configuration that is reachable from the empty configuration can also reach
the empty configuration. (Note, that the state space of the Markov chain is
defined to only contain configurations that are reachable from the initial
configuration.) From this is follows that the Markov chains is irreducible.

To see this, note that mining a particular chain can only block this chain
itself. It may unblock neighboring chains, but it can not cause any other chain
to become blocked. As a consequence the empty configuration can be reached at
any point by stopping to mine on chains that are furthest ahead and letting
other chains catch up until all chains are at the same height.

This also directly implies that all reachable configurations are mineable.
Another reason is that a non-mineable configuration would necessarily contain a
cyclic dependency.

TODO: can we provide an algebra? What are the group equations for the automaton?

TODO: can we derive the quotient automaton with respect to the number of
mineable chains?

Each transition changes the number of mineable chains by $[-1, diameter many
chains]$. That determines the diameter of the automaton and the length of
cycles.

### Continuous-Time Markov Chain on Configurations

We assume that the overall hash power is constant and evenly distributed over
all mineable chains. Each transition to a new configuration corresponds to
exactly one mineable chain.

The overall holding time for each configuration is thus distributed evenly
across all mineable chains. Therefore the transition rate between configurations
is either the overall rate multiplied by the number of mineable chains if there
is a transition or 0 when there is no transition between the configurations.

Overall, the transition between configurations can be modeled as a
continuous-time Markov chain (CTMC) where the entries of the q matrix are either
0 or the number of mineable chain in the source configuration multiplied by the
constant overall block rate of the Chainweb.

The initial configuration of the system is the empty configuration.

Our goal is to analyze:

*   How much time is spent in each configuration?
*   How much time is spent on configurations with a given number of mineable
    chains?
*   For a given graph, how much time is spent on each chain? How is it
    distributed?
*   What properties of the graph affect the distribution of time spent on each
    chain.
*   Do all chains receive equal amounts of hash power?

*   What are possible mining strategies? Should mining rewards depend on the
    hash power that a chain receives? Or is that not needed? (or does chain
    selection for miners involves a prisoner dilemma situation?)
