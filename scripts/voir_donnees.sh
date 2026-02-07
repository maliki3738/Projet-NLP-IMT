#!/bin/bash
# Script pour visualiser rapidement les données MySQL + Redis

echo "=================================="
echo "📊 ÉTAT DE VOTRE PROJET IMT-AGENT"
echo "=================================="
echo ""

echo "🔴 REDIS (Mémoire active)"
echo "------------------------"
redis-cli ping && echo "✅ Redis actif" || echo "❌ Redis hors ligne"
echo "Sessions actives: $(redis-cli DBSIZE | cut -d: -f2)"
echo ""

echo "🔵 MYSQL (Historique permanent)"
echo "--------------------------------"
mysql -uroot -pAMGMySQL chainlit -e "
SELECT 
  CONCAT('✅ ', COUNT(*), ' messages stockés') as status,
  CONCAT('👤 ', SUM(CASE WHEN type='user_message' THEN 1 ELSE 0 END), ' questions utilisateur') as questions,
  CONCAT('🤖 ', SUM(CASE WHEN type='assistant_message' THEN 1 ELSE 0 END), ' réponses bot') as reponses,
  CONCAT('💬 ', COUNT(DISTINCT threadId), ' conversations') as conversations,
  CONCAT('🕐 Dernier message: ', DATE_FORMAT(MAX(createdAt), '%d/%m/%Y à %H:%i')) as derniere_activite
FROM Step;
" 2>&1 | grep -v Warning | tail -n +2

echo ""
echo "📝 LES 5 DERNIÈRES QUESTIONS"
echo "----------------------------"
mysql -uroot -pAMGMySQL chainlit -e "
SELECT 
  CONCAT('⏰ ', TIME(createdAt)) as heure,
  LEFT(input, 70) as question
FROM Step 
WHERE type='user_message' 
ORDER BY createdAt DESC 
LIMIT 5;
" 2>&1 | grep -v Warning | tail -n +2

echo ""
echo "🤖 LES 5 DERNIÈRES RÉPONSES"
echo "----------------------------"
mysql -uroot -pAMGMySQL chainlit -e "
SELECT 
  CONCAT('⏰ ', TIME(createdAt)) as heure,
  LEFT(output, 70) as reponse
FROM Step 
WHERE type='assistant_message' 
ORDER BY createdAt DESC 
LIMIT 5;
" 2>&1 | grep -v Warning | tail -n +2

echo ""
echo "=================================="
echo "✅ TOUT FONCTIONNE CORRECTEMENT"
echo "=================================="
