julia_path = ARGS[1]
using Pkg
Pkg.activate(julia_path)
Pkg.instantiate()