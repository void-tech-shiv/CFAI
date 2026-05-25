# AI-Based Tourist Route Planner

An intelligent, multi-objective desktop route planning application built for tourists exploring the **Rajasthan Heritage Circuit**. 
This project integrates advanced Artificial Intelligence paradigms to solve routing problems, plan itineraries under budget constraints, model weather and traffic uncertainty using Bayesian/Markovian updates, and make decisions using Multi-Attribute Utility Theory (MAUT).

Designed specifically as a professional, beginner-friendly, and high-scoring submission for **B.Tech Computer Science / AI & DS Mini-Project and Viva**.

---

## 🌟 Key Features

1. **State-Space Modeling**: Represents 15 historical Rajasthan cities as coordinate-mapped nodes, with physical roads represented as weighted edges with dynamic environmental distributions.
2. **AI Search Algorithms**: Fully modular implementations of **Breadth-First Search (BFS)**, **Depth-First Search (DFS)**, **Uniform Cost Search (UCS)**, and **A* Search** using admissible Euclidean/Manhattan distance heuristics.
3. **Multi-Stop Itinerary CSP Solver**: Backtracking solver utilizing **MRV (Minimum Remaining Values)** and **LCV (Least Constraining Value)** heuristics to plan custom trips satisfying budget limits, schedule limits, crowd tolerances, and site open operational states.
4. **Bayesian Weather Updates**: Adjusts highway traffic probabilities dynamically under severe weather warnings (Rain/Fog) using Bayes' Theorem.
5. **Markov Chain Traffic Predictor**: Simulates hourly traffic state updates along highways using a memoryless state transition probability matrix.
6. **Premium Dark-Mode GUI**: CustomTkinter desktop interface featuring real-time Matplotlib route plots, comparative speed performance bar charts, hotel recommendations, and logged previous searches.
7. **Offline TTS Voice Guidance**: Non-blocking background thread Text-to-Speech synthesis that reads aloud computed travel routing summaries.
8. **Multi-Format Export**: Generates travel brochures in styled HTML format, standard professional PDFs (via ReportLab), or plain text format offline.

---

## 📁 Directory Structure

```text
tourist_route_planner/
│
├── main.py                     # Entry point for executing the desktop application
├── requirements.txt            # Required python packages list
├── README.md                   # This instruction manual
│
├── datasets/
│   ├── locations.json          # Offline database for 15+ locations, paths, hotels, coordinates
│   └── users.json              # Local encrypted registry for user profiles and history logs
│
├── models/
│   ├── __init__.py
│   ├── user.py                 # Handles OOP user registering, login validation, and logs
│   └── location.py             # Parses JSON and constructs graph models
│
├── algorithms/
│   ├── __init__.py
│   ├── search.py               # BFS, DFS, UCS, A* Search implementations
│   ├── csp.py                  # Itinerary CSP Backtracking (MRV + LCV)
│   ├── decision.py             # Multi-Attribute Utility (MAUT) normalizer and ranker
│   └── uncertainty.py          # Bayesian and Markov uncertainty calculations
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py              # Exporter module for HTML, PDF, or Text documents
│   └── voice.py                # Threaded Text-to-Speech voice guidance
│
├── gui/
│   ├── __init__.py
│   ├── app.py                  # Main window shell with theme segmented tab controllers
│   ├── auth_frame.py           # Onboarding sign-in/registration panels
│   ├── dashboard_frame.py      # Map renderer dropdowns, inputs, result logs, and hotel boxes
│   └── stats_frame.py          # Comparative Matplotlib speed graphs
│
└── reports/
    └── documentation.md        # Comprehensive academic report, PPT slides, and 30+ Viva Q&A
```

---

## 🚀 Rapid Setup & Run Guide

### 1. Prerequisites
Ensure you have Python 3.9, 3.10, or 3.11 installed. You can verify this by running:
```bash
python --version
```

### 2. Download and Extract
Unzip the source folder containing the files to your local workspace.

### 3. Install Required Dependencies
Open a terminal (Command Prompt or PowerShell on Windows) in the root folder and run:
```bash
pip install -r requirements.txt
```

### 4. Execute the Application
Run the primary execution script:
```bash
python main.py
```

---

## 📚 Academic Submission Assets
Inside the [reports/documentation.md](file:///d:/HONORS%20CLASS/term3/CFAI/pg%20byme/reports/documentation.md) folder, you will find extremely rich deliverables to assist with your B.Tech evaluation:
1. **Full Written Report**: Complete with Problem Statements, Literature Survey table, and Methodology.
2. **Mathematical Equations**: Detailed descriptions of heuristic scaling, Bayesian models, and Markov transition matrices.
3. **PowerPoint PPT Template Outline**: Organized structure for your slides.
4. **30+ Viva Q&A Preparation Sheet**: Standard and advanced questions commonly asked by external examiners regarding search spaces, CSP heuristics, Bayes' Theorem, and system engineering.

---

*Enjoy exploring the Rajasthan Heritage Circuit with AI guidance! Safe Travels!*
