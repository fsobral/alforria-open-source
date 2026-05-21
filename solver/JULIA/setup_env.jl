using Pkg
Pkg.activate(".")
Pkg.add("JuMP")
Pkg.add("HiGHS")
Pkg.add("Gurobi")
Pkg.build("Gurobi")
