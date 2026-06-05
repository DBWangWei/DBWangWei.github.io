/**
 * Research Conversation Agent
 * An AI chatbot that can answer questions about Prof. Wang's research
 */

class ResearchChatAgent {
  constructor() {
    this.isOpen = false;
    this.messageHistory = [];
    this.publications = null;
    this.init();
  }

  async init() {
    // Load publication data
    await this.loadPublications();

    // Create chat UI
    this.createChatUI();

    // Add event listeners
    this.attachEventListeners();
  }

  async loadPublications() {
    try {
      const response = await fetch('/data-publications/publications.cache.json');
      const data = await response.json();
      this.publications = data.records;
    } catch (error) {
      console.error('Failed to load publications:', error);
      this.publications = [];
    }
  }

  createChatUI() {
    const chatHTML = `
      <div id="research-chat-container" class="research-chat-container">
        <button id="chat-toggle-btn" class="chat-toggle-btn" aria-label="Open research chat">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            <path d="M9 10h6M9 14h3"/>
          </svg>
        </button>

        <div id="chat-window" class="chat-window">
          <div class="chat-header">
            <h3>Research Assistant</h3>
            <p class="chat-subtitle">Ask me about Prof. Wang's research</p>
            <button id="chat-close-btn" class="chat-close-btn" aria-label="Close chat">×</button>
          </div>

          <div id="chat-messages" class="chat-messages">
            <div class="chat-message bot-message">
              <div class="message-content">
                <p>👋 Hi! I can help you explore Prof. Wang's research. Try asking:</p>
                <ul class="suggestion-list">
                  <li>"What work has been done on vector databases?"</li>
                  <li>"Show me papers about LLMs"</li>
                  <li>"What's the AI4S research about?"</li>
                  <li>"Papers on neural operators and PDEs"</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="chat-input-container">
            <textarea
              id="chat-input"
              class="chat-input"
              placeholder="Ask about research areas, papers, or topics..."
              rows="1"
            ></textarea>
            <button id="chat-send-btn" class="chat-send-btn" aria-label="Send message">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', chatHTML);
  }

  attachEventListeners() {
    const toggleBtn = document.getElementById('chat-toggle-btn');
    const closeBtn = document.getElementById('chat-close-btn');
    const sendBtn = document.getElementById('chat-send-btn');
    const input = document.getElementById('chat-input');

    toggleBtn?.addEventListener('click', () => this.toggleChat());
    closeBtn?.addEventListener('click', () => this.toggleChat());
    sendBtn?.addEventListener('click', () => this.sendMessage());

    input?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Auto-resize textarea
    input?.addEventListener('input', (e) => {
      e.target.style.height = 'auto';
      e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
    });
  }

  toggleChat() {
    const chatWindow = document.getElementById('chat-window');
    const toggleBtn = document.getElementById('chat-toggle-btn');

    this.isOpen = !this.isOpen;

    if (this.isOpen) {
      chatWindow.classList.add('open');
      toggleBtn.classList.add('hidden');
      document.getElementById('chat-input')?.focus();
    } else {
      chatWindow.classList.remove('open');
      toggleBtn.classList.remove('hidden');
    }
  }

  async sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    this.addMessage(message, 'user');
    input.value = '';
    input.style.height = 'auto';

    // Show typing indicator
    this.showTypingIndicator();

    // Process message and get response
    const response = await this.processMessage(message);

    // Remove typing indicator and show response
    this.removeTypingIndicator();
    this.addMessage(response, 'bot');
  }

  addMessage(content, sender) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = content;

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    this.messageHistory.push({ role: sender, content });
  }

  showTypingIndicator() {
    const messagesContainer = document.getElementById('chat-messages');
    const indicator = document.createElement('div');
    indicator.className = 'chat-message bot-message typing-indicator';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = '<div class="message-content"><span></span><span></span><span></span></div>';
    messagesContainer.appendChild(indicator);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  removeTypingIndicator() {
    document.getElementById('typing-indicator')?.remove();
  }

  async processMessage(message) {
    const lowerMessage = message.toLowerCase();

    // Search for relevant papers
    const relevantPapers = this.searchPapers(lowerMessage);

    // Identify intent
    if (this.matchesIntent(lowerMessage, ['vector database', 'vector db', 'ann', 'similarity search', 'nearest neighbor'])) {
      return this.generateResponse('vector_database', relevantPapers);
    }

    if (this.matchesIntent(lowerMessage, ['llm', 'large language model', 'language model', 'alignment', 'distillation'])) {
      return this.generateResponse('llm', relevantPapers);
    }

    if (this.matchesIntent(lowerMessage, ['ai4s', 'ai for science', 'pde', 'neural operator', 'physics'])) {
      return this.generateResponse('ai4s', relevantPapers);
    }

    if (this.matchesIntent(lowerMessage, ['database', 'db', 'query', 'index'])) {
      return this.generateResponse('database', relevantPapers);
    }

    if (this.matchesIntent(lowerMessage, ['graph', 'network'])) {
      return this.generateResponse('graph', relevantPapers);
    }

    if (this.matchesIntent(lowerMessage, ['recent', 'latest', '2026', '2025'])) {
      return this.generateResponse('recent', relevantPapers);
    }

    if (this.matchesIntent(lowerMessage, ['award', 'best paper', 'distinguished'])) {
      return this.generateResponse('awards', relevantPapers);
    }

    // Default: show relevant papers or general info
    if (relevantPapers.length > 0) {
      return this.generateResponse('general', relevantPapers);
    }

    return this.generateResponse('unknown', []);
  }

  matchesIntent(message, keywords) {
    return keywords.some(keyword => message.includes(keyword));
  }

  searchPapers(query) {
    if (!this.publications) return [];

    const terms = query.toLowerCase().split(' ').filter(t => t.length > 3);

    return this.publications
      .map(paper => {
        let score = 0;
        const searchText = `${paper.title} ${paper.areas?.join(' ')} ${paper.venue} ${paper.tags?.join(' ')}`.toLowerCase();

        terms.forEach(term => {
          if (searchText.includes(term)) {
            score += searchText.split(term).length - 1;
          }
        });

        return { paper, score };
      })
      .filter(item => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 5)
      .map(item => item.paper);
  }

  generateResponse(topic, papers) {
    const responses = {
      vector_database: {
        intro: "Prof. Wang's work on vector databases focuses on efficient similarity search in high-dimensional spaces. Key areas include:",
        context: "<ul><li><strong>ANN Search</strong>: Developing efficient approximate nearest neighbor algorithms</li><li><strong>Learned Indexes</strong>: Integrating ML into index structures</li><li><strong>LSH-based Methods</strong>: Locality-sensitive hashing for scalable search</li></ul>"
      },
      llm: {
        intro: "Research on Large Language Models includes:",
        context: "<ul><li><strong>Model Distillation</strong>: Creating smaller, efficient LLMs</li><li><strong>Alignment</strong>: BMC and natural evolution approaches</li><li><strong>Memory Mechanisms</strong>: Learning to edit and update knowledge</li><li><strong>Deep Inference</strong>: Domain-specific reasoning strategies</li></ul>"
      },
      ai4s: {
        intro: "AI for Science research applies deep learning to scientific computing:",
        context: "<ul><li><strong>Neural Operators</strong>: Learning PDE solutions on arbitrary geometries</li><li><strong>Multi-graph Methods</strong>: Combining algebraic multigrid with neural networks</li><li><strong>Material Informatics</strong>: Property prediction and material design</li></ul>"
      },
      database: {
        intro: "Database research spans traditional and AI-enhanced systems:",
        context: "<ul><li><strong>Learned Indexes</strong>: ML-powered data structures</li><li><strong>Query Processing</strong>: Similarity search and keyword queries</li><li><strong>High-dimensional Data</strong>: Efficient storage and retrieval</li></ul>"
      },
      graph: {
        intro: "Graph research includes network analysis and graph databases:",
        context: ""
      },
      recent: {
        intro: "Recent publications (2025-2026) cover cutting-edge topics:",
        context: ""
      },
      awards: {
        intro: "Prof. Wang's research has received multiple prestigious awards:",
        context: "<ul><li>SIGSPATIAL Best Vision Paper</li><li>ICASSP 2023 Top 3% Paper</li><li>SIGCOMM 2022 Best Paper</li><li>ICMR 2021 Best Paper</li><li>DASFAA 2016 Best Student Paper</li></ul>"
      },
      general: {
        intro: "Here's what I found related to your question:",
        context: ""
      },
      unknown: {
        intro: "I can help you explore Prof. Wang's research in several areas:",
        context: "<ul><li><strong>Vector Databases & ANN</strong>: Similarity search and indexing</li><li><strong>Large Language Models</strong>: Alignment, distillation, and inference</li><li><strong>AI for Science</strong>: Neural operators and PDEs</li><li><strong>Database Systems</strong>: Query processing and learned indexes</li></ul><p>Try asking about specific topics like \"vector databases\" or \"neural operators\"!</p>"
      }
    };

    const template = responses[topic] || responses.unknown;
    let html = `<p>${template.intro}</p>${template.context}`;

    // Add relevant papers
    if (papers.length > 0) {
      html += '<div class="paper-results">';
      html += '<p><strong>Relevant Papers:</strong></p>';
      papers.forEach(paper => {
        const tags = paper.tags?.map(tag => `<span class="paper-tag">${tag}</span>`).join('') || '';
        const award = paper.award ? ` 🏆 <em>${paper.award}</em>` : '';
        html += `
          <div class="paper-item">
            <div class="paper-title">${paper.title}</div>
            <div class="paper-meta">${paper.venue}, ${paper.year}${award}</div>
            <div class="paper-tags">${tags}</div>
          </div>
        `;
      });
      html += '</div>';
    }

    return html;
  }
}

// Initialize chat agent when DOM is loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new ResearchChatAgent());
} else {
  new ResearchChatAgent();
}
