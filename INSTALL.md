# 🍽️ Installation de Recettor

## ⚡ Installation rapide (paquet .deb — recommandée)

> Compatible Ubuntu 20.04+ et Debian 11+

### 1. Télécharger le paquet

Rendez-vous sur la page [Releases GitHub](https://github.com/nouhailler/recettor/releases) et téléchargez `recettor_1.0.0_amd64.deb`.

### 2. Installer

```bash
# Via l'interface graphique
# Double-cliquez sur le fichier .deb dans votre gestionnaire de fichiers

# Ou en ligne de commande
sudo dpkg -i recettor_1.0.0_amd64.deb

# Résoudre les dépendances si nécessaire
sudo apt-get install -f
```

> ⏳ L'installation crée un environnement virtuel Python et installe les dépendances — comptez 1 à 2 minutes.

### 3. Lancer l'application

```bash
# Depuis le terminal
recettor

# Ou depuis le menu Applications de votre bureau (section Utilitaires)
```

### 4. Désinstaller

```bash
# Désinstaller (conserve vos données dans /opt/recettor/data)
sudo apt remove recettor

# Désinstaller et supprimer toutes les données
sudo apt purge recettor
```

---

## 🐍 Installation manuelle (depuis les sources)

> Pour tous les systèmes avec Python 3.8+

### Prérequis système

```bash
# Debian / Ubuntu
sudo apt install python3 python3-pip python3-venv libxcb-xinerama0

# Fedora / RHEL
sudo dnf install python3 python3-pip python3-virtualenv

# Arch Linux
sudo pacman -S python python-pip
```

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/nouhailler/recettor.git
cd recettor

# 2. Créer l'environnement virtuel
python3 -m venv venv

# 3. Activer l'environnement virtuel
source venv/bin/activate          # Linux / macOS
# ou
venv\Scripts\activate             # Windows

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Lancer Recettor
python main.py
```

---

## 🪟 Installation sur Windows

```powershell
# 1. Installer Python 3.8+ depuis https://python.org
# 2. Ouvrir PowerShell dans le dossier du projet

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

---

## 🍎 Installation sur macOS

```bash
# Avec Homebrew
brew install python@3.11

# Puis
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## 🗄️ Données et sauvegarde

| Élément | Emplacement |
|---|---|
| Base de données | `/opt/recettor/data/recettes.db` (paquet .deb) ou `data/recettes.db` (sources) |
| Photos des recettes | `/opt/recettor/assets/images/` |
| Sauvegardes | `/opt/recettor/data/backups/` |

**Sauvegarder vos recettes :**

```bash
# Via l'application : Fichier → Sauvegarder la base
# Ou manuellement
cp /opt/recettor/data/recettes.db ~/recettor_backup_$(date +%Y%m%d).db
```

**Exporter toutes vos recettes au format JSON :**

Depuis l'application : **Outils → Exporter toutes les recettes (JSON)**

---

## 🆘 Résolution de problèmes

### L'application ne démarre pas

```bash
# Vérifier les logs
recettor 2>&1 | head -30

# Vérifier que PyQt5 est bien installé
/opt/recettor/venv/bin/python -c "import PyQt5; print('OK')"

# Réinstaller les dépendances
/opt/recettor/venv/bin/pip install -r /opt/recettor/requirements.txt
```

### Erreur `xcb` au démarrage (Linux)

```bash
sudo apt install libxcb-xinerama0 libxcb1 libx11-6 libxkbcommon-x11-0
```

### Erreur de permissions sur la base de données

```bash
sudo chmod -R 777 /opt/recettor/data
```

---

## 📬 Support

- **Issues & bugs :** [GitHub Issues](https://github.com/nouhailler/recettor/issues)
- **Documentation :** appuyez sur `F1` dans l'application pour ouvrir l'aide complète
