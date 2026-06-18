julia_path = ARGS[1]
using Pkg
Pkg.activate(julia_path)
# Pkg.add(JuMP)
# Pkg.add(HiGHS)
# Pkg.add(Gurobi)
Pkg.instantiate()