#!/usr/bin/env python3
"""
Document Analyzer - Pipeline complet d'analyse de documents scientifiques

Ce script implémente le workflow complet :
1. Lecture multi-format (PDF, DOCX, XLSX, PPTX)
2. Extraction de structure et contenu
3. Identification résultats majeurs et conclusions
4. Extraction figures et tableaux clés
5. Génération résumé exécutif
6. Création mindmap Mermaid
7. Compilation rapport Markdown

Auteur: Marc Garel - MIO/OSU Marseille
Version: 1.0
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Imports conditionnels avec gestion d'erreur
try:
    import pdfplumber
    import fitz  # PyMuPDF
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("Warning: PDF libraries not available. Install with: pip install pdfplumber PyMuPDF")

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    print("Warning: python-docx not available. Install with: pip install python-docx")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Warning: pandas not available. Install with: pip install pandas openpyxl")

try:
    from pptx import Presentation
    HAS_PPTX = True
except ImportError:
    HAS_PPTX = False
    print("Warning: python-pptx not available. Install with: pip install python-pptx")

try:
    from PIL import Image
    import io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: Pillow not available. Install with: pip install Pillow")


class DocumentAnalyzer:
    """Analyseur de documents scientifiques multi-format."""
    
    def __init__(self, output_dir: str = "./document_analysis"):
        """Initialiser l'analyseur.
        
        Args:
            output_dir: Répertoire de sortie pour l'analyse
        """
        self.output_dir = Path(output_dir)
        self.figures_dir = self.output_dir / "figures"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        
        self.document_meta = {
            "title": "",
            "authors": [],
            "sections": {},
            "figures": [],
            "tables": [],
            "key_findings": [],
            "conclusions": []
        }
    
    def analyze(self, file_path: str) -> str:
        """Point d'entrée principal pour analyser un document.
        
        Args:
            file_path: Chemin vers le document à analyser
            
        Returns:
            Chemin vers le rapport Markdown généré
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {file_path}")
        
        ext = file_path.suffix.lower()
        
        print(f"📄 Analyse de {file_path.name} ({ext})...")
        
        # Analyser selon le format
        if ext == '.pdf':
            self._analyze_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            self._analyze_docx(file_path)
        elif ext in ['.xlsx', '.xls']:
            self._analyze_xlsx(file_path)
        elif ext in ['.pptx', '.ppt']:
            self._analyze_pptx(file_path)
        else:
            raise ValueError(f"Format non supporté : {ext}")
        
        # Générer le rapport
        report_path = self._generate_report()
        
        print(f"✅ Analyse terminée : {report_path}")
        return str(report_path)
    
    def _analyze_pdf(self, file_path: Path):
        """Analyser un fichier PDF."""
        if not HAS_PDF:
            raise ImportError("PDF libraries not installed")
        
        print("  📖 Extraction du texte...")
        with pdfplumber.open(file_path) as pdf:
            # Extraire le texte complet
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n\n"
            
            # Extraire les tableaux
            print("  📊 Extraction des tableaux...")
            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                for table_idx, table in enumerate(tables):
                    if table and len(table) > 1:
                        self.document_meta["tables"].append({
                            "page": page_num,
                            "index": table_idx,
                            "data": table
                        })
        
        # Extraire les images
        print("  🖼️  Extraction des figures...")
        self._extract_pdf_images(file_path)
        
        # Analyser la structure du texte
        self._extract_structure(full_text)
        
        # Extraire résultats et conclusions
        self._extract_findings_and_conclusions()
    
    def _extract_pdf_images(self, file_path: Path):
        """Extraire les images importantes d'un PDF."""
        if not HAS_PIL:
            print("    ⚠️  PIL non disponible, extraction d'images ignorée")
            return
        
        doc = fitz.open(file_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Filtrer par taille
                    img_pil = Image.open(io.BytesIO(image_bytes))
                    width, height = img_pil.size
                    
                    # Ne garder que les images significatives
                    if width > 300 and height > 200:
                        img_filename = f"figure_p{page_num+1}_{img_index+1}.png"
                        img_path = self.figures_dir / img_filename
                        img_pil.save(img_path)
                        
                        self.document_meta["figures"].append({
                            "filename": img_filename,
                            "page": page_num + 1,
                            "size": (width, height),
                            "path": str(img_path)
                        })
                        print(f"    ✓ Figure extraite : {img_filename}")
                except Exception as e:
                    print(f"    ⚠️  Erreur extraction image {img_index}: {e}")
        
        doc.close()
    
    def _analyze_docx(self, file_path: Path):
        """Analyser un fichier DOCX."""
        if not HAS_DOCX:
            raise ImportError("python-docx not installed")
        
        print("  📖 Lecture du document Word...")
        doc = Document(file_path)
        
        # Extraire le texte
        full_text = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        
        # Analyser la structure
        self._extract_structure(full_text)
        self._extract_findings_and_conclusions()
    
    def _analyze_xlsx(self, file_path: Path):
        """Analyser un fichier XLSX."""
        if not HAS_PANDAS:
            raise ImportError("pandas not installed")
        
        print("  📊 Lecture du fichier Excel...")
        xl_file = pd.ExcelFile(file_path)
        
        for sheet_name in xl_file.sheet_names:
            df = xl_file.parse(sheet_name)
            
            # Convertir en tableau Markdown
            table_md = df.to_markdown(index=False)
            
            self.document_meta["tables"].append({
                "sheet": sheet_name,
                "data": table_md,
                "shape": df.shape
            })
            print(f"    ✓ Feuille analysée : {sheet_name} ({df.shape[0]} lignes)")
    
    def _analyze_pptx(self, file_path: Path):
        """Analyser un fichier PPTX."""
        if not HAS_PPTX:
            raise ImportError("python-pptx not installed")
        
        print("  📊 Lecture de la présentation...")
        prs = Presentation(file_path)
        
        full_text = []
        for slide_num, slide in enumerate(prs.slides, 1):
            slide_text = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text.append(shape.text)
            
            if slide_text:
                full_text.append(f"--- Slide {slide_num} ---\n" + "\n".join(slide_text))
        
        text_content = "\n\n".join(full_text)
        self._extract_structure(text_content)
        self._extract_findings_and_conclusions()
    
    def _extract_structure(self, text: str):
        """Extraire la structure du document."""
        print("  🔍 Analyse de la structure...")
        
        # Patterns pour les sections communes
        section_patterns = {
            "Abstract": r"(?i)(abstract|résumé|summary)",
            "Introduction": r"(?i)(introduction|contexte)",
            "Methods": r"(?i)(methods?|methodology|matériel|protocole)",
            "Results": r"(?i)(results?|résultats|findings|observations)",
            "Discussion": r"(?i)(discussion|interprétation)",
            "Conclusion": r"(?i)(conclusion|perspectives)"
        }
        
        # Extraire le titre (première ligne significative)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            self.document_meta["title"] = lines[0][:100]  # Limiter à 100 chars
        
        # Découper en sections
        current_section = "Introduction"
        current_text = []
        
        for line in lines:
            # Chercher si la ligne est un titre de section
            is_section = False
            for section_name, pattern in section_patterns.items():
                if re.match(pattern, line.strip()) and len(line.strip()) < 50:
                    # Sauvegarder la section précédente
                    if current_text:
                        self.document_meta["sections"][current_section] = "\n".join(current_text)
                    # Nouvelle section
                    current_section = section_name
                    current_text = []
                    is_section = True
                    break
            
            if not is_section:
                current_text.append(line)
        
        # Dernière section
        if current_text:
            self.document_meta["sections"][current_section] = "\n".join(current_text)
        
        print(f"    ✓ {len(self.document_meta['sections'])} sections identifiées")
    
    def _extract_findings_and_conclusions(self):
        """Extraire résultats majeurs et conclusions."""
        print("  💡 Extraction des résultats et conclusions...")
        
        # Résultats
        results_text = self.document_meta["sections"].get("Results", "")
        if results_text:
            self.document_meta["key_findings"] = self._find_key_results(results_text)
        
        # Conclusions
        conclusion_text = self.document_meta["sections"].get("Conclusion", "")
        if conclusion_text:
            self.document_meta["conclusions"] = self._extract_key_points(conclusion_text, n=5)
        
        print(f"    ✓ {len(self.document_meta['key_findings'])} résultats identifiés")
        print(f"    ✓ {len(self.document_meta['conclusions'])} conclusions identifiées")
    
    def _find_key_results(self, text: str) -> List[str]:
        """Identifier les résultats quantitatifs clés."""
        findings = []
        
        # Patterns de résultats
        patterns = [
            (r'(p\s*[<>=]\s*0\.\d+)', "Statistique"),
            (r'(\d+\.?\d*\s*%)', "Pourcentage"),
            (r'(r\s*=\s*0\.\d+)', "Corrélation"),
            (r'(significantly?\s+(?:increased|decreased|higher|lower))', "Différence significative"),
        ]
        
        for pattern, category in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extraire le contexte (phrase complète)
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                
                # Nettoyer et ajouter
                if context and len(context) > 20:
                    findings.append(context[:200])  # Limiter à 200 chars
        
        # Dédupliquer et limiter
        unique_findings = list(set(findings))[:10]
        return unique_findings
    
    def _extract_key_points(self, text: str, n: int = 5) -> List[str]:
        """Extraire les points clés d'un texte."""
        sentences = re.split(r'[.!?]\s+', text)
        
        # Filtrer les phrases courtes et vides
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
        
        # Prendre les N premières
        return meaningful_sentences[:n]
    
    def _generate_executive_summary(self) -> str:
        """Générer le résumé exécutif."""
        sections = self.document_meta["sections"]
        
        # Contexte (de l'abstract ou introduction)
        context = sections.get("Abstract", sections.get("Introduction", ""))
        context_summary = " ".join(self._extract_key_points(context, n=2))
        
        # Objectif (première phrase de l'introduction)
        intro_sentences = self._extract_key_points(sections.get("Introduction", ""), n=1)
        objective = intro_sentences[0] if intro_sentences else "Non spécifié"
        
        # Méthodologie
        methods = sections.get("Methods", "")
        methods_summary = " ".join(self._extract_key_points(methods, n=2))
        
        # Résultats principaux
        findings = self.document_meta["key_findings"][:3]
        
        # Conclusion
        conclusions = self.document_meta["conclusions"][:1]
        conclusion_text = conclusions[0] if conclusions else "Non spécifiée"
        
        summary = f"""## 📋 Résumé Exécutif

**Contexte** : {context_summary[:250]}

**Objectif** : {objective[:200]}

**Méthodologie** : {methods_summary[:200]}

**Résultats Principaux** :
"""
        
        for i, finding in enumerate(findings, 1):
            summary += f"{i}. {finding}\n"
        
        summary += f"\n**Conclusion** : {conclusion_text[:200]}\n"
        
        return summary
    
    def _generate_mindmap(self) -> str:
        """Générer une mindmap Mermaid conceptuelle."""
        sections = self.document_meta["sections"]
        title = self.document_meta["title"] or "Étude scientifique"
        
        # Limiter le titre à 50 chars pour la mindmap
        title_short = title[:50]
        
        mindmap = "```mermaid\nmindmap\n"
        mindmap += f"  root(({title_short}))\n"
        
        # Branche Contexte
        if "Abstract" in sections or "Introduction" in sections:
            mindmap += "    Contexte\n"
            context_points = self._extract_key_points(
                sections.get("Abstract", sections.get("Introduction", "")), n=2
            )
            for point in context_points:
                point_short = point[:60].replace('\n', ' ')
                mindmap += f"      {point_short}\n"
        
        # Branche Méthodologie
        if "Methods" in sections:
            mindmap += "    Méthodologie\n"
            method_points = self._extract_key_points(sections["Methods"], n=3)
            for point in method_points:
                point_short = point[:60].replace('\n', ' ')
                mindmap += f"      {point_short}\n"
        
        # Branche Résultats
        if self.document_meta["key_findings"]:
            mindmap += "    Résultats\n"
            for finding in self.document_meta["key_findings"][:5]:
                finding_short = finding[:60].replace('\n', ' ')
                mindmap += f"      {finding_short}\n"
        
        # Branche Conclusions
        if self.document_meta["conclusions"]:
            mindmap += "    Conclusions\n"
            for conclusion in self.document_meta["conclusions"][:3]:
                conclusion_short = conclusion[:60].replace('\n', ' ')
                mindmap += f"      {conclusion_short}\n"
        
        mindmap += "```\n"
        return mindmap
    
    def _generate_report(self) -> Path:
        """Générer le rapport Markdown complet."""
        print("  📝 Génération du rapport...")
        
        report = f"""# Analyse : {self.document_meta['title']}

**Date d'analyse** : {datetime.now().strftime('%d/%m/%Y')}  
**Sections identifiées** : {len(self.document_meta['sections'])}  
**Figures extraites** : {len(self.document_meta['figures'])}  
**Tableaux extraits** : {len(self.document_meta['tables'])}

---

"""
        
        # Résumé exécutif
        report += self._generate_executive_summary()
        report += "\n---\n\n"
        
        # Résultats majeurs
        if self.document_meta["key_findings"]:
            report += "## 🔬 Résultats Majeurs\n\n"
            for i, finding in enumerate(self.document_meta["key_findings"], 1):
                report += f"{i}. {finding}\n\n"
            report += "---\n\n"
        
        # Conclusions principales
        if self.document_meta["conclusions"]:
            report += "## 💡 Conclusions Principales\n\n"
            for i, conclusion in enumerate(self.document_meta["conclusions"], 1):
                report += f"{i}. {conclusion}\n\n"
            report += "---\n\n"
        
        # Figures clés
        if self.document_meta["figures"]:
            report += "## 📊 Figures Clés\n\n"
            for i, fig in enumerate(self.document_meta["figures"], 1):
                report += f"### Figure {i}\n"
                report += f"![Figure {i}](./figures/{fig['filename']})\n\n"
                report += f"**Page** : {fig['page']} | **Dimensions** : {fig['size'][0]}x{fig['size'][1]} px\n\n"
            report += "---\n\n"
        
        # Tableaux
        if self.document_meta["tables"]:
            report += "## 📋 Tableaux\n\n"
            for i, table in enumerate(self.document_meta["tables"][:3], 1):  # Limiter à 3
                if "sheet" in table:
                    report += f"### Tableau {i} : {table['sheet']}\n\n"
                    report += table["data"] + "\n\n"
                else:
                    report += f"### Tableau {i} (Page {table['page']})\n\n"
                    # Convertir en Markdown
                    if table["data"]:
                        header = " | ".join(str(cell) for cell in table["data"][0])
                        separator = " | ".join(["---"] * len(table["data"][0]))
                        report += f"| {header} |\n| {separator} |\n"
                        for row in table["data"][1:4]:  # Limiter à 3 lignes
                            row_str = " | ".join(str(cell) for cell in row)
                            report += f"| {row_str} |\n"
                        report += "\n"
            report += "---\n\n"
        
        # Mindmap conceptuelle
        report += "## 🗺️ Mindmap Conceptuelle\n\n"
        report += self._generate_mindmap()
        report += "\n---\n\n"
        
        # Footer
        report += "*Analyse générée automatiquement par Document Analyzer*\n"
        
        # Sauvegarder
        report_path = self.output_dir / "analyse_document.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report_path


def main():
    """Point d'entrée CLI."""
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <chemin_document> [dossier_sortie]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./document_analysis"
    
    analyzer = DocumentAnalyzer(output_dir=output_dir)
    
    try:
        report_path = analyzer.analyze(file_path)
        print(f"\n✅ Analyse terminée avec succès !")
        print(f"📄 Rapport : {report_path}")
        print(f"🖼️  Figures : {analyzer.figures_dir}")
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
