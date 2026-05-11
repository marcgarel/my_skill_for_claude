# 🚀 Quick Start - Document Analyzer

Guide rapide pour commencer à utiliser votre nouveau skill d'analyse de documents.

---

## ⚡ Démarrage en 30 secondes

### 1. Vérifier que le skill est actif

Le skill est déjà installé dans `~/.claude/skills/doc-analyzer/`. Claude le chargera automatiquement lors de vos prochaines conversations.

### 2. Premier test simple

**Uploadez** un document PDF, DOCX, XLSX ou PPTX dans Claude.ai

**Tapez** :
```
Analyse ce document et donne-moi un résumé exécutif avec les résultats principaux
```

**Résultat attendu** : Claude va créer un fichier `analyse_document.md` avec :
- ✅ Résumé exécutif structuré
- ✅ Résultats majeurs extraits
- ✅ Conclusions principales
- ✅ Figures sauvegardées dans `./figures/`
- ✅ Mindmap Mermaid de synthèse

---

## 📝 Exemples de commandes

### Analyse complète
```
"Fais une analyse complète de cet article scientifique"
```

### Extraction ciblée
```
"Extrais uniquement les figures de résultats de ce PDF"
```

### Mindmap uniquement
```
"Crée une mindmap conceptuelle de ce document"
```

### Résultats quantitatifs
```
"Extrais toutes les valeurs statistiques significatives (p-values, corrélations)"
```

### Comparaison
```
"Analyse ces deux articles et compare leurs méthodologies"
```

---

## 🎯 Déclencheurs automatiques

Le skill se charge automatiquement quand vous utilisez :

| Mot-clé | Action |
|---------|--------|
| "analyse ce document" | Analyse complète |
| "résume cet article" | Résumé exécutif |
| "extrais les résultats" | Résultats majeurs |
| "crée une mindmap" | Mindmap Mermaid |
| "extrais les figures" | Figures importantes |
| "fais une synthèse" | Synthèse structurée |

---

## 📊 Types de documents supportés

| Format | Extension | Support |
|--------|-----------|---------|
| PDF | `.pdf` | ✅ Complet |
| Word | `.docx`, `.doc` | ✅ Complet |
| Excel | `.xlsx`, `.xls` | ✅ Tableaux |
| PowerPoint | `.pptx`, `.ppt` | ✅ Texte + Images |
| Pages | `.pages` | 🔄 Via conversion |
| Numbers | `.numbers` | 🔄 Via conversion |
| Keynote | `.key` | 🔄 Via conversion |

---

## 💻 Utilisation en ligne de commande

Si vous voulez utiliser le script Python directement :

### Installation dépendances

```bash
pip install pdfplumber PyMuPDF python-docx pandas openpyxl python-pptx Pillow --break-system-packages
```

### Exécution

```bash
python ~/.claude/skills/doc-analyzer/scripts/analyzer.py document.pdf ./output
```

**Sortie** :
```
./output/
├── analyse_document.md    # Rapport complet
└── figures/
    ├── figure_p3_1.png
    ├── figure_p5_2.png
    └── ...
```

---

## 🔍 Exemple de cas d'usage réel

### Scénario : Analyser un article de métabarcoding

**Document** : Article scientifique sur la diversité microbienne des grands fonds (PDF, 15 pages)

**Commande** :
```
Analyse cet article sur le métabarcoding des archaea et extrais les résultats de diversité avec les statistiques
```

**Claude va** :
1. ✅ Lire le PDF avec pdfplumber
2. ✅ Identifier les sections (Abstract, Methods, Results, Discussion)
3. ✅ Extraire les métriques de diversité alpha/beta
4. ✅ Identifier les p-values des tests PERMANOVA
5. ✅ Sauvegarder les figures (PCoA plots, barplots)
6. ✅ Générer un résumé exécutif en français
7. ✅ Créer une mindmap conceptuelle
8. ✅ Compiler tout dans `analyse_document.md`

**Temps** : ~30 secondes à 1 minute selon la taille du document

---

## ✨ Conseils pour de meilleurs résultats

### ✅ À faire

- Utiliser des **PDFs natifs** (non scannés)
- Documents **bien structurés** avec sections claires
- Fichiers **< 50 pages** pour performance optimale
- **Nommer clairement** votre demande

### ❌ À éviter

- PDFs scannés sans OCR (résultats limités)
- Documents sans structure (texte libre)
- Fichiers trop volumineux (> 100 Mo)
- Demandes trop vagues

---

## 🎨 Personnalisation rapide

### Changer le nombre de résultats extraits

Éditez `~/.claude/skills/doc-analyzer/SKILL.md` et modifiez :
```markdown
unique_findings = list(set(findings))[:10]  # Modifier 10 → 20
```

### Adapter les seuils de figures

```markdown
if width > 300 and height > 200:  # Modifier 300x200 → vos valeurs
```

### Modifier le template de sortie

Le rapport est généré dans la méthode `_generate_report()` du script `analyzer.py`.

---

## 🐛 Dépannage express

### ❌ "PDF libraries not available"
**Solution** :
```bash
pip install pdfplumber PyMuPDF --break-system-packages
```

### ❌ Les figures ne s'extraient pas
**Causes possibles** :
- PDF scanné (besoin OCR)
- Images trop petites (< 300x200 px)
- Format non compatible

**Solution** : Vérifier le format du document ou ajuster les seuils

### ❌ Le résumé est vide
**Cause** : Document mal structuré ou sans sections identifiables

**Solution** : Utiliser un article scientifique avec structure standard (Abstract, Methods, Results)

---

## 📚 Ressources

- **Documentation complète** : `~/.claude/skills/doc-analyzer/README.md`
- **Code source** : `~/.claude/skills/doc-analyzer/scripts/analyzer.py`
- **Tests** : `~/.claude/skills/doc-analyzer/test_cases.json`
- **Récapitulatif** : `~/.claude/skills/doc-analyzer/CREATION_SUMMARY.md`

---

## 🎓 Aller plus loin

### Combiner avec d'autres skills

```
"Analyse cet article et crée une présentation Quarto des résultats"
```
→ Utilise doc-analyzer + quarto

### Analyses comparatives

```
"Analyse ces 3 articles et crée un tableau comparatif des méthodologies"
```

### Extraction pour publication

```
"Extrais les figures et tableaux principaux pour mon article de synthèse"
```

---

## ✅ Checklist de vérification

Avant de commencer, vérifiez :

- [ ] Le skill est dans `~/.claude/skills/doc-analyzer/`
- [ ] Vous avez un document scientifique à analyser
- [ ] Le document est au format PDF, DOCX, XLSX ou PPTX
- [ ] Vous savez quelles informations vous cherchez

**Vous êtes prêt !** 🚀

---

**Dernière mise à jour** : 22/04/2024  
**Version du skill** : 1.0  
**Auteur** : Marc Garel - MIO/OSU Marseille
