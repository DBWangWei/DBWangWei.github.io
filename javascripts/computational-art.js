/**
 * Computational Art Gallery
 * Generates algorithmic art from research data
 */

class ComputationalArt {
  constructor(canvasId, options = {}) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;

    this.ctx = this.canvas.getContext('2d');
    this.options = {
      type: options.type || 'network',
      animated: options.animated !== false,
      colors: options.colors || this.getDefaultColors(),
      ...options
    };

    this.animationId = null;
    this.time = 0;
    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    const rect = this.canvas.getBoundingClientRect();

    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.ctx.scale(dpr, dpr);

    this.width = rect.width;
    this.height = rect.height;
  }

  getDefaultColors() {
    // Check if dark mode
    const isDark = document.body.getAttribute('data-md-color-scheme') === 'slate';

    if (isDark) {
      return {
        primary: '#667eea',
        secondary: '#764ba2',
        accent: '#f59e0b',
        background: '#1e293b',
        text: '#e2e8f0'
      };
    }

    return {
      primary: '#667eea',
      secondary: '#764ba2',
      accent: '#f59e0b',
      background: '#ffffff',
      text: '#1e293b'
    };
  }

  start() {
    if (this.options.animated) {
      this.animate();
    } else {
      this.draw();
    }
  }

  stop() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
  }

  animate() {
    this.time += 0.01;
    this.draw();
    this.animationId = requestAnimationFrame(() => this.animate());
  }

  draw() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    switch (this.options.type) {
      case 'network':
        this.drawCollaborationNetwork();
        break;
      case 'pde':
        this.drawPDEVisualization();
        break;
      case 'highdim':
        this.drawHighDimensionalSpace();
        break;
      case 'vector':
        this.drawVectorField();
        break;
      case 'neural':
        this.drawNeuralOperator();
        break;
      default:
        this.drawCollaborationNetwork();
    }
  }

  drawCollaborationNetwork() {
    // Simulate research collaboration network as particles with connections
    const nodeCount = 30;
    const nodes = [];

    // Generate nodes representing papers/researchers
    for (let i = 0; i < nodeCount; i++) {
      const angle = (i / nodeCount) * Math.PI * 2;
      const radius = this.width * 0.3;
      const centerX = this.width / 2;
      const centerY = this.height / 2;

      // Add some noise for organic feel
      const noise = Math.sin(this.time * 0.5 + i) * 20;

      nodes.push({
        x: centerX + Math.cos(angle) * (radius + noise),
        y: centerY + Math.sin(angle) * (radius + noise),
        size: 3 + Math.random() * 3,
        connections: Math.floor(Math.random() * 3) + 1
      });
    }

    // Draw connections
    this.ctx.strokeStyle = this.options.colors.primary + '20';
    this.ctx.lineWidth = 1;

    nodes.forEach((node, i) => {
      for (let j = 0; j < node.connections; j++) {
        const targetIdx = (i + Math.floor(Math.random() * 5) + 1) % nodeCount;
        const target = nodes[targetIdx];

        const gradient = this.ctx.createLinearGradient(node.x, node.y, target.x, target.y);
        gradient.addColorStop(0, this.options.colors.primary + '40');
        gradient.addColorStop(1, this.options.colors.secondary + '20');

        this.ctx.strokeStyle = gradient;
        this.ctx.beginPath();
        this.ctx.moveTo(node.x, node.y);
        this.ctx.lineTo(target.x, target.y);
        this.ctx.stroke();
      }
    });

    // Draw nodes
    nodes.forEach(node => {
      const gradient = this.ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, node.size);
      gradient.addColorStop(0, this.options.colors.primary);
      gradient.addColorStop(1, this.options.colors.secondary);

      this.ctx.fillStyle = gradient;
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.size, 0, Math.PI * 2);
      this.ctx.fill();
    });
  }

  drawPDEVisualization() {
    // Simulate a wave equation solution
    const gridSize = 40;
    const cellWidth = this.width / gridSize;
    const cellHeight = this.height / gridSize;

    for (let i = 0; i < gridSize; i++) {
      for (let j = 0; j < gridSize; j++) {
        const x = i * cellWidth;
        const y = j * cellHeight;

        // Wave function
        const dist = Math.sqrt(
          Math.pow(i - gridSize / 2, 2) + Math.pow(j - gridSize / 2, 2)
        );
        const wave = Math.sin(dist * 0.3 - this.time * 2) * 0.5 + 0.5;

        const alpha = wave * 0.6;

        // Create color gradient based on wave value
        const r = parseInt(this.options.colors.primary.slice(1, 3), 16);
        const g = parseInt(this.options.colors.primary.slice(3, 5), 16);
        const b = parseInt(this.options.colors.primary.slice(5, 7), 16);

        this.ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
        this.ctx.fillRect(x, y, cellWidth, cellHeight);
      }
    }
  }

  drawHighDimensionalSpace() {
    // Visualize high-dimensional data projection
    const pointCount = 100;
    const centerX = this.width / 2;
    const centerY = this.height / 2;

    // Create clusters representing different research areas
    const clusters = [
      { x: centerX - 100, y: centerY - 80, color: this.options.colors.primary, label: 'DB' },
      { x: centerX + 80, y: centerY - 60, color: this.options.colors.secondary, label: 'LLM' },
      { x: centerX - 20, y: centerY + 90, color: this.options.colors.accent, label: 'AI4S' },
    ];

    clusters.forEach(cluster => {
      for (let i = 0; i < pointCount / 3; i++) {
        const angle = Math.random() * Math.PI * 2;
        const radius = Math.random() * 60;

        const x = cluster.x + Math.cos(angle) * radius + Math.sin(this.time + i) * 5;
        const y = cluster.y + Math.sin(angle) * radius + Math.cos(this.time + i) * 5;

        const size = 2 + Math.random() * 2;
        const alpha = 0.4 + Math.random() * 0.3;

        this.ctx.fillStyle = cluster.color + Math.floor(alpha * 255).toString(16);
        this.ctx.beginPath();
        this.ctx.arc(x, y, size, 0, Math.PI * 2);
        this.ctx.fill();
      }

      // Draw cluster labels
      this.ctx.fillStyle = this.options.colors.text;
      this.ctx.font = 'bold 14px sans-serif';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(cluster.label, cluster.x, cluster.y);
    });
  }

  drawVectorField() {
    // Draw a dynamic vector field
    const gridSize = 20;
    const stepX = this.width / gridSize;
    const stepY = this.height / gridSize;

    this.ctx.strokeStyle = this.options.colors.primary + '60';
    this.ctx.lineWidth = 1.5;

    for (let i = 0; i < gridSize; i++) {
      for (let j = 0; j < gridSize; j++) {
        const x = i * stepX + stepX / 2;
        const y = j * stepY + stepY / 2;

        // Calculate vector direction and magnitude
        const dx = Math.sin(x * 0.02 + this.time) * Math.cos(y * 0.02);
        const dy = Math.cos(x * 0.02) * Math.sin(y * 0.02 + this.time);

        const magnitude = Math.sqrt(dx * dx + dy * dy);
        const length = magnitude * 15;

        // Draw arrow
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);
        this.ctx.lineTo(x + dx * length, y + dy * length);
        this.ctx.stroke();

        // Draw arrowhead
        const arrowSize = 4;
        const angle = Math.atan2(dy, dx);
        this.ctx.beginPath();
        this.ctx.moveTo(x + dx * length, y + dy * length);
        this.ctx.lineTo(
          x + dx * length - arrowSize * Math.cos(angle - Math.PI / 6),
          y + dy * length - arrowSize * Math.sin(angle - Math.PI / 6)
        );
        this.ctx.moveTo(x + dx * length, y + dy * length);
        this.ctx.lineTo(
          x + dx * length - arrowSize * Math.cos(angle + Math.PI / 6),
          y + dy * length - arrowSize * Math.sin(angle + Math.PI / 6)
        );
        this.ctx.stroke();
      }
    }
  }

  drawNeuralOperator() {
    // Visualize neural operator concept with flowing particles
    const particleCount = 150;
    const particles = [];

    for (let i = 0; i < particleCount; i++) {
      const progress = (i / particleCount + this.time * 0.1) % 1;
      const x = progress * this.width;
      const y = this.height / 2 + Math.sin(progress * Math.PI * 4 + this.time) * 80;

      particles.push({ x, y, progress });
    }

    // Draw flow lines
    this.ctx.strokeStyle = this.options.colors.primary + '20';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    particles.forEach((p, i) => {
      if (i === 0) {
        this.ctx.moveTo(p.x, p.y);
      } else {
        this.ctx.lineTo(p.x, p.y);
      }
    });
    this.ctx.stroke();

    // Draw particles
    particles.forEach(p => {
      const size = 2 + Math.sin(p.progress * Math.PI) * 2;
      const gradient = this.ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, size);
      gradient.addColorStop(0, this.options.colors.primary);
      gradient.addColorStop(1, this.options.colors.secondary + '00');

      this.ctx.fillStyle = gradient;
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
      this.ctx.fill();
    });
  }
}

// Gallery Manager
class ComputationalArtGallery {
  constructor() {
    this.artworks = new Map();
    this.init();
  }

  init() {
    // Find all art canvases
    const canvases = document.querySelectorAll('.computational-art-canvas');

    canvases.forEach(canvas => {
      const type = canvas.dataset.artType || 'network';
      const animated = canvas.dataset.animated !== 'false';

      const art = new ComputationalArt(canvas.id, {
        type,
        animated
      });

      this.artworks.set(canvas.id, art);
      art.start();
    });

    // Handle visibility changes to pause/resume animations
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        this.artworks.forEach(art => art.stop());
      } else {
        this.artworks.forEach(art => art.start());
      }
    });

    // Handle theme changes
    const observer = new MutationObserver(() => {
      this.artworks.forEach(art => {
        art.options.colors = art.getDefaultColors();
      });
    });

    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['data-md-color-scheme']
    });
  }

  add(canvasId, options) {
    if (this.artworks.has(canvasId)) {
      this.artworks.get(canvasId).stop();
    }

    const art = new ComputationalArt(canvasId, options);
    this.artworks.set(canvasId, art);
    art.start();
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new ComputationalArtGallery());
} else {
  new ComputationalArtGallery();
}
