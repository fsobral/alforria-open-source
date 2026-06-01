julia_path = ARGS[1]
dat_path = ARGS[2]
using Pkg
Pkg.activate(julia_path)
using JuMP, HiGHS, Gurobi
include("../structs.jl")
include("../alforria.jl")
include(dat_path)

mod, x, xi = alforria(conjuntos, psar, pform, pconf, opt)
optimize!(mod)