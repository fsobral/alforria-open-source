using Pkg
Pkg.activate(".")
# ENV["GRB_LICENSE_FILE"] = "C:\\Users\\seven\\gurobi.lic"
using JuMP, HiGHS, Gurobi
include("structs.jl")
include("alforria.jl")
# include("alforria.dat.jl")