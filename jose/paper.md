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

BrightWebApp is a [Python](https://www.python.org) software package, stand-alone web application and development template that demonstrates a framework for building complex life-cycle assessment (LCA) and supply chain analysis applications that run in the browser using [WebAssembly (WASM)](https://webassembly.org). It combines the Brightway [@Mutel2017] LCA framework for calculation with the Holoviz Panel [@holoviz_panel] library for interactivity, executing entirely client-side via Pyodide [@pyodide]. As a stand-alone web application, it allows users to perform life cycle assessment, life cycle impact assessment and supply chain analysis of the entire US economy, powered by the US Environmentally-Extended Input-Output (USEEIO) database [@yang2017useeio] directly in their web browser without the need for a local installation of either Python or Brightway. In this context, it is well suited for teaching quantitative sustainability assessment. As a development template, it provides a starting point for developers to build their own web applications that leverage the Brightway framework in the browser and comes with extensive documentation describing the build and deployment process.

# Statement of Need

The Brightway framework [@Mutel2017] is a powerful tool for life-cycle assessment and supply chain analysis. However, it is designed primarily for command-line or local Python environments, which poses a challenge in the educational context and the development of web applications. In life cycle assessment workshops, participants often bring enterprise-managed devices where installing Python packages is restricted, forcing organizers to provision and maintain a Jupyter server and user management services. Similarly, web applications must typically use a complex backend to run the framework or rely on serving static, pre-computed data to users. A recent example of this latter static approach is the carculator application [@sacchi2022and], which assesses the environmental impact of automobiles. BrightWebApp addresses this issue by providing the first template of a WebAssembly-enabled web application for complex life cycle assessment calculations in the browser, eliminating the need for either a local Python environment or a server backend.

\clearpage

# Emission Scope Splitting and Supply Chain Analysis

BrightWebApp implements an example use-case that demonstrates how to split life-cycle assessment results into different "emission scopes" according to the Greenhouse Gas Protocol accounting standard [@bhatia2004greenhouse], shown in \autoref{fig:scope_splitting}.

> Scope 1: Direct GHG emissions. These are from sources that are owned or controlled by the company, for example, emissions from combustion in owned or controlled boilers, furnaces, vehicles, etc.

> Scope 2: Electricity indirect GHG emissions. These are from the generation of purchased electricity consumed by the company. Scope 2 emissions physically occur at the facility where electricity is generated.

> Scope 3: Other indirect GHG emissions. All other indirect emissions.

![Diagram of the example use-case implemented in the BrightWebApp package. Here, every numbered circle represents a production node in the supply chain graph of automotive manufacturing. The supply chain can be split into different levels of "depth". Every node can be assigned to one of three "emission scopes", as defined by the Greenhouse Gas Protocol accounting standard [@bhatia2004greenhouse] \label{fig:scope_splitting}](_media/scope_splitting.pdf){height="5.3cm"}

Users can also interactively explore how changes in the efficiency of individual production processes impact the overall supply chain and associated environmental impacts. This is illustrated in \autoref{fig:user_input_table}, which shows a single branch of a supply chain tree. Here, users can modify the efficiency of individual production processes (i.e. how much input is required to produce a unit of output) and immediately see how this affects the total value chain.

![Diagram of a single branch in a supply chain tree in the context of the economic analysis implemented in the BrightWebApp. The diagram here shows a final demand of 100\$ worth of the product produced by sector 0. This induces demand for production in sectors upstream 1, which induces demand for production in sector 2, etc. Naturally, upstream processes contribute successively less. Red bars indicate the "base data" recorded in the economic data. Users can now change the "efficiency" (=how much upstream product is required) for individual processes. This provides instructive insights into how local efficiency changes impact the total value chain - and associated environmental or socio-economic impacts. \label{fig:user_input_table}](_media/user_input_table.pdf){height="3.4cm"}

\clearpage

# Acknowledgements

This work has been supported by the Swiss Innovation Agency Innosuisse in the context of the WISER flagship project (PFFS-21-72). In addition, Michael P. Weinold gratefully acknowledges the support of the Swiss Study Foundation.

# References