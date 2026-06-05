/**
 * WebGL Background Effect - Geometric Mesh
 * Flowing and morphing 3D shapes using Three.js
 */

class WebGLBackground {
  constructor() {
    this.container = null;
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.mesh = null;
    this.time = 0;
    this.mouseX = 0;
    this.mouseY = 0;
    this.targetX = 0;
    this.targetY = 0;

    // Check if we're on the homepage
    if (this.isHomePage() && this.hasWebGLSupport()) {
      this.init();
    }
  }

  isHomePage() {
    // Check if we're on the root/index page only
    const path = window.location.pathname;
    // Homepage is exactly / or /index.html (no subdirectories)
    return path === '/' || path === '/index.html';
  }

  hasWebGLSupport() {
    try {
      const canvas = document.createElement('canvas');
      return !!(window.WebGLRenderingContext &&
        (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
    } catch(e) {
      return false;
    }
  }

  init() {
    this.createContainer();
    this.setupScene();
    this.createMesh();
    this.setupEventListeners();
    this.animate();
  }

  createContainer() {
    this.container = document.createElement('div');
    this.container.id = 'webgl-background';
    this.container.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: -1;
      pointer-events: none;
      opacity: 0.3;
    `;
    document.body.insertBefore(this.container, document.body.firstChild);
  }

  setupScene() {
    // Scene
    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.Fog(0x000000, 1, 1000);

    // Camera
    this.camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    this.camera.position.z = 30;

    // Renderer
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true
    });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setClearColor(0x000000, 0);
    this.container.appendChild(this.renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    this.scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0x667eea, 1);
    directionalLight.position.set(10, 10, 10);
    this.scene.add(directionalLight);

    const directionalLight2 = new THREE.DirectionalLight(0x764ba2, 0.5);
    directionalLight2.position.set(-10, -10, -10);
    this.scene.add(directionalLight2);
  }

  createMesh() {
    // Create a complex geometry
    const geometry = new THREE.IcosahedronGeometry(15, 4);

    // Custom shader material for flowing effect
    const material = new THREE.MeshPhongMaterial({
      color: 0x667eea,
      emissive: 0x112244,
      specular: 0x764ba2,
      shininess: 100,
      wireframe: false,
      transparent: true,
      opacity: 0.8
    });

    this.mesh = new THREE.Mesh(geometry, material);
    this.scene.add(this.mesh);

    // Store original positions for morphing
    const positions = geometry.attributes.position;
    this.originalPositions = [];
    for (let i = 0; i < positions.count; i++) {
      this.originalPositions.push(
        positions.getX(i),
        positions.getY(i),
        positions.getZ(i)
      );
    }
  }

  setupEventListeners() {
    // Mouse move
    document.addEventListener('mousemove', (e) => {
      this.mouseX = (e.clientX / window.innerWidth) * 2 - 1;
      this.mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
    });

    // Resize
    window.addEventListener('resize', () => {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // Pause when tab is hidden
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && this.animationId) {
        cancelAnimationFrame(this.animationId);
        this.animationId = null;
      } else if (!document.hidden && !this.animationId) {
        this.animate();
      }
    });
  }

  animate() {
    this.animationId = requestAnimationFrame(() => this.animate());

    this.time += 0.005;

    // Smooth mouse following
    this.targetX += (this.mouseX - this.targetX) * 0.05;
    this.targetY += (this.mouseY - this.targetY) * 0.05;

    // Rotate mesh
    this.mesh.rotation.x = this.time * 0.3 + this.targetY * 0.5;
    this.mesh.rotation.y = this.time * 0.5 + this.targetX * 0.5;
    this.mesh.rotation.z = this.time * 0.2;

    // Morph vertices
    const positions = this.mesh.geometry.attributes.position;
    for (let i = 0; i < positions.count; i++) {
      const i3 = i * 3;
      const x = this.originalPositions[i3];
      const y = this.originalPositions[i3 + 1];
      const z = this.originalPositions[i3 + 2];

      // Apply sine wave distortion
      const distortion = Math.sin(this.time + x * 0.1) *
                        Math.cos(this.time + y * 0.1) *
                        Math.sin(this.time + z * 0.1);

      positions.setXYZ(
        i,
        x + distortion * 0.5,
        y + distortion * 0.5,
        z + distortion * 0.5
      );
    }
    positions.needsUpdate = true;
    this.mesh.geometry.computeVertexNormals();

    // Render
    this.renderer.render(this.scene, this.camera);
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new WebGLBackground();
  });
} else {
  new WebGLBackground();
}
