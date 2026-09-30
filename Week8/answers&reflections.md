# AI Laboratory: Answers and Reflections

## Part I & II: Probability and Bayesian Networks

**Question 1: Why is this decomposition useful for generating text?**
The autoregressive decomposition breaks the complex joint probability of an entire sentence into a sequence of simpler, conditional probabilities. This mirrors the left-to-right process of generating text step-by-step, allowing a model to predict the next token based on the history of tokens generated so far.

**Question 2: What independence assumption is being made by this network?**
The first-order Markov language model assumes that the current token depends only on the immediately preceding token, entirely independent of all prior history.
Expressed in probability notation: $P(X_t \vert{} X_1, X_2, \dots, X_{t-1}) = P(X_t \vert{} X_{t-1})$.

## Part III & IV: Conditional Probability Table

**Question 3: Construct the conditional probability distribution for specific words.**
Based on the provided dataset, the conditional probabilities $P(\text{next word} \mid \text{current word})$ are:

* **the**: `{'cat': 0.5, 'dog': 0.5, 'mat': 0.333, 'rug': 0.333, 'park': 0.333}`
* **cat**: `{'sat': 0.667, 'ran': 0.333}`
* **dog**: `{'sat': 0.667, 'ran': 0.333}`
* **sat**: `{'on': 1.0}`
* **ran**: `{'to': 1.0}`
* **Zero-probability transitions**: Any sequence not observed in the training data (e.g., $P(\text{dog} \mid \text{cat}) = 0$) has a zero probability.

## Part VI: Inspecting the LLM-Generated Code

**Question 4: Where in the program are the transition counts stored?**
The transition counts are stored in a nested dictionary (e.g., `transition_counts`), which maps the `current_word` to a sub-dictionary of `next_word` frequency counts.

**Question 5: Where is $P(X_t\vert{}X_{t-1})$ computed?**
It is computed in the initialization loop where the count of a specific transition is divided by the total number of transitions from that state (`count / total_transitions`).

**Question 6: How does the program choose the next word?**
The program can operate in two modes:

1. **Greedy:** Always choosing the word with the highest probability using `max()`.
2. **Sampling:** Choosing the next word by sampling from the probability distribution using `random.choices()` weighted by the computed probabilities. Sampling respects the probabilistic nature of the network, whereas greedy selection is deterministic.



**Question 7: What happens if the program encounters a word for which no transition has been observed?**
The program will raise a `KeyError` or halt unexpectedly because the dictionary does not contain a probability distribution for an unobserved state.

## Part VII: Testing the Probability Model

**Question 8: If one of the totals is 0.87, what does this tell you about the implementation?**
It indicates a bug in the implementation. For a valid probability model, the sum of probabilities for all possible next states from a given current state must strictly equal 1.0 ($\sum_v P(v\vert{}w) = 1$). A sum of 0.87 means the code is either failing to count all transitions, calculating the denominator incorrectly, or suffering from severe floating-point precision loss.

## Part VIII & X: Predicting and Generating Text

**Question 9: Are the most probable predictions always the same as the words that you would personally expect?**
No. A simple probability model strictly reflects the mathematical frequencies of the training text without semantic understanding. Human linguistic expectations draw on vast real-world context, logic, and grammar, which this constrained first-order model lacks.

**Question 10: Compare the two sets of generated sentences. Which mode produces more variation? Why?**
Sampling produces significantly more variation. Greedy generation repeatedly selects $\arg\max_w P(w\vert{}w_{\text{previous}})$, which leads to a deterministic, repeating cycle every time it starts with the same token. Sampling generates text probabilistically based on weights, allowing it to explore different valid paths in the Bayesian network.

## Part XI, XII & XIII: Second-Order Bayesian Network

**Question 11: How does the second-order model differ from the first-order model?**

1. **Graph structure:** Nodes now have two parents ($X_{t-2} \rightarrow X_t \leftarrow X_{t-1}$) instead of one.


2. **Conditional probability table:** The table conditions on a tuple of two words $P(X_t \vert{} X_{t-2}, X_{t-1})$ rather than a single word.


3. **Context available:** It utilizes a larger window (2 preceding words), allowing it to capture longer-term dependencies.


4. **Data needed:** It requires exponentially more data to reliably estimate probabilities because the state space of possible word pairs is vastly larger than single words.



**Question 12: Why does increasing the amount of context potentially improve prediction? Why can it simultaneously make the model harder to estimate from limited data?**
Increasing context restricts ambiguity, allowing for more accurate and grammatically coherent predictions (e.g., knowing the previous two words narrows down logical next words). However, it makes the model harder to estimate because the size of the conditional probability table grows exponentially. With limited data, most word-pair contexts will have zero observations, leading to data sparsity and an inability to generate words when encountering unseen context pairs.

## Part XV & Final Question: Reflections

**Question 13: Why is Approach B preferable when constructing an intelligent system?**
Approach B is preferable because it explicitly defines the intended probabilistic model ($P(X_t\vert{}X_{t-1})$) and its behavioral invariants. By specifying the mathematical model, developers can clearly distinguish the conceptual design from the code implementation. This makes it possible to validate the generated code using strict probabilistic invariants (like checking if probabilities sum to 1) rather than blindly trusting a black-box output.

**Question 14: What did thinking of the language model as a Bayesian network give you?**
Viewing the language model as a Bayesian network provided:

* **A factorisation of the joint distribution:** It mathematically justified breaking the complex sequence of words into computable, step-by-step conditional probabilities via the chain rule.


* **A principled method for generation:** It outlined how generation is directly tied to traversing the network sequentially by sampling from the conditional probability table at each node.


* **A way to reason about independence assumptions:** It made clear exactly what information was being discarded (e.g., everything before $X_{t-1}$ in a first-order model) and allowed for structured analysis of how increasing the context window changed the network structure.



---

## Final Reflection: LLM Usage and Validation

During this laboratory, the LLM was used as an implementation assistant by providing it with strict behavioral and probabilistic specifications (Approach B) rather than open-ended requests. This ensured the LLM generated conditional probability tables based on explicit frequency counting rather than defaulting to generic machine learning libraries.

**Validation and Code Correction Example:**
While inspecting and testing the LLM-generated code for text generation, a critical issue was identified during the "Greedy Generation" testing. Because greedy generation strictly chooses the most probable next word, the model got trapped in an infinite loop: `the` $\rightarrow$ `cat` $\rightarrow$ `sat` $\rightarrow$ `on` $\rightarrow$ `the`, causing a `KeyboardInterrupt`.

To correct this, I modified the LLM's raw output by introducing a structural safeguard. I added a `max_length=20` parameter to the `generate_sentence` function and updated the `while True:` loop to `while len(sentence) < max_length:`. This correction ensured that deterministic cycles would cleanly terminate, demonstrating the importance of understanding the model's behavior to safely validate and constrain LLM-generated code.