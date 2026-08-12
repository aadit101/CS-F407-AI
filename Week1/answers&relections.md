# AI Laboratory: Neural Models Reflections

## Deliverable 1: Task 1 Problem Specification

**1. Input, Output, and Examples:**
*   **Input Space ($X$):** Binary vectors of length 2, representing two sensors: $\{0,1\}^2$.
*   **Output Space ($Y$):** A single binary value $\{0, 1\}$ representing the disagreement warning.
*   **Labelled Examples:** $(0,0) \rightarrow 0$, $(0,1) \rightarrow 1$, $(1,0) \rightarrow 1$, $(1,1) \rightarrow 0$.

**2. Linear Separability Explanation:**
If these four points are plotted on a 2D plane, the positive class points $(0,1)$ and $(1,0)$ sit on opposite corners of a square from the negative class points $(0,0)$ and $(1,1)$. It is geometrically impossible to draw a single straight decision boundary that separates the 0s from the 1s. 

**3. Linear Model Prediction:**
If trained with only a single affine transformation followed by a sigmoid output, the model will fail to learn the XOR function. It will likely collapse to predicting a constant 0.5 probability for all inputs to minimize overall error, unable to capture the non-linear boundary.

---

## Deliverable 2: Model Design and Validation Criteria (Task 2)

**Baseline Design:** 2 inputs $\rightarrow$ 2 hidden units $\rightarrow$ 1 output.

**1. Why is the hidden nonlinearity scientifically necessary here?**
A stack of affine layers without nonlinear activations collapses mathematically into a single affine map. Nonlinearity is required to distort the feature space so the XOR problem becomes linearly separable in the hidden layer.

**2. Why is sigmoid plus binary cross-entropy a sensible engineering pairing for the output?**
The target is a single binary yes/no answer. The sigmoid function squashes the affine output into a valid probability distribution $[0, 1]$, and binary cross-entropy perfectly measures the divergence between this predicted probability and the true binary label.

**3. Validation Criteria:**
*   The final scalar loss approaches $0$.
*   All four thresholded predictions exactly match the target labels.
*   The gradients (`parameter.grad`) are non-zero during training, indicating an active learning signal.

---

## Deliverable 3: LLM Prompts and Corrections (Task 3)

**Prompt Used:**
> Generate minimal PyTorch code for a 2-2-1 neural network to solve the XOR problem. Use the four standard XOR examples. Use a ReLU hidden activation, a linear output layer paired with BCEWithLogitsLoss, and random weight initialization. Train using full-batch SGD for 2000 steps. After training, report the final loss, all four probabilities, thresholded labels, and the first-layer weight gradient tensor (`parameter.grad`) after a backward pass. Set a random seed for reproducibility.

**Corrections Made to Generated Code:**
The LLM successfully generated the standard boilerplate. However, for the symmetry experiment (Task 4C), the LLM naturally defaulted to random initialization. I had to manually override its initialization step with `nn.init.zeros_` to test the scientific hypothesis regarding identical weights.

---

## Deliverable 6: Reflection Questions

**1. What did the XOR experiment demonstrate about the difference between depth and nonlinearity?**
It demonstrated that depth alone is insufficient for complex representations. A stack of affine layers without nonlinear hidden activations simply collapses into a single affine map. The hidden nonlinearity is required to distort the feature space so XOR becomes linearly separable.

**2. In your successful run, what evidence showed that backpropagation supplied a useful learning signal rather than merely a nonzero gradient?**
The primary evidence was that the scalar loss monotonically decreased toward zero and all four predictions perfectly matched the targets. A non-zero gradient simply proves parameters are moving; driving the loss to zero proves the signal correctly guided the weights toward the optimal boundary.

**3. Why did identical/zero weight initialisation prevent the two hidden units from learning distinct features?**
This demonstrated the "symmetry problem." Because both hidden units had identical weights, they produced identical outputs for any given input, causing backpropagation to deliver the exact same gradient to both units. Without random initialization to break this symmetry, the units remain locked together and cannot learn the distinct boundaries required to solve XOR.

**4. How did changing the hidden activation affect the gradient you observed? Distinguish the scientific explanation from the engineering observation.**
*   **Scientific Explanation:** Different activations dictate the local Jacobian factors during the chain rule. A sigmoid unit contributes small derivatives (max 0.25), and nearly zero if saturated, potentially shrinking gradients deeper in the network. A ReLU unit contributes a strict derivative of 1 if active, avoiding gradient shrinkage.
*   **Engineering Observation:** In practice, the ReLU model exhibited larger early gradient norms and required fewer steps to reliably converge, whereas the sigmoid model started with much smaller gradient norms and learned slower.

**5. Why must the output layer and loss be selected together according to the task?**
The output activation must format the network's raw numbers into a shape that matches the target data, and the loss must properly measure the divergence of that specific shape. For binary outcomes, a single logit with sigmoid correctly maps to a $[0, 1]$ probability, paired perfectly with binary cross-entropy. For multi-class outcomes, 3 logits with softmax map to a probability vector, paired with categorical cross-entropy.

**6. Give one example where the LLM improved your engineering productivity and one example where human verification was essential.**
*   **Productivity:** The LLM generated the PyTorch boilerplate—such as the training loop, zeroing gradients, and loss computations—in seconds, accelerating the engineering phase.
*   **Human Verification:** Human verification was essential for the symmetry experiment. An LLM prompted to write a working network will naturally apply random initialization. I had to explicitly structure the test and intercept the weights to zero them out in order to test the scientific hypothesis.

**7. Which tests in this laboratory would you keep if the model were scaled up, and which would become too expensive?**
*   **Keep:** Tracking the scalar loss trajectory, evaluating batch accuracy, and running standard forward passes for evaluation are practices that scale efficiently.
*   **Too Expensive:** Printing every individual prediction, manually inspecting raw weight tensors, and running exhaustive finite-difference gradient checks become computationally and cognitively impossible when dealing with models featuring tens of millions of parameters.