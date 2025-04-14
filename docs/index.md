# BrightWebApp

[:simple-webassembly: Open Browser-based interactive WebAssembly Application (may load slowly) ](https://webapp.brightway.dev){ .md-button }

`BrightWebApp` is a Python package designed to showcase how [the Brightway software framework](https://docs.brightway.dev/en/latest/) can be adapted to provide complex life-cycle assessment calculations in the context of web applications. It is designed to be used either through a [Pyodide](https://pyodide.org/en/stable/) ([WebAssembly](https://www.google.com/search?client=safari&rls=en&q=webassembly&ie=UTF-8&oe=UTF-8)) enabled [Panel](https://panel.holoviz.org) dashboard, or by accessing it running in a Docker container.

```mermaid
flowchart LR
    4 -->|"(...)"| 3 -->|0.1→<b>0.2</b>| 2 -->|"=0.4*(0.5/0.25)"| 1 -->|0.5→<b>0.25</b>| 0
    6 -->|"=0.7*(0.5/0.25)"| 5 -->|"=0.2*(0.5/0.25)"| 1
    8 -->|"(...)"| 7 -->|0.05→<b>0.15</b>| 2

    style 0 fill:#FFCCCB
    style 1 fill:#33CAFF
    style 2 fill:#33CAFF
    style 3 fill:#A2A2A2
    style 4 fill:#A2A2A2
    style 5 fill:#33CAFF
    style 6 fill:#33CAFF
    style 7 fill:#A2A2A2
    style 8 fill:#A2A2A2
```

**Illustration of a supply chain graph, as it would appear in the context of life-cycle assessment**.

As a use-case, it implements a simple logic for modifying branches of a supply chain based user input. This allows practitioners to modify either the amount of flow between production processes or the environmental burden intensity of individual processes.