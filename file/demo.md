# RareNav — User Guide

**Rare Disease AI Navigator** · Powered by MedGemma (Google HAI-DEF) · ClinVar 5M+ variants · HPO Phenotype Ontology

---

## What is RareNav?

RareNav is an AI-powered clinical support tool designed to help **patients, families, and clinicians** navigate the complex landscape of rare genetic diseases. It combines Google's MedGemma multimodal language model with real-world clinical databases (ClinVar, HPO) to provide instant, evidence-based answers about genetic variants, rare disease diagnosis, and clinical management.

> ⚠️ **Important:** RareNav is a research and educational tool. It is not a medical device and does not replace professional medical advice. Always consult qualified healthcare professionals for clinical decisions.

---

## Quick Start

### 1. Launch the application

```bash
cd rarenav
python app.py
```

Then open your browser at **http://localhost:5000**

### 2. Choose your entry point

RareNav offers three ways to get started:

| Entry | Who it's for | How to use |
|-------|-------------|------------|
| **AI Assistant** | Everyone | Type your question or upload a genetic report |
| **Variant Database** | Patients with reports, Clinicians | Search by gene name (e.g. HFE, CFTR, BRCA1) |
| **Disease Library** | Patients exploring symptoms, Students | Browse or search by disease name, gene, or symptom |

---

## Core Features

### 💬 AI Assistant (Chat)

The main interface. Ask anything in plain language:

- *"What does it mean if my BRCA1 variant is Pathogenic?"*
- *"My child has seizures and muscle weakness — what rare diseases should we consider?"*
- *"Is Marfan syndrome hereditary? What is the risk for my children?"*
- *"What treatments are available for Gaucher disease?"*

**Clinician Mode** — Toggle in the top-right corner. Switches AI responses from plain patient language to clinical terminology with ACMG criteria references, evidence grades, and specialist-level detail.

**Clinical Detail button** — Appears under each AI response. Click to get a clinical-language version of any answer without leaving the conversation.

---

### 📄 Upload Genetic Report (Multimodal AI)

**The most powerful feature.** Upload a genetic test report as a PDF or image file.

1. Click the 📎 button in the chat input bar, or click **Upload Genetic Report** in the left panel
2. Drop your file (PDF, JPG, or PNG — max 10MB)
3. Click **Analyze Report**

MedGemma's vision model reads the report and:
- Extracts all genetic variants mentioned
- Identifies their clinical classification (Pathogenic / VUS / Benign)
- Links variants to associated conditions
- Automatically sets the conversation context so you can ask follow-up questions

*This feature uses MedGemma 4B multimodal — a medically fine-tuned vision-language model from Google. In demo mode, example output is shown.*

---

### 🗄 Variant Database

Search across ClinVar's 5M+ clinical variant submissions in real time.

**How to search:**
1. Go to **Variant Database** in the navigation bar
2. Type a gene name (e.g. `HFE`, `CFTR`, `BRCA1`, `LDLR`)
3. Optionally filter by variant name or clinical significance
4. Click any row to open the detail drawer

**Quick-access gene buttons** are shown above the search bar for the most commonly queried genes.

**Variant detail drawer** shows:
- Full HGVS variant name
- Chromosomal position
- Reference / alternate allele
- ClinVar review status and number of submitters
- Associated phenotypes
- Direct links to ClinVar, PubMed, and ClinicalTrials.gov
- **"Ask AI"** button — jumps to chat with full variant context

**Classification color codes:**

| Color | Meaning |
|-------|---------|
| 🔴 Red | Pathogenic |
| 🟠 Orange | Likely Pathogenic |
| 🟣 Purple | Variant of Uncertain Significance (VUS) |
| 🟢 Green | Benign / Likely Benign |
| ⚫ Gray | Conflicting interpretations |

---

### 📖 Disease Library

Curated profiles for 50+ rare diseases, organized by organ system.

Each disease card includes:
- Gene(s) responsible
- Inheritance pattern and prevalence
- Key clinical features
- Diagnostic approach
- Treatment options
- Recommended specialists
- Links to OMIM, ClinicalTrials.gov, and PubMed

**Click any disease card** to open the full profile, then click **"Ask AI about this"** to jump into a conversation with the disease pre-loaded as context.

---

## Context System

When you click **"Ask AI"** from the Variant Database or Disease Library, RareNav sets an **active context** — visible as a blue bar above the chat input and a panel on the right side of the screen.

The context tells the AI which variant or condition you're focused on, so you can ask natural follow-up questions like *"Is this treatable?"* or *"What should I tell my doctor?"* without repeating all the details.

Click **✕ clear** to remove the context.

---

## Clinician Mode

Designed for healthcare professionals. When enabled:

- AI responses use clinical terminology (ACMG criteria, HGVS notation, evidence grades)
- Variant explanations include PS1/PM2/BA1-style evidence summaries
- Differential diagnosis uses structured clinical reasoning
- Response style matches clinical note / consultation letter format

Toggle with the **👨‍⚕️ Clinician Mode** button in the navigation bar.

---

## Mobile Use

RareNav is fully mobile-responsive. Open **http://[your-server-ip]:5000** on any smartphone or tablet.

On mobile:
- Navigation moves to a bottom tab bar
- Left panel becomes a slide-up drawer (tap the ☰ menu icon)
- Chat fills the full screen
- All features remain accessible

---

## Demo Mode vs Full Mode

| Feature | Demo Mode | Full Mode |
|---------|-----------|-----------|
| AI responses | Pre-written example responses | Live MedGemma 4B inference |
| Variant search | Real ClinVar data ✅ | Real ClinVar data ✅ |
| Disease Library | Full library ✅ | Full library ✅ |
| Report upload | Example extraction | Real MedGemma vision |
| HPO symptom mapping | Built-in 40 terms | Full HPO ontology (13,000+ terms) |

The status indicator in the top-right corner shows the current mode:
- 🟢 **Ready** — MedGemma loaded, full functionality
- 🟡 **Demo mode** — Model not loaded, example responses shown
- ⚫ **Offline** — Cannot reach the server

---

## Data Sources

| Source | Version | Description |
|--------|---------|-------------|
| **ClinVar** | Feb 2026 | NCBI clinical variant archive — 5M+ submissions |
| **HPO** | v2024-01-11 | Human Phenotype Ontology — 13,000+ phenotype terms |
| **MedGemma 4B IT** | Google HAI-DEF | Medically fine-tuned multimodal language model |
| **Disease Library** | Curated | 50+ rare disease profiles with clinical summaries |

---

## Frequently Asked Questions

**Q: Is my data stored anywhere?**
All processing happens on your local server. No data is sent to external services (MedGemma runs locally). Session data is stored in memory only and cleared when the server restarts.

**Q: How accurate is the AI?**
MedGemma is trained on medical literature and is more accurate than general-purpose LLMs for genetics questions. However, AI outputs should always be verified with primary sources and reviewed by qualified clinicians before any medical decision.

**Q: Can I use this for clinical decisions?**
RareNav is a research and educational tool. It is not validated as a clinical decision support system and should not be used as the sole basis for medical decisions.

**Q: What if a variant is not in ClinVar?**
RareNav will fall back to MedGemma's training knowledge and provide an AI-inferred interpretation, clearly labeled as such. For novel variants, consult a clinical geneticist.

**Q: Why is the first startup slow?**
ClinVar's variant_summary.txt (3.8GB) is parsed and indexed on first run, which takes 2–5 minutes. A cache file is saved automatically — subsequent startups load in seconds.

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `Shift + Enter` | New line in message |
| `Escape` | Close any open modal or drawer |

---

## Project Information

**RareNav** was developed for the **MedGemma Impact Challenge** (Google, 2026).

- GitHub: [https://github.com/IveGotMagicBean/RareNav_MedGemma](https://github.com/IveGotMagicBean/RareNav_MedGemma)
- Model: MedGemma 4B IT (google/medgemma-4b-it)
- License: MIT

---

*Last updated: February 2026*
