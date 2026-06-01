using Pkg
Pkg.activate(".")
using JuMP, HiGHS, Gurobi
include("../structs.jl")
include("../alforria.jl")
