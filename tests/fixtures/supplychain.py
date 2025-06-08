# %%
import bw2data as bd


def example_system_bike_production():
    """
    Sets up a simple supply chain graph in a Brightway project for testing purposes.
    Includes a bike production node, steel production node, electricity production node,
    and a biosphere node for Carbon Dioxide emissions:

    ```mermaid
    graph TD
    subgraph Technosphere
        A["bike production (DK)"]
        B["steel production (DE)"]
        C["electricity production (AT)"]
    end

    subgraph Biosphere
        D(Carbon Dioxide)
    end

    B -- 15.5 kg --> A
    C -- 5.5 kWh --> B
    B -- 0.001 kg --> C
    B -- 26.6 kg --> D
    C -- 11.2 kg --> D

    style D fill:#ffcccc,stroke:#333,stroke-width:2px
    ```

    Also implements a simple `IPCC` impact assessment method for Carbon Dioxide emissions.

    See Also
    --------
    - ["From the Ground Up": The Supply Chain Graph](https://github.com/brightway-lca/from-the-ground-up/blob/main/1%20-%20The%20supply%20chain%20graph.ipynb)
    - [`@cmutel`'s response to an issue on GitHub](https://github.com/brightway-lca/brightway2-calc/issues/123#issuecomment-2897856461)
    """

    try:
        bd.projects.delete_project(
            name = "fixture",
            delete_dir = True
        )
        bd.projects.set_current("fixture")
    except:
        bd.projects.set_current("fixture")

    db = bd.Database("fixture")
    db.register()

    data = {
        'code': 'bike',
        'name': 'bike production',
        'location': 'DK',
        'unit': 'bike',
        'type': bd.labels.chimaera_node_default,
        'reference product': 'bike',
    }
    bike = db.new_node(**data)
    bike.save()

    data = {
        'code': 'steel',
        'name': 'steel production',
        'location': 'DE',
        'unit': 'kg',
        'type': bd.labels.chimaera_node_default,
        'reference product': 'steel',
    }
    steel = db.new_node(**data)
    steel.save()

    data = {
        'code': 'elec',
        'name': 'electricity production',
        'location': 'AT',
        'unit': 'kWh',
        'type': bd.labels.chimaera_node_default,
        'reference product': 'electricity',
    }
    elec = db.new_node(**data)
    elec.save()

    data = {
        'code': 'co2',
        'name': 'Carbon Dioxide',
        'categories': ('air',),
        'unit': 'kg',
        'type': bd.labels.biosphere_node_default,
    }
    co2 = db.new_node(**data)
    co2.save()

    bike.new_edge(
        amount=15.5, 
        uncertainty_type=0,
        type=bd.labels.consumption_edge_default,
        input=steel,
    ).save()

    steel.new_edge(
        amount=5.5, 
        uncertainty_type=0,
        type=bd.labels.consumption_edge_default,
        input=elec,
    ).save()

    elec.new_edge(
        amount=0.001, 
        uncertainty_type=0,
        type=bd.labels.consumption_edge_default,
        input=steel,
    ).save()

    steel.new_edge(
        amount=26.6, 
        uncertainty_type=5, 
        minimum=26,
        maximum=27.2, 
        type=bd.labels.biosphere_edge_default,
        input=co2,
    ).save()

    elec.new_edge(
        amount=11.2, 
        uncertainty_type=5, 
        minimum=13,
        maximum=10, 
        type=bd.labels.biosphere_edge_default,
        input=co2,
    ).save()


    ipcc = bd.Method(('IPCC',))
    ipcc.write([
        (co2.key, {'amount': 1, 'uncertainty_type': 3, 'loc': 1, 'scale': 0.05}),
    ])