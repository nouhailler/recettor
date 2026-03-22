from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTabWidget, QTextBrowser, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


# ── Styles HTML communs ───────────────────────────────────────────────────────

_CSS = """
<style>
  body  { font-family: Arial, sans-serif; font-size: 13px; color: #2C1810;
          line-height: 1.6; margin: 0; padding: 0; }
  h1    { font-size: 18px; color: #8B4513; border-bottom: 2px solid #D4A574;
          padding-bottom: 6px; margin-top: 4px; }
  h2    { font-size: 15px; color: #2C1810; background: #F0E8D8;
          border-left: 4px solid #D4A574; padding: 4px 10px;
          margin-top: 18px; margin-bottom: 6px; }
  h3    { font-size: 13px; color: #8B4513; margin-top: 14px; margin-bottom: 4px; }
  ul    { margin: 4px 0 8px 0; padding-left: 22px; }
  li    { margin-bottom: 3px; }
  p     { margin: 6px 0; }
  .tip  { background: #FFF9C4; border-left: 3px solid #F39C12;
          padding: 6px 10px; margin: 8px 0; border-radius: 4px; }
  .note { background: #D5E8D4; border-left: 3px solid #27AE60;
          padding: 6px 10px; margin: 8px 0; border-radius: 4px; }
  .warn { background: #FADBD8; border-left: 3px solid #E74C3C;
          padding: 6px 10px; margin: 8px 0; border-radius: 4px; }
  .calc { background: #EBF5FB; border-left: 3px solid #3498DB;
          padding: 6px 10px; margin: 8px 0; border-radius: 4px;
          font-family: monospace; font-size: 12px; }
  table { border-collapse: collapse; width: 100%; margin: 8px 0; }
  th    { background: #D4A574; color: #2C1810; padding: 5px 8px; text-align: left; }
  td    { border: 1px solid #E8D5C0; padding: 4px 8px; }
  tr:nth-child(even) td { background: #FAF6F0; }
  code  { background: #F0E8D8; padding: 1px 4px; border-radius: 3px;
          font-family: monospace; font-size: 12px; }
  hr    { border: none; border-top: 1px solid #D4A574; margin: 10px 0 8px 0; }
</style>
"""


def _page(body: str) -> str:
    return f"<html><head>{_CSS}</head><body>{body}</body></html>"


# ── Contenu de chaque onglet ──────────────────────────────────────────────────

OVERVIEW = _page("""
<h1>Bienvenue dans Recettor</h1>
<p>Recettor est une application de gestion de recettes de cuisine entièrement locale.
Toutes vos données sont stockées dans une base SQLite sur votre machine — aucune connexion internet requise.</p>

<h2>Navigation principale</h2>
<p>La barre latérale gauche donne accès à toutes les fonctionnalités :</p>
<table>
  <tr><th>Bouton</th><th>Rôle</th></tr>
  <tr><td><b>Rechercher</b></td><td>Chercher des recettes par nom, ingrédient, régime, difficulté, cuisine ou calories — inclut un filtre ★ Recettes favorites</td></tr>
  <tr><td><b>Saisonnalité</b></td><td>Parcourir les recettes et ingrédients de saison mois par mois</td></tr>
  <tr><td><b>Mon Frigo</b></td><td>Sélectionner les ingrédients disponibles, obtenir des suggestions classiques et des suggestions IA via Ollama</td></tr>
  <tr><td><b>🛒 Liste de courses</b></td><td>Gérer votre liste d'articles à acheter, avec ajout automatique depuis les suggestions IA</td></tr>
  <tr><td><b>Ajouter</b></td><td>Créer une nouvelle recette via un formulaire complet en 9 onglets</td></tr>
  <tr><td><b>Importer / Exporter</b></td><td>Échanger des recettes au format JSON</td></tr>
  <tr><td><b>★ Favoris</b></td><td>Gérer les ingrédients favoris et les recettes favorites (deux onglets)</td></tr>
</table>

<h2>Barre de statut</h2>
<p>En bas de la fenêtre, la barre de statut affiche en permanence :</p>
<ul>
  <li>La <b>date du jour</b> (jour, mois, année)</li>
  <li>La <b>saison en cours</b> (calculée automatiquement)</li>
  <li>Le <b>nombre total de recettes</b> dans la base</li>
  <li>Le nom et la version de l'application</li>
</ul>
<p>Ce compteur se met à jour automatiquement après chaque ajout ou suppression de recette.</p>

<h2>Menu Fichier</h2>
<ul>
  <li><b>Sauvegarder la base</b> — crée une copie de sauvegarde de la base de données SQLite
      dans le répertoire <code>backups/</code>, horodatée (format : <code>recettor_backup_YYYYMMDD_HHMMSS.db</code>).</li>
  <li><b>Quitter</b> — ferme l'application.</li>
</ul>

<h2>Menu Outils</h2>
<ul>
  <li><b>Importer des recettes (JSON)</b> — importe un fichier JSON contenant une ou plusieurs recettes.</li>
  <li><b>Exporter toutes les recettes (JSON)</b> — exporte l'intégralité de la base au format JSON.</li>
  <li><b>Voir le format d'import</b> — affiche le template JSON avec tous les champs disponibles et leurs valeurs valides.</li>
</ul>

<div class="note">
  <b>Sauvegarde automatique :</b> il est recommandé de sauvegarder régulièrement via
  <i>Fichier → Sauvegarder la base</i> avant toute opération d'import massif.
</div>
""")

SEARCH = _page("""
<h1>Panneau de recherche</h1>
<p>Le panneau Rechercher permet de trouver des recettes selon de multiples critères, combinables librement.</p>

<h2>Recherche par nom (floue)</h2>
<p>Saisissez tout ou partie du nom d'une recette dans la barre de recherche principale.
La recherche est <b>floue</b> (fuzzy matching) : elle tolère les fautes de frappe et les correspondances partielles.</p>
<div class="calc">
  Score de correspondance = max(
    ratio_partiel(requête, nom_recette),
    ratio_partiel(requête, description_recette)
  )
  Seuil minimum : 60 / 100 — les résultats sont triés du plus pertinent au moins pertinent.
</div>

<h2>Recherche par ingrédient</h2>
<p>Le champ <b>Par ingrédient</b> dispose d'une autocomplétion sur tous les ingrédients de la base.
La saisie est <b>insensible à la casse</b> et filtre par <i>contient</i> (ex : taper « tom » propose « tomate », « tomate cerise »…).
La recherche retourne toutes les recettes contenant cet ingrédient.</p>
<div class="note">
  Les caractères spéciaux sont normalisés automatiquement :
  « œuf » et « oeuf » sont traités de façon identique.
</div>

<h2>Filtres combinés</h2>
<table>
  <tr><th>Filtre</th><th>Valeurs possibles</th></tr>
  <tr><td>Type de plat</td><td>Entrée, Plat principal, Dessert, Soupe, Salade, Snack, Boisson, Sauce, Accompagnement</td></tr>
  <tr><td>Régime alimentaire</td><td>Standard, Végétarien, Végétalien, Sans lactose, Sans gluten</td></tr>
  <tr><td>Difficulté</td><td>Facile, Intermédiaire, Difficile</td></tr>
  <tr><td>Cuisine</td><td>Française, Italienne, Japonaise, Espagnole, Mexicaine, Indienne, Chinoise, Américaine, Méditerranéenne…</td></tr>
</table>
<p>Tous les filtres sont cumulables avec la recherche par nom et par ingrédient.
Cliquez sur <b>Réinitialiser</b> pour effacer tous les filtres d'un coup.</p>

<h2>Filtre calorique</h2>
<p>Cochez la case <b>Calories max par personne</b> pour activer le spinner (50 – 3 000 kcal, par pas de 50).
Seules les recettes dont les calories par portion sont renseignées ET inférieures ou égales à la valeur saisie apparaissent.</p>
<div class="tip">
  Exemple : pour un repas de midi léger, cochez la case et réglez le curseur sur 500 kcal.
  Les recettes sans données caloriques ne sont <i>pas</i> exclues si vous utilisez ce filtre en combinaison avec d'autres.
</div>

<h2>Ingrédients favoris</h2>
<p>La zone <b>★ Mes ingrédients favoris</b> affiche vos ingrédients marqués comme favoris.
Cliquez sur un tag pour lancer immédiatement une recherche sur cet ingrédient.
Le bouton <b>Rechercher avec tous mes favoris</b> lance une recherche globale sur l'ensemble de vos favoris.</p>

<h2>Filtre Recettes favorites</h2>
<p>Cliquez sur le bouton <b>☆ Recettes favorites</b> (à droite dans la barre de filtres) pour n'afficher
que vos recettes marquées comme favorites. Lorsqu'il est actif, le bouton affiche <b>★</b> en doré.</p>
<div class="tip">
  <b>Astuce :</b> combinez ce filtre avec la recherche par nom ou par ingrédient pour retrouver instantanément
  une recette favorite particulière.
</div>

<h2>Fiches résultats</h2>
<p>Chaque carte affiche : image, nom, badges (type, difficulté, cuisine), durée totale, régime, calories, et note.
La couleur du badge difficulté est : <span style="color:#27AE60"><b>vert</b></span> = Facile,
<span style="color:#E67E22"><b>orange</b></span> = Intermédiaire,
<span style="color:#C0392B"><b>rouge</b></span> = Difficile.</p>
""")

SEASONAL = _page("""
<h1>Vue saisonnière</h1>
<p>Cet écran vous aide à cuisiner en accord avec les saisons : ingrédients frais disponibles et recettes adaptées.</p>

<h2>Sélecteur de mois</h2>
<p>Le mois affiché par défaut est le mois courant. Le menu déroulant permet de naviguer librement vers n'importe quel mois de l'année.</p>

<h2>Saisons et couleurs</h2>
<table>
  <tr><th>Saison</th><th>Mois</th><th>Couleur titre</th></tr>
  <tr><td>Printemps</td><td>Mars, Avril, Mai</td><td style="color:#27AE60">Vert</td></tr>
  <tr><td>Été</td><td>Juin, Juillet, Août</td><td style="color:#E67E22">Orange</td></tr>
  <tr><td>Automne</td><td>Septembre, Octobre, Novembre</td><td style="color:#E67E22">Orange foncé</td></tr>
  <tr><td>Hiver</td><td>Décembre, Janvier, Février</td><td style="color:#3498DB">Bleu</td></tr>
</table>

<h2>Alerte fin de saison</h2>
<p>Si des ingrédients arrivent en fin de disponibilité dans les prochaines semaines, une zone d'alerte orange apparaît
en haut de la page avec le symbole ⚠. Profitez-en avant qu'ils ne disparaissent des étals !</p>

<h2>Ingrédients de saison</h2>
<p>La grille affiche tous les ingrédients disponibles pour le mois sélectionné.
Cliquez sur un ingrédient pour <b>filtrer les recettes</b> qui l'utilisent.
Cliquez à nouveau sur le même ingrédient (sélectionné en rouge foncé) pour annuler le filtre.</p>

<h2>Recettes de saison</h2>
<p>Chaque carte de recette affiche le <b>pourcentage d'ingrédients de saison</b> utilisés dans la recette,
calculé ainsi :</p>
<div class="calc">
  % ingrédients de saison = (nombre d'ingrédients de la recette présents dans la liste de saison
                              / nombre total d'ingrédients de la recette) × 100
</div>
<p>Lorsqu'un filtre par ingrédient est actif, le bouton <b>✕ Voir toutes les recettes de saison</b>
apparaît pour revenir à la vue complète.</p>
""")

FRIDGE = _page("""
<h1>Mon Frigo</h1>
<p>Ce mode vous propose automatiquement des recettes réalisables à partir des ingrédients que vous avez sous la main.</p>

<h2>Ajouter des ingrédients</h2>
<p>Tapez un ingrédient dans le champ de saisie (autocomplétion disponible) puis appuyez sur <b>Entrée</b>
ou cliquez sur <b>+ Ajouter</b>. L'ingrédient apparaît sous forme de tag dans la zone frigo (fond vert pâle, bordure en pointillés verts).</p>
<p>Pour retirer un ingrédient, cliquez sur le <b>×</b> à droite de son tag.
Le bouton <b>Vider le frigo</b> supprime tous les ingrédients d'un coup.</p>

<h2>Persistance entre sessions</h2>
<p>Le contenu de votre frigo est <b>sauvegardé automatiquement</b> dans la base de données.
Lorsque vous relancez l'application, vous retrouvez exactement les mêmes ingrédients.</p>

<h2>Calcul de compatibilité</h2>
<p>Pour chaque recette de la base, Recettor calcule le nombre d'ingrédients du frigo présents dans la recette :</p>
<div class="calc">
  matching_count = nombre d'ingrédients du frigo trouvés dans la liste d'ingrédients de la recette
  total          = nombre total d'ingrédients de la recette
  compatibilité  = round(matching_count / total × 100) %
</div>
<p>Les recettes sont triées du taux le plus élevé au plus bas. Seules les recettes ayant au moins 1 ingrédient en commun s'affichent.</p>

<h2>Code couleur des badges</h2>
<table>
  <tr><th>Compatibilité</th><th>Couleur</th><th>Signification</th></tr>
  <tr><td>≥ 80 %</td><td style="color:#1B5E20"><b>Vert</b></td><td>Recette très réalisable</td></tr>
  <tr><td>50 – 79 %</td><td style="color:#E67E22"><b>Orange</b></td><td>Recette partiellement réalisable, il manque quelques ingrédients</td></tr>
  <tr><td>&lt; 50 %</td><td style="color:#C0392B"><b>Rouge</b></td><td>Recette peu réalisable avec le frigo actuel</td></tr>
</table>

<div class="tip">
  <b>Astuce :</b> commencez par les recettes en vert — vous les réaliserez avec peu ou pas d'achats supplémentaires.
  Les recettes en orange vous indiquent les ingrédients manquants pour compléter votre liste de courses.
</div>

<h2>✨ Suggestions IA (Ollama)</h2>
<p>Le bouton <b>✨ Suggestions IA (Ollama)</b> (en bas du panneau Mon Frigo) envoie la liste de vos ingrédients
à un modèle de langage local <b>Ollama</b> pour obtenir des suggestions de recettes créatives,
même si elles ne figurent pas encore dans votre base.</p>

<h3>Prérequis</h3>
<ul>
  <li>Ollama doit être installé et démarré : <code>ollama serve</code></li>
  <li>Le modèle configuré doit être disponible (voir <code>config.py</code> : <code>OLLAMA_MODEL</code>, par défaut <code>qwen2.5:7b</code>)</li>
  <li>Avoir au moins un ingrédient dans le frigo</li>
</ul>

<h3>Cartes de suggestions</h3>
<p>Chaque carte contient le nom, la description, la liste des ingrédients et les étapes résumées.
Trois actions sont disponibles :</p>
<ul>
  <li><b>🔍 Voir le détail</b> — affiche une fiche avec les étapes numérotées</li>
  <li><b>💾 Sauvegarder dans Recettor</b> — enregistre la recette dans la base avec les données enrichies
      (nutrition, astuces, erreurs à éviter, variantes, source = nom du modèle)</li>
  <li><b>🛒 Ajouter manquants (N)</b> — ajoute les ingrédients manquants à la liste de courses
      (N = nombre d'ingrédients absents du frigo)</li>
</ul>

<h3>Messages d'erreur courants</h3>
<table>
  <tr><th>Message</th><th>Cause / Solution</th></tr>
  <tr><td>Ollama non disponible</td><td>Lancez <code>ollama serve</code> dans un terminal.</td></tr>
  <tr><td>Modèle introuvable</td><td>Lancez <code>ollama pull qwen2.5:7b</code>.</td></tr>
  <tr><td>Délai dépassé (120s)</td><td>Inférence trop lente (CPU). Essayez un modèle plus petit (<code>qwen2.5:3b</code>)
      ou augmentez <code>OLLAMA_TIMEOUT</code> dans <code>config.py</code>.</td></tr>
  <tr><td>Réponse invalide</td><td>Le modèle n'a pas respecté le JSON. Relancez la requête.</td></tr>
</table>
</div>
<div class="note">
  <b>Confidentialité :</b> Ollama fonctionne entièrement en local. Vos données ne quittent jamais votre machine.
</div>
""")

RECIPE_VIEW = _page("""
<h1>Fiche recette</h1>
<p>La fiche recette s'ouvre en cliquant sur n'importe quelle carte dans les vues Recherche, Saisonnalité ou Mon Frigo.
Elle est organisée en <b>6 onglets</b>.</p>

<h2>Onglet Présentation</h2>
<p>Vue d'ensemble de la recette :</p>
<ul>
  <li><b>Photo</b> (à gauche) avec infos rapides : temps de préparation, temps de cuisson, temps de repos, durée totale, nombre de portions, coût estimé, saison idéale, note.</li>
  <li><b>Badges</b> (type de plat, difficulté, cuisine, régime).</li>
  <li>Description, histoire/origine, auteur, source, région, occasion.</li>
  <li>Tags cliquables et notes personnelles.</li>
</ul>

<h2>Onglet Ingrédients</h2>
<p>Tableau complet des ingrédients pour le nombre de portions prévu :</p>
<table>
  <tr><th>Colonne</th><th>Description</th></tr>
  <tr><td>Ingrédient</td><td>Nom (avec majuscule initiale)</td></tr>
  <tr><td>Quantité</td><td>Valeur numérique</td></tr>
  <tr><td>Unité</td><td>g, ml, pièce, cuillère à soupe…</td></tr>
  <tr><td>Préparation</td><td>Mode de préparation (émincé, en dés…)</td></tr>
  <tr><td>Optionnel</td><td>Marqué « Optionnel » en gris si non obligatoire</td></tr>
  <tr><td>Remplacement</td><td>Ingrédient de substitution possible</td></tr>
  <tr><td>Qualité</td><td>Précisions sur la qualité souhaitée</td></tr>
</table>

<h2>Onglet Étapes</h2>
<p>Les étapes de préparation s'affichent dans l'ordre chronologique.
Chaque étape indique son numéro, la technique utilisée, la durée en minutes,
et la température si applicable (cuisson au four, etc.).</p>

<h2>Onglet Informations</h2>
<p>Informations pratiques regroupées en 5 sections :</p>
<ul>
  <li><b>Équipement nécessaire</b> — ustensiles et appareils requis.</li>
  <li><b>Allergènes</b> — liste des allergènes présents (ou « Aucun allergène renseigné »).</li>
  <li><b>Paramètres de cuisson</b> — type de cuisson, température du four, puissance du feu.</li>
  <li><b>Conservation</b> — durées au réfrigérateur, au congélateur, méthode de réchauffage.</li>
  <li><b>Profil sensoriel</b> — profil aromatique, intensité du goût, texture, indice glycémique.</li>
</ul>

<h2>Onglet Nutrition</h2>

<h3>Graphique macronutriments</h3>
<p>Le donut chart répartit visuellement les <b>glucides</b> (bleu), <b>protéines</b> (rouge) et <b>lipides</b> (orange)
en pourcentage de la masse totale des macros :</p>
<div class="calc">
  % glucides   = glucides (g)  / (glucides + protéines + lipides) × 100
  % protéines  = protéines (g) / (glucides + protéines + lipides) × 100
  % lipides    = lipides (g)   / (glucides + protéines + lipides) × 100
</div>
<p>La légende affiche également la masse totale des macros et l'équivalent calorique estimé :</p>
<div class="calc">
  Énergie estimée = glucides × 4 kcal + protéines × 4 kcal + lipides × 9 kcal
</div>

<h3>Calculateur calorique</h3>
<p>Saisissez votre <b>objectif calorique</b> (en kcal) et cliquez sur <b>Calculer</b>.
Le résultat s'affiche automatiquement au chargement de l'onglet avec la valeur par défaut (400 kcal).</p>
<div class="calc">
  ratio         = objectif_kcal / calories_par_portion
  % portion     = ratio × 100
  poids assiette = poids_moyen_par_portion (g) × ratio

  Poids moyen par portion = somme de tous les ingrédients convertis en g ou ml
                            (g, kg, ml, cl, l, cuillère à café=5ml, cuillère à soupe=15ml)
                            divisée par le nombre de portions
</div>
<p>Exemple : recette à 415 kcal/portion, objectif 400 kcal :</p>
<div class="calc">
  ratio     = 400 / 415 = 0,964
  % portion = 96 %  →  « 96% d'une portion individuelle (415 kcal × 96% = 400 kcal) »
</div>
<p>Le tableau des ingrédients ajustés montre les quantités recalculées avec ce ratio pour chaque ingrédient.</p>

<h3>Valeurs nutritionnelles complètes</h3>
<p>Tableau récapitulatif par portion : calories, glucides, protéines, lipides, fibres, sucre, sel.
Les valeurs à zéro ne sont pas affichées.</p>

<h2>Onglet Conseils</h2>
<p>Cinq catégories de conseils, chacune avec son code couleur :</p>
<table>
  <tr><th>Catégorie</th><th>Couleur</th></tr>
  <tr><td>Astuces du chef</td><td style="background:#FFF9C4">Jaune</td></tr>
  <tr><td>Erreurs à éviter</td><td style="background:#FADBD8">Rouge pâle</td></tr>
  <tr><td>Variantes</td><td style="background:#D5F5E3">Vert pâle</td></tr>
  <tr><td>Accompagnements</td><td style="background:#EBF5FB">Bleu pâle</td></tr>
  <tr><td>Accords mets &amp; boissons</td><td style="background:#F5EEF8">Violet pâle</td></tr>
</table>

<h2>Modifier et supprimer</h2>
<p>Les boutons <b>Modifier</b> et <b>Supprimer</b> sont accessibles dans l'en-tête de la fiche.
La suppression demande une confirmation. Après modification ou suppression, tous les panneaux
de l'application (recherche, saisonnalité, frigo) se mettent à jour automatiquement.</p>

<h2>Marquer comme favori</h2>
<p>Dans l'en-tête de la fiche, le bouton <b>☆ Favori</b> permet de marquer ou démarquer la recette comme favorite.
L'étoile passe en orange (<b>★ Favori</b>) lorsque la recette est dans les favoris.
Retrouvez toutes vos recettes favorites dans <b>★ Favoris → onglet ★ Recettes</b> ou via le filtre
<b>☆ Recettes favorites</b> dans le panneau Recherche.</p>
""")

ADD_RECIPE = _page("""
<h1>Ajouter / Modifier une recette</h1>
<p>Le formulaire de saisie est organisé en <b>9 onglets</b>. Seul le champ <b>Nom</b> est obligatoire.</p>

<h2>Onglet 1 — Identification</h2>
<ul>
  <li><b>Nom *</b> — champ obligatoire, unique identifiant de la recette.</li>
  <li>Autres noms, description, histoire/origine, auteur, source.</li>
  <li>Type de cuisine (liste + saisie libre), région, occasion.</li>
  <li>Type de plat, catégorie, régime alimentaire, saison idéale.</li>
</ul>

<h2>Onglet 2 — Temps & Difficulté</h2>
<ul>
  <li>Temps de préparation, de cuisson, de repos (en minutes).</li>
  <li><b>Durée totale</b> calculée automatiquement (affichée en h:mm si &gt; 60 min).</li>
  <li>Difficulté, nombre de portions, coût estimé, note (/5 par pas de 0,5).</li>
</ul>

<h2>Onglet 3 — Ingrédients</h2>
<p>Tableau de saisie des ingrédients. Boutons <b>Ajouter un ingrédient</b> / <b>Supprimer la sélection</b>.</p>
<ul>
  <li>Le champ <i>Ingrédient</i> dispose d'une autocomplétion sur les ingrédients déjà connus.</li>
  <li>Si un ingrédient nouveau est saisi, il est automatiquement créé dans la base.</li>
  <li>Chaque ligne : nom, quantité, unité, préparation, optionnel (case à cocher), remplacement, qualité.</li>
</ul>
<div class="note">
  Les noms d'ingrédients sont normalisés automatiquement (minuscules, suppression des ligatures
  œ→oe, æ→ae) pour garantir la cohérence de la recherche.
</div>

<h2>Onglet 4 — Étapes</h2>
<p>Chaque étape contient : numéro, durée (min), température (°C), technique (liste + libre), et description.
Boutons <b>Ajouter une étape</b> / <b>Supprimer la dernière étape</b>.</p>

<h2>Onglet 5 — Équipement & Allergènes</h2>
<ul>
  <li><b>Équipement</b> — cases à cocher sur une liste prédéfinie + champ « Autre équipement » libre.</li>
  <li><b>Allergènes</b> — cases à cocher sur la liste officielle des 14 allergènes majeurs.</li>
</ul>

<h2>Onglet 6 — Nutrition</h2>
<p>Valeurs nutritionnelles <b>par portion</b> :</p>
<ul>
  <li>Calories (kcal), protéines (g), glucides (g), lipides (g), fibres (g), sucre (g), sel (g).</li>
  <li>Vitamines et minéraux (champs texte libres).</li>
</ul>
<div class="tip">
  Ces données permettent d'activer le filtre calorique dans la recherche et le calculateur calorique dans la fiche.
</div>

<h2>Onglet 7 — Cuisson & Conservation</h2>
<ul>
  <li>Température du four (°C), puissance du feu, type de cuisson.</li>
  <li>Durée de conservation au réfrigérateur et au congélateur, méthode de réchauffage, méthode de stockage.</li>
  <li>Présentation : type d'assiette, disposition, décoration, garniture.</li>
</ul>

<h2>Onglet 8 — Conseils & Tags</h2>
<ul>
  <li>Cinq zones de saisie (une ligne = un conseil) : astuces, erreurs à éviter, variantes, accompagnements, accords.</li>
  <li>Tags : mots-clés séparés par des virgules (ex : <code>été, végétarien, rapide</code>).</li>
  <li>Notes personnelles, profil aromatique, intensité du goût, texture, indice glycémique.</li>
</ul>

<h2>Onglet 9 — Photo</h2>
<p>Choisissez une image (JPG, PNG, GIF, BMP, WEBP) depuis votre disque.
Elle est copiée automatiquement dans le dossier <code>images/</code> de l'application avec un nom sécurisé.
Un aperçu 400×300 px est affiché. Vous pouvez la supprimer avec le bouton dédié.</p>

<h2>Enregistrement</h2>
<p>Cliquez sur <b>Enregistrer la recette</b>. Si le nom est vide, un avertissement s'affiche.
Après enregistrement, tous les panneaux se rafraîchissent automatiquement.</p>
""")

IMPORT_EXPORT = _page("""
<h1>Import / Export JSON</h1>
<p>Recettor utilise un format JSON standardisé pour échanger des recettes entre instances ou partager vos créations.</p>

<h2>Structure du fichier JSON</h2>
<div class="calc">
{
  "recettes": [
    {
      "nom": "Nom de la recette",   ← OBLIGATOIRE
      "type_plat": "Plat principal",
      "regime": "Standard",
      "difficulte": "Facile",
      "saison_ideale": "Toutes saisons",
      "calories": 350,
      "ingredients": [ { "nom": "tomate", "quantite": 4, "unite": "pièce" } ],
      "etapes": [ { "numero": 1, "description": "...", "duree": 10 } ],
      ...
    }
  ]
}
</div>

<h2>Valeurs acceptées pour les champs clés</h2>
<table>
  <tr><th>Champ JSON</th><th>Valeurs valides</th></tr>
  <tr><td><code>regime</code></td><td>Standard, Végétarien, Végétalien, Sans lactose, Sans gluten</td></tr>
  <tr><td><code>difficulte</code></td><td>Facile, Intermédiaire, Difficile</td></tr>
  <tr><td><code>saison_ideale</code></td><td>Toutes saisons, Printemps, Été, Automne, Hiver</td></tr>
  <tr><td><code>type_plat</code></td><td>Entrée, Plat principal, Dessert, Soupe, Salade, Snack, Boisson, Sauce, Accompagnement</td></tr>
  <tr><td><code>type_cuisine</code></td><td>Française, Italienne, Japonaise, Espagnole, Mexicaine, Indienne, Chinoise, Américaine, Méditerranéenne…</td></tr>
</table>
<p>Les valeurs en dehors de ces listes sont acceptées mais n'alimenteront pas les filtres de la recherche.</p>

<h2>Importer des recettes</h2>
<p>Via <b>Importer/Exporter → Importer (JSON)</b> ou <b>Outils → Importer des recettes (JSON)</b>.
Sélectionnez votre fichier JSON. En cas d'erreur sur une recette individuelle,
les autres recettes valides sont quand même importées et le rapport d'erreurs est affiché.</p>

<h2>Exporter des recettes</h2>
<p>Via <b>Importer/Exporter → Exporter tout (JSON)</b>. Choisissez l'emplacement et le nom du fichier.
<b>Toutes</b> les recettes de la base sont exportées en un seul fichier JSON.
Ce fichier peut être réimporté dans n'importe quelle instance de Recettor.</p>

<h2>Format d'import complet</h2>
<p>Consultez <b>Outils → Voir le format d'import</b> pour afficher le template JSON annoté
avec l'intégralité des champs disponibles et des exemples de valeurs.</p>

<div class="warn">
  <b>Doublons :</b> il n'y a pas de vérification de doublon à l'import.
  Importer deux fois le même fichier créera deux fois les mêmes recettes.
  Effectuez une sauvegarde avant un import massif.
</div>
""")

FAVORITES = _page("""
<h1>Gestion des favoris</h1>
<p>La fenêtre <b>★ Mes Favoris</b> (barre latérale) est organisée en deux onglets :
<b>★ Ingrédients</b> et <b>★ Recettes</b>. Tous les favoris sont persistants (sauvegardés en base).</p>

<h2>Onglet ★ Ingrédients</h2>
<p>Les ingrédients favoris sont des raccourcis de recherche que vous utilisez fréquemment.</p>

<h3>Ajouter un ingrédient favori</h3>
<p>Tapez un ingrédient (autocomplétion disponible) et cliquez sur <b>★ Ajouter</b> ou appuyez sur Entrée.
Si l'ingrédient est déjà dans vos favoris, un message vous l'indique.</p>

<h3>Supprimer un ingrédient favori</h3>
<p>Cliquez sur le <b>✕</b> du tag à supprimer, ou utilisez <b>Tout supprimer</b> (avec confirmation).</p>

<h3>Utiliser les ingrédients favoris dans la recherche</h3>
<p>Dans le panneau Recherche, les tags favoris apparaissent en jaune dans la zone <b>★ Mes ingrédients favoris</b>.
Deux usages :</p>
<ul>
  <li><b>Cliquer sur un tag</b> : lance la recherche sur cet ingrédient seul.</li>
  <li><b>Rechercher avec tous mes favoris</b> : lance une recherche qui retourne les recettes
      contenant <i>au moins un</i> de vos ingrédients favoris.</li>
</ul>

<h2>Onglet ★ Recettes</h2>
<p>Vos recettes favorites, ajoutées via le bouton <b>☆ Favori</b> dans la fiche de chaque recette.</p>

<h3>Ajouter une recette aux favoris</h3>
<p>Ouvrez une recette et cliquez sur <b>☆ Favori</b> dans son en-tête.
L'étoile passe en orange (<b>★ Favori</b>) pour confirmer l'ajout.</p>

<h3>Accéder aux recettes favorites</h3>
<ul>
  <li>Via <b>★ Favoris → onglet ★ Recettes</b> : liste complète avec badges de type, difficulté et cuisine.
      Boutons <b>Ouvrir</b> et <b>✕</b> (retirer des favoris).</li>
  <li>Via le filtre <b>☆ Recettes favorites</b> dans le panneau Recherche : affiche uniquement vos recettes
      favorites parmi les résultats.</li>
</ul>

<h3>Retirer une recette des favoris</h3>
<p>Cliquez sur <b>✕</b> dans la liste des favoris, ou cliquez à nouveau sur <b>★ Favori</b> dans la fiche recette.</p>

<div class="note">
  Supprimer une recette de la base la retire automatiquement de vos favoris.
</div>
""")

SHOPPING_LIST = _page("""
<h1>Liste de courses</h1>
<p>Accessible via <b>🛒 Liste de courses</b> dans la barre latérale, ce panneau vous permet de noter
les articles à acheter et de les cocher au fur et à mesure de vos achats.</p>

<h2>Ajouter un article</h2>
<p>Tapez le nom de l'article dans le champ de saisie et appuyez sur <b>Entrée</b> ou cliquez sur <b>+ Ajouter</b>.
Si l'article est déjà dans la liste, il n'est pas dupliqué.</p>

<h2>Cocher / Décocher un article</h2>
<p>Cliquez sur la case à gauche de l'article pour le cocher (texte barré = article acheté).
Cliquez à nouveau pour le décocher.</p>

<h2>Supprimer des articles</h2>
<ul>
  <li>Bouton <b>✕</b> à droite d'un article : supprime cet article uniquement.</li>
  <li><b>Supprimer les cochés</b> : retire tous les articles cochés d'un coup.</li>
  <li><b>Tout vider</b> : efface toute la liste (avec confirmation).</li>
</ul>

<h2>Ajout automatique depuis les suggestions IA</h2>
<p>Dans la fenêtre de suggestions IA (Mon Frigo → ✨ Suggestions IA), chaque carte affiche le bouton
<b>🛒 Ajouter manquants (N)</b> lorsque des ingrédients de la recette sont absents du frigo.
Cliquez dessus pour les ajouter automatiquement à votre liste de courses.</p>

<div class="tip">
  <b>Workflow recommandé :</b>
  <ol>
    <li>Ajoutez vos ingrédients dans <b>Mon Frigo</b></li>
    <li>Cliquez sur <b>✨ Suggestions IA</b> pour obtenir des idées de recettes</li>
    <li>Cliquez sur <b>🛒 Ajouter manquants</b> pour peupler la liste de courses automatiquement</li>
    <li>Au supermarché, cochez les articles un par un</li>
    <li>Cliquez sur <b>Supprimer les cochés</b> pour nettoyer la liste</li>
  </ol>
</div>

<h2>Persistance</h2>
<p>La liste est sauvegardée en base SQLite et persiste entre toutes les sessions.
L'état coché/décoché de chaque article est également mémorisé.</p>
""")

OLLAMA_AI = _page("""
<h1>Intelligence artificielle (Ollama)</h1>
<p>Recettor s'intègre avec <b>Ollama</b>, un moteur d'inférence local qui fait tourner des modèles de langage
entièrement sur votre machine — aucune donnée n'est envoyée à Internet.</p>

<h2>Installation d'Ollama</h2>
<ol>
  <li>Téléchargez Ollama sur <b>ollama.com</b></li>
  <li>Installez-le (Linux, macOS ou Windows)</li>
  <li>Démarrez le service : <code>ollama serve</code></li>
  <li>Téléchargez le modèle recommandé : <code>ollama pull qwen2.5:7b</code></li>
</ol>

<h2>Configuration dans Recettor</h2>
<p>Trois paramètres dans <code>config.py</code> :</p>
<table>
  <tr><th>Paramètre</th><th>Valeur par défaut</th><th>Description</th></tr>
  <tr><td><code>OLLAMA_BASE_URL</code></td><td><code>http://localhost:11434</code></td><td>URL du serveur Ollama</td></tr>
  <tr><td><code>OLLAMA_MODEL</code></td><td><code>qwen2.5:7b</code></td><td>Nom du modèle à utiliser</td></tr>
  <tr><td><code>OLLAMA_TIMEOUT</code></td><td><code>120</code></td><td>Délai maximal en secondes</td></tr>
</table>

<h2>Choisir le bon modèle</h2>
<table>
  <tr><th>Modèle</th><th>RAM requise</th><th>GPU</th><th>Vitesse CPU</th><th>Qualité</th></tr>
  <tr><td><code>qwen2.5:3b</code></td><td>~3 Go</td><td>Non requis</td><td>Rapide (~30 s)</td><td>Basique</td></tr>
  <tr><td><code>qwen2.5:7b</code></td><td>~8 Go</td><td>Non requis</td><td>Moyen (~90 s)</td><td>Bonne ✓</td></tr>
  <tr><td><code>qwen2.5:14b</code></td><td>~16 Go</td><td>Recommandé</td><td>Lent (&gt;120 s)</td><td>Excellente</td></tr>
</table>

<h2>Données renvoyées par le modèle</h2>
<p>Ollama reçoit un prompt système qui lui demande un tableau JSON de recettes avec les champs :</p>
<div class="calc">
  nom, description, ingredients[], etapes_resume,
  temps_preparation, temps_cuisson, nb_portions,
  type_plat, type_cuisine, regime, saison,
  calories_portion, proteines, glucides, lipides, fibres,
  astuces[], erreurs_a_eviter[], variantes[]
</div>
<p>Lorsque vous sauvegardez une recette, tous ces champs sont enregistrés dans la base :
la source est automatiquement remplie avec le nom du modèle, et les notes personnelles indiquent
<i>« Recette générée par : &lt;modèle&gt; »</i>.</p>

<h2>Messages d'erreur</h2>
<table>
  <tr><th>Message affiché</th><th>Cause</th><th>Solution</th></tr>
  <tr><td>Ollama non disponible</td><td>Service non démarré</td><td><code>ollama serve</code></td></tr>
  <tr><td>Modèle introuvable</td><td>Modèle non téléchargé</td><td><code>ollama pull qwen2.5:7b</code></td></tr>
  <tr><td>Délai dépassé (120s)</td><td>Inférence trop lente (CPU)</td><td>Utiliser <code>qwen2.5:3b</code> ou augmenter <code>OLLAMA_TIMEOUT</code></td></tr>
  <tr><td>Réponse invalide</td><td>JSON malformé par le modèle</td><td>Relancer la requête</td></tr>
</table>

<div class="note">
  <b>Confidentialité :</b> Ollama fonctionne entièrement en local.
  Vos ingrédients et recettes ne quittent jamais votre machine.
</div>
""")

CALCULATIONS = _page("""
<h1>Détail de tous les calculs</h1>
<p>Cette page récapitule l'ensemble des formules utilisées dans Recettor.</p>

<h2>Recherche floue (Fuzzy Search)</h2>
<p>La recherche par nom utilise l'algorithme <b>partial_ratio</b> de la bibliothèque
<i>fuzzywuzzy</i> (distance de Levenshtein). Il cherche la meilleure sous-chaîne
correspondante, ce qui tolère les fautes de frappe et les saisies partielles.</p>
<hr/>
<div class="calc">
  score = max( partial_ratio(requête, nom_recette),
               partial_ratio(requête, description_recette) )

  Seuil minimum : score ≥ 60 / 100
  Tri           : score décroissant (meilleure correspondance en premier)
</div>

<h2>Compatibilité Frigo</h2>
<p>Pour chaque recette de la base, Recettor compte combien d'ingrédients du frigo
sont présents dans la liste d'ingrédients de la recette, puis calcule un taux de
compatibilité. La requête SQL utilise <code>SUM(CASE WHEN … THEN 1 ELSE 0 END)</code>
pour compter les correspondances directement en base.</p>
<hr/>
<div class="calc">
  matching = COUNT( ingrédients_recette ∩ ingrédients_frigo )
  total    = COUNT( ingrédients_recette )
  score    = ROUND( matching / total × 100 )

  SQL :
    SUM(CASE WHEN ingredient.name IN (liste_frigo) THEN 1 ELSE 0 END) AS matching_count
    COUNT(ingredient.name) AS total_ingredients

  Tri    : score décroissant (côté Python après la requête SQL)
  Filtre : seules les recettes avec matching ≥ 1 sont affichées
</div>

<h2>Énergie des macronutriments (donut chart)</h2>
<p>Le graphique en donut répartit visuellement les trois macronutriments selon leur
part de masse totale. L'énergie estimée est calculée avec les coefficients
énergétiques standard (Atwater).</p>
<hr/>
<div class="calc">
  Coefficients Atwater :
    Glucides   → 4 kcal / g
    Protéines  → 4 kcal / g
    Lipides    → 9 kcal / g

  Énergie estimée = glucides × 4  +  protéines × 4  +  lipides × 9   (kcal)

  Répartition graphique :
    part glucides   = glucides   / (glucides + protéines + lipides) × 100
    part protéines  = protéines  / (glucides + protéines + lipides) × 100
    part lipides    = lipides    / (glucides + protéines + lipides) × 100
</div>

<h2>Calculateur calorique</h2>
<p>Saisissez un objectif calorique (ex : 400 kcal pour un repas léger). Recettor
calcule quelle fraction d'une portion individuelle correspond à cet objectif,
puis ajuste le poids dans l'assiette et les quantités de chaque ingrédient.</p>
<hr/>
<div class="calc">
  ratio          = objectif_kcal / calories_par_portion
  portion        = ratio × 100  %  (affiché arrondi à l'entier)
  kcal résultant = calories_par_portion × ratio  =  objectif_kcal  ✓
</div>
<p>Estimation du poids dans l'assiette — seuls les ingrédients exprimés en
unités convertibles (g, kg, ml, cl, l, cuillère…) sont pris en compte :</p>
<hr/>
<div class="calc">
  Facteurs de conversion vers grammes / millilitres :
    g=1,  kg=1 000,  ml=1,  cl=10,  l=1 000
    cuillère à café = 5,  cuillère à soupe = 15

  poids_portion_g  = Σ( quantité × facteur ) / nombre_de_portions
  poids_assiette   = poids_portion_g × ratio
</div>
<p>Quantités des ingrédients ajustées pour l'objectif calorique :</p>
<hr/>
<div class="calc">
  quantité_ajustée = (quantité_recette / portions) × ratio
                   = quantité pour 1 portion × ratio
</div>

<h2>Durée totale (formulaire de saisie)</h2>
<p>La durée totale est calculée automatiquement pendant la saisie, sans action de l'utilisateur.</p>
<hr/>
<div class="calc">
  durée_totale = temps_préparation + temps_cuisson + temps_repos   (minutes)
  Affichage    : si durée > 60 min  →  format "Xh YYmin"
                 sinon              →  format "YY min"
</div>

<h2>Ingrédients de saison</h2>
<p>La base contient une table <code>seasonal_ingredients</code> qui associe chaque
ingrédient aux mois pendant lesquels il est disponible. Le pourcentage affiché sur
chaque carte de recette mesure combien de ses ingrédients sont de saison ce mois-ci.</p>
<hr/>
<div class="calc">
  saison = COUNT( ingrédients_recette ∩ seasonal_ingredients[mois_courant] )
  total  = COUNT( ingrédients_recette )
  score  = ROUND( saison / total × 100 )
</div>

<h2>Normalisation des ingrédients</h2>
<p>Pour garantir que « Oeuf », « oeuf », « Œuf » et « œuf » désignent bien le même
ingrédient, tous les noms passent par une fonction de normalisation au moment de
l'enregistrement <b>et</b> au moment de la recherche.</p>
<hr/>
<div class="calc">
  normalize(name) :
    1. Conversion en minuscules
    2. Suppression des ligatures :  œ → oe,  Œ → Oe,  æ → ae,  Æ → Ae
    3. Suppression des espaces en début et fin (strip)

  Résultat : « Œuf », « oeuf », « OEUF »  →  tous stockés comme  « oeuf »
</div>

<h2>Compteur de recettes (barre de statut)</h2>
<p>Le nombre de recettes affiché en bas de fenêtre est recalculé après chaque
ajout, modification ou suppression de recette.</p>
<hr/>
<div class="calc">
  SELECT COUNT(*) FROM recipes
</div>
""")


# ── Dialogue principal ────────────────────────────────────────────────────────

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aide — Recettor")
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowMaximizeButtonHint
        )
        self.resize(900, 680)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(0)

        # En-tête
        header = QLabel("  Documentation complète de Recettor")
        header.setFont(QFont("Arial", 15, QFont.Bold))
        header.setFixedHeight(48)
        header.setStyleSheet(
            "background-color: #2C1810; color: #F0E8D8; padding-left: 16px;"
        )
        layout.addWidget(header)

        # Onglets
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.setStyleSheet("""
            QTabBar::tab { padding: 6px 14px; font-size: 12px; }
            QTabBar::tab:selected { font-weight: bold; color: #8B4513; }
        """)

        pages = [
            ("Vue d'ensemble",          OVERVIEW),
            ("Recherche",               SEARCH),
            ("Saisonnalité",            SEASONAL),
            ("Mon Frigo",               FRIDGE),
            ("🛒 Liste de courses",     SHOPPING_LIST),
            ("Fiche recette",           RECIPE_VIEW),
            ("Ajouter / Modifier",      ADD_RECIPE),
            ("Import / Export",         IMPORT_EXPORT),
            ("★ Favoris",              FAVORITES),
            ("✨ IA (Ollama)",          OLLAMA_AI),
            ("Calculs & formules",      CALCULATIONS),
        ]
        for title, html in pages:
            browser = QTextBrowser()
            browser.setOpenExternalLinks(False)
            browser.document().setDocumentMargin(16)
            browser.setHtml(html)
            browser.setStyleSheet("border: none; background: white;")
            tabs.addTab(browser, title)

        layout.addWidget(tabs)

        # Bouton fermer
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(12, 4, 12, 0)
        btn_row.addStretch()
        close_btn = QPushButton("Fermer")
        close_btn.setMinimumWidth(100)
        close_btn.setMinimumHeight(36)
        close_btn.setStyleSheet(
            "QPushButton { background-color: #D4A574; color: #2C1810; border-radius: 6px; "
            "padding: 4px 20px; font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background-color: #C4956A; }"
        )
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)
