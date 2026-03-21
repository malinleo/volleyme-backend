import invoke.collection

from inv import utils

utils_ns = invoke.collection.Collection.from_module(utils)

ns = invoke.collection.Collection()
ns.add_collection(utils_ns, name="utils")
