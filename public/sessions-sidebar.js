// Script pour afficher les sessions actives dans un sidebar personnalisé
window.addEventListener('DOMContentLoaded', function() {
  console.log('🚀 IMT Sessions Sidebar initializing...');
  
  // Créer le sidebar
  createSessionsSidebar();
  
  // Actualiser toutes les 30 secondes
  setInterval(updateSessionsSidebar, 30000);
});

function createSessionsSidebar() {
  // Vérifier si le sidebar existe déjà
  if (document.getElementById('imt-sessions-sidebar')) {
    return;
  }
  
  const sidebar = document.createElement('div');
  sidebar.id = 'imt-sessions-sidebar';
  sidebar.innerHTML = `
    <div class="imt-sidebar-header">
      <h3>💬 Discussions actives</h3>
      <span class="imt-session-count">0/3</span>
    </div>
    <div id="imt-sessions-list" class="imt-sessions-list">
      <p class="imt-loading">Chargement...</p>
    </div>
    <div class="imt-sidebar-footer">
      <small>TTL: 60min | Max: 3 sessions</small>
    </div>
  `;
  
  document.body.appendChild(sidebar);
  
  // Charger les sessions depuis le serveur
  updateSessionsSidebar();
}

async function updateSessionsSidebar() {
  const listContainer = document.getElementById('imt-sessions-list');
  if (!listContainer) return;
  
  try {
    // Récupérer les sessions depuis le backend (via websocket ou API)
    // Pour l'instant, simulation avec localStorage
    const sessions = getSessionsFromStorage();
    
    if (sessions.length === 0) {
      listContainer.innerHTML = '<p class="imt-empty">Aucune autre session</p>';
      updateSessionCount(0);
      return;
    }
    
    // Afficher les sessions (max 2 autres + 1 actuelle)
    const currentSessionId = getCurrentSessionId();
    const otherSessions = sessions.filter(s => s.id !== currentSessionId).slice(0, 2);
    
    listContainer.innerHTML = otherSessions.map((session, i) => `
      <div class="imt-session-item" data-session-id="${session.id}">
        <div class="imt-session-header">
          <span class="imt-session-label">Session ${i + 1}</span>
          <span class="imt-session-id">${session.id.substring(0, 8)}...</span>
        </div>
        <div class="imt-session-stats">
          <span class="imt-stat">💬 ${session.messageCount} msg</span>
          <span class="imt-stat">⏱️ ${session.ttlMinutes}min</span>
        </div>
        <button class="imt-session-switch" onclick="switchToSession('${session.id}')">
          Reprendre
        </button>
      </div>
    `).join('');
    
    updateSessionCount(sessions.length);
    
  } catch (error) {
    console.error('Erreur lors de la récupération des sessions:', error);
    listContainer.innerHTML = '<p class="imt-error">Erreur de chargement</p>';
  }
}

function getSessionsFromStorage() {
  // Simulation - à remplacer par un appel API réel
  const stored = localStorage.getItem('imt_sessions');
  if (!stored) return [];
  
  try {
    return JSON.parse(stored);
  } catch {
    return [];
  }
}

function getCurrentSessionId() {
  // Récupérer l'ID de session actuel depuis l'URL ou le sessionStorage
  return sessionStorage.getItem('current_session_id') || 'current';
}

function updateSessionCount(count) {
  const counter = document.querySelector('.imt-session-count');
  if (counter) {
    counter.textContent = `${count}/3`;
  }
}

function switchToSession(sessionId) {
  console.log('Basculer vers session:', sessionId);
  // TODO: Implémenter la logique de bascule via Chainlit
  alert(`Fonction de bascule vers session ${sessionId} à implémenter`);
}

// Exposer les fonctions globalement
window.updateSessionsSidebar = updateSessionsSidebar;
window.switchToSession = switchToSession;

console.log('✅ IMT Sessions Sidebar initialized');
