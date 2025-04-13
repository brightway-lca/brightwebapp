# %%
import bw2data as bd
import bw2calc as bc
import bw2analyzer as ba

bd.projects.delete_project(name='test', delete_dir=True or False)
bd.projects.set_current("test")

sb = bd.Database("steel bike")
sb.register()

coal = sb.new_node(name="Coal", unit="kg", code="coal")
steel = sb.new_node(name="Steel", unit="kg", code="steel")
iron_mining = sb.new_node(name="Iron mining", unit="kg", code="im")
iron_ore = sb.new_node(name="Iron ore", unit="kg", code="io", type="emission")
steel_bike = sb.new_node(name="Steel bike", unit="unit", code="sb")

coal.save()
steel.save()
iron_mining.save()
iron_ore.save()
steel_bike.save()

iron_mining.new_edge(
    input=iron_ore,
    amount=1.25, 
    uncertainty_type=5, 
    minimum=1,
    maximum=1.75, 
    type='biosphere',
).save()

steel.new_edge(
    input=iron_mining,
    amount=1.1, 
    uncertainty_type=5, 
    minimum=1,
    maximum=1.25, 
    type='technosphere',
).save()

steel.new_edge(
    input=coal,
    amount=0.2, 
    uncertainty_type=5, 
    minimum=0.1,
    maximum=0.5, 
    type='technosphere',
).save()

steel_bike.new_edge(
    input=steel,
    amount=8, 
    uncertainty_type=5, 
    minimum=4,
    maximum=15, 
    type='technosphere',
).save()

bd.Method(("resources",)).write([
    (iron_ore.key, {'amount': 3.141, 'uncertainty_type': 3, 'loc': 3.141, 'scale': 0.5926535}),
])

lca = bc.LCA({steel_bike: 1}, ("resources",))
lca.lci()
lca.lcia()