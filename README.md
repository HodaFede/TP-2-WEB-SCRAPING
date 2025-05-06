# TP-2-WEB-SCRAPING Scraper Doctolib

Ce projet est un script Python qui récupère automatiquement des informations sur des médecins depuis Doctolib (nom, adresse, prix, disponibilité…) et sauvegarde le tout dans un fichier CSV.

# Ce que j'ai fait

* Un craper complet avec :

  * Récupération des paramètres de recherche via le terminal (spécialité, secteur, type de consultation, etc.),
  * Ouverture automatique de Doctolib avec Selenium,
  * Recherche automatique de la spécialité médicale,
  * Scraping des informations essentielles (nom, adresse, prix, type de consultation…),
  * Possibilité de filtrer par code postal (ou exclure certaines adresses),
  * Gestion automatique de la pagination (il passe à la page suivante jusqu'à atteindre le nombre de résultats demandé),
  * Sauvegarde propre dans un fichier CSV.
  * * La gestion des erreurs : si un problème survient, le script sauvegarde la page dans `debug_page.html` pour pouvoir analyser ce   qui a bloqué.


# Utilité 
* Apprendre à utiliser Selenium pour automatiser des recherches sur le web,
* Comprendre comment structurer un script qui gère à la fois les entrées utilisateur, la navigation web, et l'export des données,
* Travailler sur un cas concret

# Ce qui me manque encore

* Filtrage dynamique sur le site :
  Actuellement, les filtres (secteur, prix minimum/maximum, type de consultation) sont appliqués après le scraping en Python, mais pas directement sur le site. Cela veut dire que le script scrape tous les résultats puis filtre ceux qui correspondent.

* Robustesse aux changements du site :
  Doctolib change parfois ses classes CSS et sa structure. Aujourd’hui le script fonctionne, mais il peut casser si la structure du site évolue.

* Rapidité :
  Le scraping est séquentiel (il scrape un résultat après l’autre, page par page). 

---

# Ce que j'aurais pu faire 

* Automatiser les filtres directement sur le site (en cliquant sur les filtres Doctolib ou en modifiant l’URL avec les bons paramètres),
* Ajouter une interface graphique simple pour que ce soit plus agréable que le terminal,
* Utiliser des outils comme BeautifulSoup en plus de Selenium pour aller plus vite si on travaille avec du HTML statique,
* Prévoir un système qui vérifie régulièrement si les sélecteurs CSS ont changé,
* Pourquoi pas un mode headless activé par défaut pour éviter d'ouvrir Chrome à chaque fois !

---

# Prérequis

* Python 3
* Google Chrome
* [ChromeDriver](https://chromedriver.chromium.org/downloads)

Installer Selenium :

```bash
pip install selenium
```

---

#Utilisation

Lancer le script :

```bash
python doctolib_scraper.py
```

Répondre aux questions (nombre de résultats, spécialité, secteur, code postal…).
# Résultat
Les résultats sont sauvegardés dans un fichier `doctors_results.csv`.

# Exemple d’amélioration technique

Si je voulais appliquer les filtres dès la recherche, j'aurais pu :

* Repérer les boutons/menus sur Doctolib pour choisir secteur / consultation / prix,
* Automatiser le clic dessus avec Selenium avant d'exécuter la recherche.

Cela rendrait le scraping plus rapide et plus propre, car il ne collecterait que des résultats pertinents dès le départ.

