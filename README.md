# Cars vs Police

Un jeu de poursuites automobiles en 3D où tu dois survivre aux attaques des policiers !

## 🎮 Gameplay

- Tu pilotes une **voiture jaune** sur une map avec des routes
- **4 voitures de police bleues** essaient de t'écraser
- Tu as **3 vies** - chaque collision avec un policier te coûte 1 vie
- Quand tu perds tes 3 vies, c'est GAME OVER !

## 🎯 Objectif

**Survive le plus longtemps possible** en évitant les voitures de police !

## 🕹️ Contrôles

| Touche | Action |
|--------|--------|
| **W** | Accélérer |
| **S** | Freiner |
| **A** | Tourner à gauche |
| **D** | Tourner à droite |
| **R** | Relancer le jeu (après GAME OVER) |

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## ▶️ Lancer le jeu

```bash
python cars_vs_police.py
```

## 🎨 Caractéristiques

- ✅ Map 3D avec routes principales et secondaires
- ✅ Voiture du joueur contrôlable (jaune)
- ✅ 4 IA policiers (bleues) avec détection du joueur
- ✅ Système de collision et de vies (3 lives)
- ✅ Caméra suivant le joueur
- ✅ HUD affichant les vies restantes

## 📝 Notes

- Les limites de la map t'empêchent de sortir de l'aire de jeu
- Les policiers utilisent une IA simple qui te poursuit directement
- Le cooldown de collision empêche les dégâts trop rapides
- Appuie sur R après la défaite pour relancer

## 🔧 Technologies

- **Pygame** - Framework de jeu
- **PyOpenGL** - Rendu 3D avec OpenGL
- **NumPy** - Calculs mathématiques
