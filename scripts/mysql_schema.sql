/* =========================================================
   CRÉATION DE LA BASE DE DONNÉES
   ========================================================= */

/* Crée la base de données si elle n'existe pas encore */
CREATE DATABASE IF NOT EXISTS chainlit_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

/* Sélection de la base de données */
USE chainlit_db;


/* =========================================================
   TABLE : User
   Stocke les utilisateurs du chatbot
   ========================================================= */
CREATE TABLE IF NOT EXISTS User (
  /* Identifiant unique (UUID) */
  id CHAR(36) PRIMARY KEY,

  /* Identifiant externe (email, username, etc.) */
  identifier VARCHAR(255) UNIQUE NOT NULL,

  /* Informations supplémentaires (JSON) */
  metadata JSON NULL,

  /* Date de création */
  createdAt DATETIME NOT NULL,

  /* Date de dernière mise à jour */
  updatedAt DATETIME NOT NULL
);


/* =========================================================
   TABLE : Thread
   Représente une conversation complète
   ========================================================= */
CREATE TABLE IF NOT EXISTS Thread (
  /* Identifiant unique du thread */
  id CHAR(36) PRIMARY KEY,

  /* Nom optionnel de la conversation */
  name VARCHAR(255) NULL,

  /* Référence vers l'utilisateur */
  userId CHAR(36) NULL,

  /* Identifiant utilisateur redondant (fallback) */
  userIdentifier VARCHAR(255) NULL,

  /* Tags de classification (JSON) */
  tags JSON NULL,

  /* Métadonnées libres */
  metadata JSON NULL,

  /* Date de création */
  createdAt DATETIME NOT NULL,

  /* Date de dernière mise à jour */
  updatedAt DATETIME NOT NULL
);


/* =========================================================
   TABLE : Step
   Stocke chaque message, réponse IA ou action
   ========================================================= */
CREATE TABLE IF NOT EXISTS Step (
  /* Identifiant unique du step */
  id CHAR(36) PRIMARY KEY,

  /* Référence vers le thread */
  threadId CHAR(36) NOT NULL,

  /* Référence vers le step parent (chaînage) */
  parentId CHAR(36) NULL,

  /* Nom optionnel */
  name VARCHAR(255) NULL,

  /* Type du step (user_message, assistant_message, tool_call, etc.) */
  type VARCHAR(50) NOT NULL,

  /* Entrée utilisateur */
  input MEDIUMTEXT NULL,

  /* Sortie de l'IA */
  output MEDIUMTEXT NULL,

  /* Métadonnées du step */
  metadata JSON NULL,

  /* Tags optionnels */
  tags JSON NULL,

  /* Date de création */
  createdAt DATETIME NOT NULL,

  /* Début d'exécution */
  startTime DATETIME NULL,

  /* Fin d'exécution */
  endTime DATETIME NULL,

  /* Indique si une erreur est survenue */
  isError BOOLEAN DEFAULT FALSE,

  /* Informations sur la génération LLM */
  generation JSON NULL,

  /* Feedback intégré */
  feedback JSON NULL,

  /* Index pour accélérer les recherches par thread */
  INDEX (threadId)
);


/* =========================================================
   TABLE : Element
   Stocke les fichiers, images et contenus générés
   ========================================================= */
CREATE TABLE IF NOT EXISTS Element (
  /* Identifiant unique */
  id CHAR(36) PRIMARY KEY,

  /* Référence vers le thread */
  threadId CHAR(36) NULL,

  /* Référence vers un step */
  forId CHAR(36) NULL,

  /* Nom de l'élément */
  name VARCHAR(255) NULL,

  /* Type de l'élément */
  type VARCHAR(50) NULL,

  /* URL distante */
  url TEXT NULL,

  /* Chemin local */
  path TEXT NULL,

  /* Contenu texte */
  content MEDIUMTEXT NULL,

  /* Type MIME */
  mime VARCHAR(100) NULL,

  /* Métadonnées */
  metadata JSON NULL,

  /* Date de création */
  createdAt DATETIME NOT NULL,

  /* Date de mise à jour */
  updatedAt DATETIME NOT NULL,

  /* Index pour recherches rapides */
  INDEX (threadId)
);


/* =========================================================
   TABLE : Feedback
   Stocke l'évaluation utilisateur des réponses IA
   ========================================================= */
CREATE TABLE IF NOT EXISTS Feedback (
  /* Identifiant unique */
  id CHAR(36) PRIMARY KEY,

  /* Référence vers le step évalué */
  stepId CHAR(36) NOT NULL,

  /* Nom du feedback (rating, like, etc.) */
  name VARCHAR(255) NOT NULL,

  /* Valeur numérique du feedback */
  value FLOAT NOT NULL,

  /* Commentaire optionnel */
  comment TEXT NULL,

  /* Date de création */
  createdAt DATETIME NOT NULL,

  /* Date de mise à jour */
  updatedAt DATETIME NOT NULL,

  /* Index pour jointures rapides */
  INDEX (stepId)
);

SELECT
  type,
  LEFT(COALESCE(input, output), 80) AS message,
  TIME(createdAt) AS heure
FROM Step
ORDER BY createdAt DESC
LIMIT 10;

select * from Step;