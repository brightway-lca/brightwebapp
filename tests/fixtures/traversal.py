# %%
import bw2data as bd
import bw2calc as bc
import pytest


#@pytest.fixture
def example_system_bike_production():
    """
    TODO add summary here!

    See Also
    --------
    - ["From the Ground Up": The Supply Chain Graph](https://github.com/brightway-lca/from-the-ground-up/blob/main/1%20-%20The%20supply%20chain%20graph.ipynb)
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

    bike = db.new_node(
        code='bike',
        name='bike production',
        location='DK',
        unit='bike'
    )
    bike.save()
    ng = db.new_node(
        code='ng',
        name='natural gas production',
        location='NO',
        unit='MJ'
    )
    ng.save()
    cf = db.new_node(
        code='cf',
        name='carbon fibre production',
        location='DE',
        unit='kg'
    )
    cf.save()
    co2 = db.new_node(
        code='co2', 
        name="Carbon Dioxide", 
        categories=('air',),
        type='emission',
        unit='kg'
    )
    co2.save()

    bike.new_edge(
        amount=2.5, 
        type='technosphere',
        input=cf
    ).save()
    cf.new_edge(
        amount=237.3,
        uncertainty_type=5, 
        minimum=200, 
        maximum=300, 
        type='technosphere',
        input=ng,
    ).save()
    cf.new_edge(
        amount=26.6, 
        uncertainty_type=5, 
        minimum=26,
        maximum=27.2, 
        type='biosphere',
        input=co2,
    ).save()

    ipcc = bd.Method(('IPCC'))
    ipcc.write([
        (co2.key, {'amount': 1, 'uncertainty_type': 3, 'loc': 1, 'scale': 0.05}),
    ])

    return db


# %%

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

bike = db.new_node(
    code='bike',
    name='bike production',
    location='DK',
    unit='bike'
)
bike.save()

co2 = db.new_node(
    code='co2', 
    name="Carbon Dioxide", 
    categories=('air',),
    type='emission',
    unit='kg'
)
co2.save()

ipcc = bd.Method(('IPCC'))
ipcc.write([
    (co2.key, {'amount': 1, 'uncertainty_type': 3, 'loc': 1, 'scale': 0.05}),
])

# %%
ng = db.new_node(
    code='ng',
    name='natural gas production',
    location='NO',
    unit='MJ'
)
ng.save()
cf = db.new_node(
    code='cf',
    name='carbon fibre production',
    location='DE',
    unit='kg'
)
cf.save()
co2 = db.new_node(
    code='co2', 
    name="Carbon Dioxide", 
    categories=('air',),
    type='emission',
    unit='kg'
)
co2.save()

bike.new_edge(
    amount=2.5, 
    type='technosphere',
    input=cf
).save()
cf.new_edge(
    amount=237.3,
    uncertainty_type=5, 
    minimum=200, 
    maximum=300, 
    type='technosphere',
    input=ng,
).save()
cf.new_edge(
    amount=26.6, 
    uncertainty_type=5, 
    minimum=26,
    maximum=27.2, 
    type='biosphere',
    input=co2,
).save()


# %%

db = example_system_bike_production()

lca = bc.LCA( 
    demand={bd.get_node(code='bike'): 100}, 
    method = ('IPCC')
)
lca.lci()