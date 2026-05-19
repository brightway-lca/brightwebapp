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
date: 15 May 2026
bibliography: paper.bib

---

# Summary

`BrightWebApp` is a [Python](https://www.python.org) software package, stand-alone web application and development template that demonstrates a framework for building complex life-cycle assessment (LCA) and supply chain analysis applications that run in the browser using [WebAssembly (WASM)](https://webassembly.org). It combines the Brightway [@Mutel2017] LCA framework for calculation with the Holoviz Panel [@holoviz_panel] library for interactivity, executing entirely client-side via Pyodide [@pyodide]. As a stand-alone web application, it allows users to perform life cycle assessment, life cycle impact assessment and supply chain analysis of the entire US economy, based on the US Environmentally-Extended Input-Output (USEEIO) database [@yang2017useeio] directly in their web browser without the need for a local installation of either Python or Brightway. As a web application, it is therefore uniquely suited for teaching quantitative sustainability assessment without technical overhead. As a development template, it provides a starting point for developers to build their own web applications that leverage the Brightway framework in the browser and comes with extensive documentation describing the build and deployment process.

# Statement of need

The Brightway framework [@Mutel2017] is a powerful tool for life-cycle assessment and supply chain analysis, now widely used in academic and industry settings. However, it is designed primarily for use from the command-line or through local Python environments, which poses a challenge in the educational context. In life cycle assessment classes and workshops, participants often bring enterprise-managed devices where installing Python packages is restricted, forcing organizers to provision and maintain a Jupyter server and user management services. On the other hand, a standalone web application as the obvious alternative must typically use a complex backend to expose the calculation framework or rely on serving static, pre-computed data to users. A recent example of this latter static approach is the carculator application [@sacchi2022and], which assesses the environmental impact of automobiles. In this context, `BrightWebApp` addresses the aforemmentioned issues by providing the first template of a WebAssembly-enabled web application for complex life cycle assessment calculations in the browser, eliminating the need for either a local Python environment or a server backend.

# State of the field

Several established open-source tools address adjacent problems in life-cycle assessment and supply chain analysis. The Brightway framework itself [@Mutel2017] provides the calculation core but is designed for local command-line use. Activity Browser [@steubing2020activity] offers a desktop graphical interface to Brightway but still requires a local installation of Python and the framework on each user device. openLCA [@ciroth2007ict] is a widely used Java-based LCA application with similar local-installation requirements. Domain-specific tools built on Brightway, such as carculator [@sacchi2022and] for automotive LCA, have begun to expose results through web interfaces, but these typically serve only pre-computed scenarios because the underlying calculation engine cannot run in the browser.

\textbf{Table 1} Selection of representative open-source software packages for life-cycle assessment and supply chain analysis. Abbreviations: Py. = Python, Jv. = Java.

```{=latex}
\begingroup
\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}p{0.24\linewidth}p{0.09\linewidth}p{0.59\linewidth}@{}}
\hline
Name & Lang. & Purpose \\
\hline
Brightway (\href{https://doi.org/10.21105/joss.00236}{2017}) & Py. & LCA calculation framework (local) \\
Activity Browser (\href{https://github.com/LCA-ActivityBrowser/activity-browser}{2020}) & Py. & Desktop GUI for Brightway \\
carculator (\href{https://doi.org/10.1016/j.rser.2022.112475}{2022}) & Py. & Automotive LCA with static web frontend \\
openLCA (\href{https://www.openlca.org}{2023}) & Jv. & General-purpose LCA software (local) \\
\hline
\end{tabular}
\endgroup
```

`BrightWebApp` therefore fills a novel scholarly and pedagogical niche. To the best knowledge of the authors, it is the first complete template for running a full Brightway-based LCA workflow client-side in the browser. It therefore enables sustainability education in without the need for platform-specific local Python installations or server backends.

# Software design

The central design choice of `BrightWebApp` is to execute the full Brightway stack [@Mutel2017] inside the user's browser through the Pyodide [@pyodide] WebAssembly Python runtime, rather than on a remote server. The interactive user interface is built with Holoviz Panel [@holoviz_panel], whose components are rendered directly in the browser through Pyodide. This client-side architecture eliminates the need for a server backend, user authentication, or session management, and ensures that no user data leaves the device.

The package is organized as a small set of focused modules. The `brightway` module wraps the underlying Brightway calculation primitives (`bw2data`, `bw2io`, `bw2calc`) for use in the browser context. The `traversal` module implements supply-chain graph traversal on top of `bw_graph_tools` for the example use case. The `modifications` module exposes interactive parameter adjustments that propagate through the supply chain in real time. The same package can be used both as a stand-alone web application and as a development template that downstream projects can fork to build their own browser-based LCA tools.

# Research impact statement

The framework implemented in `BrightWebApp` has supported scholarly and teaching outputs. It was developed in the context of the teaching requirements of the doctoral research _Hybrid Life-Cycle Assessment for Sustainable Aviation_ [@weinold2026hybridaviation] and has been used to deliver hands-on life-cycle assessment teaching in the context of multipl academic life cycle assessment seminars:

- [DdS/PSI Spring School 2024, Quebec (May 2024)](https://github.com/Depart-de-Sentier/Schools-2024-May-Quebec)
- [DdS/PSI Autumn School (October 2024)](https://github.com/Depart-de-Sentier/autumn-school-dds-psi-2024)
- [DdS/PSI Summer School 2025, Singapore (June 2025)](https://github.com/Depart-de-Sentier/Schools-2025-June-Singapore)

# Emission scope splitting and supply chain analysis

`BrightWebApp` implements an example use-case that demonstrates how to split life-cycle assessment results into different "emission scopes" according to the Greenhouse Gas Protocol accounting standard [@bhatia2004greenhouse], shown in \autoref{fig:scope_splitting}.

> Scope 1: Direct GHG emissions. These are from sources that are owned or controlled by the company, for example, emissions from combustion in owned or controlled boilers, furnaces, vehicles, etc.

> Scope 2: Electricity indirect GHG emissions. These are from the generation of purchased electricity consumed by the company. Scope 2 emissions physically occur at the facility where electricity is generated.

> Scope 3: Other indirect GHG emissions. All other indirect emissions.

![Diagram of the example use-case implemented in the BrightWebApp package. Here, every numbered circle represents a production node in the supply chain graph of automotive manufacturing. The supply chain can be split into different levels of "depth". Every node can be assigned to one of three "emission scopes", as defined by the Greenhouse Gas Protocol accounting standard [@bhatia2004greenhouse] \label{fig:scope_splitting}](_media/scope_splitting.pdf){height="5.3cm"}

Users can also interactively explore how changes in the efficiency of individual production processes impact the overall supply chain and associated environmental impacts. This is illustrated in \autoref{fig:user_input_table}, which shows a single branch of a supply chain tree. Here, users can modify the efficiency of individual production processes (i.e. how much input is required to produce a unit of output) and immediately see how this affects the total value chain.

![Diagram of a single branch in a supply chain tree in the context of the economic analysis implemented in the BrightWebApp. The diagram here shows a final demand of 100\$ worth of the product produced by sector 0. This induces demand for production in sectors upstream 1, which induces demand for production in sector 2, etc. Naturally, upstream processes contribute successively less. Red bars indicate the "base data" recorded in the economic data. Users can now change the "efficiency" (=how much upstream product is required) for individual processes. This provides instructive insights into how local efficiency changes impact the total value chain - and associated environmental or socio-economic impacts. \label{fig:user_input_table}](_media/user_input_table.pdf){height="3.4cm"}


# AI Usage disclosure

Large language models (LLMs) were used as programming assistants for repository maintenance, the improvement of unit and integration tests, and the formatting of this publication. All resulting changes were reviewed by the authors.

# Acknowledgements

This work has been supported by the Swiss Innovation Agency Innosuisse in the context of the WISER flagship project (PFFS-21-72). In addition, Michael P. Weinold gratefully acknowledges the support of the Swiss Study Foundation.

# References
