---
title: 'BrightWebApp: A Framework for Complex Life-Cycle Assessment and Supply Chain Analysis in the Browser with WebAssembly and Brightway'
tags:
  - Python
  - life-cycle assessment
  - supply chain analysis
  - web assembly
  - WASM
  - Pyodide
  - Holoviz Panel
authors:
  - name: Michael P. Weinold
    orcid: 0000-0003-4859-2650
    equal-contrib: false
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Christopher Mutel
    equal-contrib: false # (This is how you can denote equal contributions between multiple authors)
    orcid: 0000-0002-7898-9862
    affiliation: "3"
affiliations:
 - name: Laboratory for Energy Systems Analysis, PSI Centers for Nuclear Engineering \& Sciences and Energy \& Environmental Sciences, Villigen, Switzerland
   index: 1
 - name: Chair of Energy Systems Analysis, Institute of Energy and Process Engineering, Department of Mechanical and Process Engineering, ETH Zurich, Zurich, Switzerland
   index: 2
 - name: Départ de Sentier (DdS) Non-Profit Association, Riniken, Switzerland
   index: 3
date: 01 July 2025
bibliography: paper.bib

---

# Summary

`brightwebapp` is a Python package that provides a framework for building complex life-cycle assessment (LCA) and supply chain analysis applications that run in the browser using WebAssembly (WASM). It leverages the [Brightway](https://brightway.dev) LCA framework and the [Holoviz Panel](https://panel.holoviz.org) library to create interactive web applications. The package is designed as a template for developers to create their own LCA applications, with a focus on ease of use and flexibility.

# Statement of Need

The Brightway framework [@Mutel2017] is a powerful tool for life-cycle assessment and supply chain analysis. However, it traditionally requires a local Python environment, which poses a challenge for web applications and interactive dashboards. These applications must either use a complex server backend to run the framework or rely on serving static, pre-computed data to users. A recent example of this is the carculator application [@sacchi2022and], which assesses the environmental impact of automobiles.
`brightwebapp` addresses this issue by allowing users to run LCA and supply chain analysis applications directly in their web browser, eliminating the need for a local installation. This grants users the flexibility to directly explore the impact of different LCA parameters.

# Brightway and WebAssembly

In developing `brightwebapp`, all Brightway dependencies were made compatible with Pyodide, either by replacing them with pure Python implementations or with packages included in the Pyodide distribution. This ensures that the Brightway framework can run efficiently in the browser without requiring any additional server-side components.

# Template for Web Applications

`brightwebapp` provides a template for building Holoviz Panel web applications and dashboards that run the Brightway framework in the browser using WebAssembly. To achieve this, it uses [Pyodide](https://pyodide.org/en/stable/), a Python distribution for the browser and Node.js that allows running Python code in the browser. The implemented example application demonstrates how to use the Brightway framework to perform a supply chain analysis of a sector in the USEEIO database [@yang2017useeio].

# Acknowledgements

This work has been supported by the Swiss Innovation Agency Innosuisse in the context of the WISER flagship project (PFFS-21-72). In addition, Michael P. Weinold gratefully acknowledges the support of the Swiss Study Foundation.

# References