---
title: 'BrightWebApp: A Framework for Teaching Life-Cycle Assessment and Supply Chain Analysis in the Browser with WebAssembly and Brightway'
tags:
  - Python
  - sustainability
  - environmental impact
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
date: 31 December 2025
bibliography: paper.bib

---

# Summary

`brightwebapp` is a Python software package and web application that demonstrates 
 a framework for building complex life-cycle assessment (LCA) and supply chain analysis applications that run in the browser using WebAssembly (WASM). It leverages the [Brightway](https://brightway.dev) LCA framework and the [Holoviz Panel](https://panel.holoviz.org) [@holoviz_panel] library to create interactive web applications with [Pyodide](https://pyodide.org/en/stable/) [@pyodide].
The package is designed as a template for developers to create their own LCA applications, with a focus on ease of use and flexibility. As a stand-alone web application, it allows users to perform LCA and supply chain analysis of the entire US economy, based on theUSEEIO database [@yang2017useeio] directly in their web browser without the need for a local installation of Python or Brightway. This makes it an ideal tool for teaching and learning about LCA and supply chain analysis in a web-based environment.

# Statement of Need

The Brightway framework [@Mutel2017] is a powerful tool for life-cycle assessment and supply chain analysis. However, it is designed primarily for command-line or local Python environments, which poses a challenge in the educational context and the development of web applications. In life cycle assessment workshops, participants often bring enterprise-managed devices where installing Python packages is restricted, forcing organizers to provision and maintain a Jupyter server and user management services. Similarly, web applications must typically use a complex backend to run the framework or rely on serving static, pre-computed data to users. A recent example of this latter static approach is the carculator application [@sacchi2022and], which assesses the environmental impact of automobiles. BrightWebApp addresses this issue by providing the first template of a WebAssembly-enabled web application for complex life cycle assessment calculations in the browser, eliminating the need for either a local Python environment or a server backend.

# Emission Scope Splitting and Supply Chain Analysis

![Diagram of the example use-case implemented in the BrightWebApp package. Here, every numbered circle represents a production node in the supply chain graph of automotive manufacturing. The supply chain can be split into different levels of "depth". Every node can be assigned to one of three "emission scopes", as defined by the Greenhouse Gas Protocol accounting standard [@bhatia2004greenhouse] \label{fig:scope_splitting}](_media/scope_splitting.pdf){height="5.5cm"}

![Diagram of a single branch in a supply chain tree in the context of the economic analysis implemented in the BrightWebApp. The diagram here shows a final demand of 100\$ worth of the product produced by sector 0. This induces demand for production in sectors upstream 1, which induces demand for production in sector 2, etc. Naturally, upstream processes contribute successively less. Red bars indicate the "base data" recorded in the economic data. Users can now change the "efficiency" (=how much upstream product is required) for individual processes. This provides instructive insights into how local efficiency changes impact the total value chain - and associated environmental or socio-economic impacts. \label{fig:user_input_table}](_media/user_input_table.pdf){height="3.2cm"}


# Brightway and WebAssembly

In developing `brightwebapp`, all Brightway dependencies were made compatible with Pyodide, either by replacing them with pure Python implementations or with packages included in the Pyodide distribution. This ensures that the Brightway framework can run efficiently in the browser without requiring any additional server-side components.

# Template for Web Applications

`brightwebapp` provides a template for building Holoviz Panel web applications and dashboards that run the Brightway framework in the browser using WebAssembly. To achieve this, it uses [Pyodide](https://pyodide.org/en/stable/) [@pyodide], a Python distribution for the browser and Node.js that allows running Python code in the browser. The implemented example application demonstrates how to use the Brightway framework to perform a supply chain analysis of a sector in the USEEIO database [@yang2017useeio].

\clearpage

# Acknowledgements

This work has been supported by the Swiss Innovation Agency Innosuisse in the context of the WISER flagship project (PFFS-21-72). In addition, Michael P. Weinold gratefully acknowledges the support of the Swiss Study Foundation.

# References