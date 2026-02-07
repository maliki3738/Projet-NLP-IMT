(() => {
  if (document.getElementById('imt-bg-canvas')) return;

  const canvas = document.createElement('canvas');
  canvas.id = 'imt-bg-canvas';
  Object.assign(canvas.style, {
    position: 'fixed',
    inset: '0',
    zIndex: '0',
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
    opacity: '0.95'
  });
  document.body.appendChild(canvas);

  const halo = document.createElement('div');
  halo.id = 'imt-cursor-halo';
  document.body.appendChild(halo);

  const brain = document.createElement('div');
  brain.id = 'imt-holo-brain';
  brain.innerHTML = `
    <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <defs>
        <radialGradient id="brainGlow" cx="50%" cy="40%" r="60%">
          <stop offset="0%" stop-color="#6efbff" stop-opacity="0.85" />
          <stop offset="55%" stop-color="#23a7ff" stop-opacity="0.35" />
          <stop offset="100%" stop-color="#0b1020" stop-opacity="0" />
        </radialGradient>
        <linearGradient id="brainLine" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#4de9ff" stop-opacity="0.9" />
          <stop offset="100%" stop-color="#3b6cff" stop-opacity="0.7" />
        </linearGradient>
      </defs>
      <circle cx="256" cy="256" r="200" fill="url(#brainGlow)" />
      <g fill="none" stroke="url(#brainLine)" stroke-width="2.5" stroke-linecap="round">
        <path d="M166 210c-28 10-42 34-38 62 6 40 44 58 76 52" />
        <path d="M346 210c28 10 42 34 38 62-6 40-44 58-76 52" />
        <path d="M196 168c-16 16-24 36-22 58 2 22 12 38 28 52" />
        <path d="M316 168c16 16 24 36 22 58-2 22-12 38-28 52" />
        <path d="M224 132c-24 10-40 30-40 56" />
        <path d="M288 132c24 10 40 30 40 56" />
        <path d="M208 268c-8 22-2 44 16 58" />
        <path d="M304 268c8 22 2 44-16 58" />
        <path d="M256 110v292" />
      </g>
    </svg>
  `;
  document.body.appendChild(brain);

  const radar = document.createElement('div');
  radar.id = 'imt-radar-scan';
  document.body.appendChild(radar);

  const ctx = canvas.getContext('2d');
  let w = 0;
  let h = 0;
  let dpr = Math.max(1, window.devicePixelRatio || 1);

  const nodes = [];
  const links = [];
  const pulses = [];
  const sparks = [];

  const CONFIG = {
    grid: 76,
    nodeJitter: 22,
    linkChance: 0.22,
    maxLinksPerNode: 3,
    pulseCount: 100,
    pulseSpeed: 0.28,
  };

  let audioLevel = 0.12;
  let audioTarget = 0.12;
  let audioReady = false;

  function resize() {
    dpr = Math.max(1, window.devicePixelRatio || 1);
    w = Math.floor(window.innerWidth);
    h = Math.floor(window.innerHeight);
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    buildGraph();
  }

  function rand(min, max) {
    return min + Math.random() * (max - min);
  }

  function buildGraph() {
    nodes.length = 0;
    links.length = 0;

    const cols = Math.ceil(w / CONFIG.grid);
    const rows = Math.ceil(h / CONFIG.grid);

    for (let y = 0; y <= rows; y++) {
      for (let x = 0; x <= cols; x++) {
        const nx = x * CONFIG.grid + rand(-CONFIG.nodeJitter, CONFIG.nodeJitter);
        const ny = y * CONFIG.grid + rand(-CONFIG.nodeJitter, CONFIG.nodeJitter);
        nodes.push({ x: nx, y: ny, links: 0 });
      }
    }

    for (let i = 0; i < nodes.length; i++) {
      const a = nodes[i];
      if (a.links >= CONFIG.maxLinksPerNode) continue;
      for (let j = i + 1; j < nodes.length; j++) {
        const b = nodes[j];
        if (b.links >= CONFIG.maxLinksPerNode) continue;
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const dist = Math.hypot(dx, dy);
        if (dist < CONFIG.grid * 1.2 && Math.random() < CONFIG.linkChance) {
          links.push({ a, b });
          a.links++;
          b.links++;
          if (a.links >= CONFIG.maxLinksPerNode) break;
        }
      }
    }

    pulses.length = 0;
    for (let i = 0; i < CONFIG.pulseCount; i++) {
      const link = links[Math.floor(Math.random() * links.length)];
      if (!link) break;
      pulses.push({
        link,
        t: Math.random(),
        speed: CONFIG.pulseSpeed * rand(0.6, 1.4),
        size: rand(1.4, 3.8)
      });
    }
  }

  function drawBackground() {
    ctx.clearRect(0, 0, w, h);

    const boost = Math.max(0.1, Math.min(audioLevel, 0.9));
    const grd = ctx.createRadialGradient(w * 0.5, h * 0.2, 10, w * 0.5, h * 0.2, Math.max(w, h));
    grd.addColorStop(0, `rgba(0, 210, 255, ${0.1 + boost * 0.3})`);
    grd.addColorStop(0.45, 'rgba(0, 90, 150, 0.12)');
    grd.addColorStop(1, 'rgba(0, 0, 0, 0.82)');
    ctx.fillStyle = grd;
    ctx.fillRect(0, 0, w, h);
  }

  function drawLinks() {
    ctx.save();
    ctx.globalAlpha = 0.6 + audioLevel * 0.3;
    ctx.lineWidth = 1;
    ctx.strokeStyle = 'rgba(60, 210, 255, 0.3)';
    links.forEach(({ a, b }) => {
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
    });
    ctx.restore();
  }

  function drawNodes() {
    ctx.save();
    ctx.fillStyle = 'rgba(120, 230, 255, 0.65)';
    nodes.forEach(n => {
      ctx.fillRect(n.x - 1, n.y - 1, 2, 2);
    });
    ctx.restore();
  }

  function drawPulses() {
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    pulses.forEach(p => {
      p.t += p.speed * (0.0035 + audioLevel * 0.004);
      if (p.t > 1) p.t = 0;
      const { a, b } = p.link;
      const x = a.x + (b.x - a.x) * p.t;
      const y = a.y + (b.y - a.y) * p.t;
      const glow = ctx.createRadialGradient(x, y, 0, x, y, 18 + audioLevel * 14);
      glow.addColorStop(0, 'rgba(0, 255, 240, 0.95)');
      glow.addColorStop(1, 'rgba(0, 255, 240, 0)');
      ctx.fillStyle = glow;
      ctx.fillRect(x - 22, y - 22, 44, 44);
      ctx.fillStyle = 'rgba(190, 255, 255, 0.95)';
      ctx.beginPath();
      ctx.arc(x, y, p.size + audioLevel * 2.2, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.restore();
  }

  function drawSparks() {
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    for (let i = sparks.length - 1; i >= 0; i--) {
      const s = sparks[i];
      s.life -= 1;
      s.r += 1.2 + audioLevel * 1.8;
      if (s.life <= 0) {
        sparks.splice(i, 1);
        continue;
      }
      const glow = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r);
      glow.addColorStop(0, `rgba(0, 255, 240, ${0.45 * s.life / s.max})`);
      glow.addColorStop(1, 'rgba(0, 255, 240, 0)');
      ctx.fillStyle = glow;
      ctx.fillRect(s.x - s.r, s.y - s.r, s.r * 2, s.r * 2);
    }
    ctx.restore();
  }

  function render() {
    drawBackground();
    drawLinks();
    drawNodes();
    drawPulses();
    drawSparks();
    audioLevel += (audioTarget - audioLevel) * 0.08;
    document.body.style.setProperty('--audio-level', audioLevel.toFixed(3));
    requestAnimationFrame(render);
  }

  let haloX = 0;
  let haloY = 0;
  let targetX = window.innerWidth * 0.5;
  let targetY = window.innerHeight * 0.5;

  function animateHalo() {
    haloX += (targetX - haloX) * 0.08;
    haloY += (targetY - haloY) * 0.08;
    halo.style.transform = `translate(${haloX}px, ${haloY}px)`;
    requestAnimationFrame(animateHalo);
  }

  function pulseOnMessage() {
    const link = links[Math.floor(Math.random() * links.length)];
    if (link) {
      const { a, b } = link;
      sparks.push({
        x: (a.x + b.x) * 0.5,
        y: (a.y + b.y) * 0.5,
        r: 20,
        life: 30,
        max: 30
      });
    }
    brain.classList.remove('imt-brain-pulse');
    void brain.offsetWidth;
    brain.classList.add('imt-brain-pulse');
    radar.classList.remove('imt-radar-pulse');
    void radar.offsetWidth;
    radar.classList.add('imt-radar-pulse');
  }

  function setTypingState(isTyping) {
    document.body.classList.toggle('imt-typing', isTyping);
  }

  function findSidebar() {
    return document.querySelector('[data-testid*="sidebar" i], aside, nav, .sidebar, [class*="sidebar" i]');
  }

  function findHistoryAnchor(sidebar) {
    if (!sidebar) return null;
    return (
      sidebar.querySelector('[data-testid*="thread-history" i]') ||
      sidebar.querySelector('[data-testid*="history" i]') ||
      sidebar.querySelector('ul')
    );
  }

  function ensureHistoryPlaceholder() {
    const sidebar = findSidebar();
    if (!sidebar) return false;

    let placeholder = document.getElementById('imt-history-placeholder');
    if (!placeholder) {
      placeholder = document.createElement('div');
      placeholder.id = 'imt-history-placeholder';
      placeholder.className = 'imt-history-placeholder';
      placeholder.innerHTML = ``;
      const header = sidebar.querySelector('header');
      const target = findHistoryAnchor(sidebar);
      if (header && header.parentElement === sidebar) {
        header.insertAdjacentElement('afterend', placeholder);
      } else if (target && target.parentElement) {
        target.parentElement.insertBefore(placeholder, target);
      } else {
        sidebar.prepend(placeholder);
      }
    }

    // Ajouter les boutons GitHub et Langfuse
    const newChatButton = sidebar.querySelector('button[data-testid*="new" i], button[aria-label*="new" i], header button');
    
    if (newChatButton && !document.getElementById('imt-github-button')) {
      // Copier les classes du bouton Nouvelle discussion
      const buttonClasses = newChatButton.className;
      
      // Bouton GitHub
      const githubBtn = document.createElement('button');
      githubBtn.id = 'imt-github-button';
      githubBtn.className = buttonClasses;
      githubBtn.innerHTML = `
        <img src="/public/github.png" alt="GitHub" style="width: 20px; height: 20px; filter: brightness(0) invert(1);" />
        <span>GitHub</span>
      `;
      githubBtn.onclick = () => window.open('https://github.com/maliki3738/Projet-NLP-IMT', '_blank');
      
      // Bouton Langfuse
      const langfuseBtn = document.createElement('button');
      langfuseBtn.id = 'imt-langfuse-button';
      langfuseBtn.className = buttonClasses;
      langfuseBtn.innerHTML = `
        <img src="/public/langfuse.png" alt="Langfuse" style="width: 20px; height: 20px; filter: brightness(0) invert(1);" />
        <span>Langfuse</span>
      `;
      langfuseBtn.onclick = () => window.open('https://cloud.langfuse.com/project/cml9pn5ld0014ad08qdq7m2gz', '_blank');
      
      // Insérer les boutons juste après le bouton Nouvelle discussion
      newChatButton.insertAdjacentElement('afterend', githubBtn);
      githubBtn.insertAdjacentElement('afterend', langfuseBtn);
    }

    const hasItems = Boolean(
      sidebar.querySelector('[data-testid*="history" i] li, [data-testid*="sidebar" i] li')
    );
    placeholder.style.display = hasItems ? 'none' : 'block';
    return true;
  }

  const observer = new MutationObserver((mutations) => {
    let sawMessage = false;
    let typing = false;
    for (const m of mutations) {
      if (m.addedNodes && m.addedNodes.length) {
        sawMessage = true;
        m.addedNodes.forEach(node => {
          if (!(node instanceof HTMLElement)) return;
          if (node.matches('[data-testid*="typing" i], .typing, .cl-typing, .loader, [aria-live="polite"]')) {
            typing = true;
          }
          if (node.querySelector && node.querySelector('[data-testid*="typing" i], .typing, .cl-typing, .loader')) {
            typing = true;
          }
        });
      }
    }
    if (sawMessage) pulseOnMessage();
    if (typing) setTypingState(true);
    ensureHistoryPlaceholder();
  });

  const typingWatcher = setInterval(() => {
    const typingEl = document.querySelector('[data-testid*="typing" i], .typing, .cl-typing, .loader');
    setTypingState(Boolean(typingEl));
  }, 800);

  function startObserver() {
    const root = document.querySelector('#root');
    if (root) {
      observer.observe(root, { childList: true, subtree: true });
    }
  }

  // Animation visuelle uniquement (pas de micro requis)
  function setupAudio() {
    if (audioReady) return;
    audioReady = true;
    // Animation par pulsation idle
    let t = 0;
    const idle = () => {
      t += 0.03;
      audioTarget = 0.12 + Math.sin(t) * 0.05;
      requestAnimationFrame(idle);
    };
    idle();
  }

  function onFirstGesture() {
    setupAudio();
    window.removeEventListener('click', onFirstGesture);
    window.removeEventListener('keydown', onFirstGesture);
  }

  window.addEventListener('mousemove', (e) => {
    targetX = e.clientX;
    targetY = e.clientY;
  }, { passive: true });

  window.addEventListener('resize', resize, { passive: true });
  window.addEventListener('click', onFirstGesture, { once: true });
  window.addEventListener('keydown', onFirstGesture, { once: true });

  resize();
  render();
  animateHalo();
  startObserver();
  ensureHistoryPlaceholder();

  let placeholderAttempts = 0;
  const placeholderBoot = setInterval(() => {
    placeholderAttempts += 1;
    if (ensureHistoryPlaceholder() || placeholderAttempts > 30) {
      clearInterval(placeholderBoot);
    }
  }, 800);
})();
