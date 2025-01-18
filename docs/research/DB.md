---
tags:
  - research
  - github
  - info
  - resource
  - teaching
---

# Database Research 

I currently work on 

- DB + AI: 
  - Learned indexes
  - LSH-based indexes
- Vector Databases
  - Efficient and scalable index construction
  - Efficient query processing
- Data Management issue for High-dimensional or Metric Spaces
- Graph
  - kdd? icde
- Misc



head uses pooling to compute the state flow F (s; θ). Since the Fe(s;θ) P (s′|s;θ) !2graphincludesonlyunassignedvariables,allactionsrelatedto
′F′ LFL(s,s;θ)= log +log ′ +E(s→s)
these variables are considered in the probability distribution.
Fe(s′;θ) PB(s|s ;θ)
.
The GFNSAT architecture aligns the PF (s′|s; θ) with the
(7) The energy terms empower FL-GFN to generate solutions that are more likely to achieve high rewards by directing the search process toward optimal solutions. In the context of SAT problems, FL-GFN can explore a wide range of solutions, effectively minimizing conflicts and producing higher-quality
results.
III. GFNSAT: A GFLOWNET FRAMEWORK FOR GRAPH-BASED SAT SOLVING
Our objective in this paper is to construct a distribution over variable assignments to accelerate SAT solving during the warming-up stage. Figure 2 illustrates the overview of GFNSAT. Given a CNF, the GNN generates a probability distribution over possible assignment actions. Upon making an assignment decision, the CNF undergoes simplification through CDCL and transitions to the next state, where the GNN generates another probability distribution to determine the next round of assignment. Until the CNF is solved, the solution is evaluated based on the proportion of conflict- free assignments, which serves as the reward. The GNN parameters are then optimized by minimizing the GFlowNet loss, ensuring that the policy πθ aligns proportionally with the reward function. This process allows the model to effectively assimilate diverse solving experiences and strategically utilize them within the solution space.
A. State Representation
We build upon the setup of Graph-Q-SAT [5], which rep- resents the CNF formula as a graph, where variables and clauses are connected through directed edges. Each variable vertex has two possible actions: setting the variable to TRUE or FALSE. As shown in Figure 3, a GNN processes the graph through message passing to generate graph embeddings, which are then decoded through two output heads. The first head employs Softmax to model the forward probability distribution PF (s′|s; θ) for valid variable assignments, while the second
GFlowNets objective, generating diverse SAT solving strate- gies that are proportional to the rewards, thereby enhancing the SAT solution derivation process.