import Pkg
# using Pkg
Pkg.activate(".")
Pkg.add(JuMP)
Pkg.add(HiGHS)
Pkg.add(Gurobi)
using JuMP, HiGHS, Gurobi
include("../structs.jl")
include("../alforria.jl")
