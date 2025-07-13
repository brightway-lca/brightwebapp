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

`brightwebapp` is a Python package that provides a framework for building complex life-cycle assessment (LCA) and supply chain analysis applications that run in the browser using WebAssembly (WASM). It leverages the [Brightway](https://brightway.dev) LCA framework and the [Holoviz Panel](https://panel.holoviz.org) library to create interactive web applications. The package is designed as a template for developers to create their own LCA and supply chain analysis applications, with a focus on ease of use and flexibility.

# Statement of Need

The Brightway framework [@Mutel2017] is a powerful tool for life-cycle assessment and supply chain analysis, but it traditionally requires a local Python environment to run. On the one hand, this can be a barrier for users who are not familiar with Python or do not have the necessary environment set up. On the other hand, it means that web applications and interactive dashboards using Brightway as their computational core require a server backend to run the Brightway framework, which can be complex to set up and maintain. A recent example is the `carculator` application [@sacchi2022and], which assesses the environmental impact of automobiles.`brightwebapp` addresses this issue by allowing users to run LCA and supply chain analysis applications directly in their web browser, without the need for a local installation.

# Brightway and WebAssembly

# Interactive Web Application

The package documentation allows users to compute fuel burn directly in the browser, without the need to install the package locally. This is achieved through the use of a [Pyodide](https://pyodide.org/en/stable/) Web Assembly Python kernel. The interactive documentation is available at [jetfuelburn.readthedocs.io](https://jetfuelburn.readthedocs.io).

# Acknowledgements

This work has been supported by the Swiss Innovation Agency Innosuisse in the context of the WISER flagship project (PFFS-21-72). In addition, Michael P. Weinold gratefully acknowledges the support of the Swiss Study Foundation.

# References