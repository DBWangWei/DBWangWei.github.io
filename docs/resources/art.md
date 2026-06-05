# Computational Art Gallery

Algorithmic visualizations generated from research concepts and data.

/// html | div.art-gallery-container

<div class="art-gallery-grid">
  <div class="art-piece">
    <div class="art-canvas-wrapper">
      <canvas id="art-network" class="computational-art-canvas" data-art-type="network" data-animated="true"></canvas>
    </div>
    <div class="art-piece-info">
      <h3 class="art-piece-title">Research Collaboration Network</h3>
      <p class="art-piece-description">A dynamic visualization of research collaborations and paper connections, where nodes represent publications and edges show cross-citations and co-authorship patterns.</p>
    </div>
  </div>

  <div class="art-piece">
    <div class="art-canvas-wrapper">
      <canvas id="art-pde" class="computational-art-canvas" data-art-type="pde" data-animated="true"></canvas>
    </div>
    <div class="art-piece-info">
      <h3 class="art-piece-title">Wave Equation Simulation</h3>
      <p class="art-piece-description">Visual representation of PDE solutions using neural operators. This shows a wave equation propagating from the center, demonstrating AI4S research on solving partial differential equations.</p>
    </div>
  </div>

  <div class="art-piece">
    <div class="art-canvas-wrapper">
      <canvas id="art-highdim" class="computational-art-canvas" data-art-type="highdim" data-animated="true"></canvas>
    </div>
    <div class="art-piece-info">
      <h3 class="art-piece-title">High-Dimensional Space Projection</h3>
      <p class="art-piece-description">Research areas (DB, LLM, AI4S) embedded in 2D space. Each cluster represents papers in that domain, showing how different research topics relate in the embedding space.</p>
    </div>
  </div>

  <div class="art-piece">
    <div class="art-canvas-wrapper">
      <canvas id="art-vector" class="computational-art-canvas" data-art-type="vector" data-animated="true"></canvas>
    </div>
    <div class="art-piece-info">
      <h3 class="art-piece-title">Dynamic Vector Field</h3>
      <p class="art-piece-description">A flowing vector field representing gradient flows in optimization landscapes. Related to learned index structures and vector database research.</p>
    </div>
  </div>

  <div class="art-piece">
    <div class="art-canvas-wrapper">
      <canvas id="art-neural" class="computational-art-canvas" data-art-type="neural" data-animated="true"></canvas>
    </div>
    <div class="art-piece-info">
      <h3 class="art-piece-title">Neural Operator Flow</h3>
      <p class="art-piece-description">Particle flow through a neural operator transformation, visualizing how data propagates through learned function approximations in AI4S applications.</p>
    </div>
  </div>
</div>

///

## About This Gallery

This gallery showcases **algorithmic art** generated from research concepts in databases, machine learning, and AI for science. Each piece is:

- **Computationally generated** using JavaScript and Canvas API
- **Animated in real-time** with mathematical functions
- **Inspired by research** in vector databases, neural operators, and high-dimensional data

The visualizations are not just decorative—they represent actual concepts from ongoing research:

- **Network graphs** model collaboration patterns and citation networks
- **PDE simulations** demonstrate neural operator learning for scientific computing
- **Vector fields** represent optimization landscapes in learned index structures
- **High-dimensional projections** show semantic clustering of research topics

All code is open source and part of this website's repository. The art adapts to your theme (light/dark mode) and pauses when the page is hidden to save resources.

---

*"Mathematics is an art practiced with highly specialized tools."* — Creating beautiful patterns from the mathematical foundations of computer science.
