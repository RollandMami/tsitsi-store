
# Tsitsi Store

- **Author**: ANDRIANAVALONA Maminirina rolland

## Description

Projet e-commerce développé avec Django. Ce dépôt contient l'application back-end et les templates nécessaires pour gérer un catalogue de produits, un panier, le processus de commande, la gestion des utilisateurs et les notifications.

## Utilisation

1. Créer un environnement virtuel et l'activer.
2. Installer les dépendances :

```bash
pip install -r requirement.txt
```

3. Appliquer les migrations :

```bash
python manage.py makemigrations
python manage.py migrate
```

4. Mettre à jour les produits 'is_main_representative' (important après ajout de ce champ) :

```bash
python manage.py shell
```

Puis dans le shell Python Django:

```python
from store.models import Product

# Reset au cas où
Product.objects.update(is_main_representative=False)

# Option 1 : tous les produits disponibles deviennent représentants
Product.objects.filter(is_available=True).update(is_main_representative=True)

# Option 2 (recommandé pour variantes groupées) : un représentant par group_id
for group in Product.objects.values_list('group_id', flat=True).distinct():
    if not group:
        continue
    main = Product.objects.filter(group_id=group, is_available=True).order_by('-created_date').first()
    if main:
        main.is_main_representative = True
        main.save()

# Vérifier
print(Product.objects.filter(is_available=True, is_main_representative=True).count())
```

5. Créer un superutilisateur (si besoin) :

```bash
python manage.py createsuperuser
```

5. Lancer le serveur de développement :

```bash
python manage.py runserver
```

6. Accéder à l'application depuis `http://127.0.0.1:8000/`.

## Ressource

- Framework principal : Django
- Base de données : SQLite (fichier `db.sqlite3`)
- Frontend : templates Django + bibliothèques CSS/JS standard (Bootstrap, etc.)
- Fichiers de configuration principaux : [tsitsistore/settings.py](tsitsistore/settings.py)

## Détails sur les algorithmes utilisés et pourquoi les avoir choisis

### Note importante sur `is_main_representative` et `group_id`

- `group_id` permet d'indiquer des variantes d'un même produit (couleurs, tailles, etc.).
- `Product` avec `group_id=None` ou chaîne vide est considéré comme produit unique (sans variantes).
- En affichage (vues `home`, `products_list_view`, `search`) seuls les produits avec `is_main_representative=True` sont montrés.
- Si tu ajoutes le champ `is_main_representative` par migration, il faut fixer explicitement ce booléen pour les anciens enregistrements.

### Commande à exécuter après migration

```bash
python manage.py shell
```

```python
from store.models import Product

# Tout remettre à False (sécurisé)
Product.objects.update(is_main_representative=False)

# Produits uniques (sans groupe) restent visibles
Product.objects.filter(group_id__isnull=True, is_available=True).update(is_main_representative=True)
Product.objects.filter(group_id='', is_available=True).update(is_main_representative=True)  # si tu as stocké une chaîne vide

# Une seule représentation par groupe (variantes)
for group in Product.objects.exclude(group_id__isnull=True).exclude(group_id='').values_list('group_id', flat=True).distinct():
    main = Product.objects.filter(group_id=group, is_available=True).order_by('-created_date').first()
    if main:
        main.is_main_representative = True
        main.save()

# Vérification
print("représentatifs:", Product.objects.filter(is_available=True, is_main_representative=True).count())
```

- Pagination : limitation du nombre d'objets par page pour réduire la charge mémoire et améliorer la latence côté client.
- Caching (le cas échéant) : cache par vue ou fragments de template pour réduire les accès répétés à la base de données et accélérer les pages à fort trafic.
- Recherche et recommandations : approche simple basée sur la correspondance de catégories/attributs produits (similarité par catégorie/tags) — choisie pour sa simplicité d'implémentation et ses performances acceptables sans infrastructure ML dédiée.
- Traitement des commandes : logique transactionnelle via l'ORM (transactions DB) pour garantir la cohérence des stocks et des commandes.

Si vous souhaitez que j'ajoute des sections supplémentaires (ex. architecture, tests, CI/CD, ou exemples d'API), dites-le et je l'ajouterai.

# Mis à jour du redimentionnement des images

```bash
python ./manage.py shell
from store.models import Product
for p in Product.objects.all():
    p.save() # Le redimensionnement se déclenche ici

```
