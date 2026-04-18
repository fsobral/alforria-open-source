include("structs.jl")

conj = ConjuntosAlforria(
    Set(["A", "B", "C"]), 
    Set(["T1", "T2"]), 
    2:7, 
    1:16, 
    1:2, 
    Set(["G1", "G2"]), 
    1:3, 
    Set(["G1", "G2"]), 
    Set(["T1"]), 
    Set(["A"])
)

sar = ParametrosSAR(
    Set([("T1", 1, 1, 1), ("T2", 2, 2, 2)]), 
    Dict("A" => 10, "B" => 20, "C" => 30), 
    Dict("A" => 5, "B" => 10, "C" => 15), 
    Dict("A" => 5, "B" => 10, "C" => 15), 
    Set([("A", "G1"), ("B", "G2")]), 
    Dict("T1" => "G1", "T2" => "G2")
)

form = ParametrosFormulario(
    Set(["A"]), 
    Dict("A" => 5), 
    Dict("A" => 5), 
    Set([("A", 1)]), 
    Set([("A", "T1")]), 
    Set([("A", "T2")]), 
    Dict([(("A", "G1"), 0.8), (("A", "G2"), 0.2)]), 
    Dict([(("A", 1, 1), 0.9), (("A", 2, 2), 0.1)]), 
    Set(["G1"]), 
    Set([("A", 1, 1, 1)]), 
    Dict("A" => 0.5), 
    Dict("A" => 0.3), 
    Dict("A" => 0.2), 
    Dict("A" => 0.4), 
    Dict("A" => 0.6), 
    Dict("A" => 0.6), 
    Dict("A" => 0.6), 
    Dict("A" => 10, "B" => 20, "C" => 30), 
    Dict("A" => 5, "B" => 10, "C" => 15), 
    Dict("A" => 5, "B" => 10, "C" => 15), 
    Dict("A" => 5, "B" => 10, "C" => 15)
)

function defineParametrosConvencionados()::ParametrosConvencionados

	chmax_efetivo_anual = 20
	chmax_efetivo_semestral = 12
	chmax_temporario_anual = 40
	chmax_temporario_semestral = 22
	chmax_diaria = 8
	chmin_efetivo_anual = 16
	chmin_temporario_anual = 24

	chmin_graduacao = 8
	numdiscmax_temporario = 8
	

	paraiso_cargahor = Dict(false => 8, true => 17)
	inferno_cargahor = Dict(false => 10, true => 21)
	cargahor = ParaisoInfernoCustoMarginal(paraiso_cargahor, inferno_cargahor, custoMarginal(paraiso_cargahor, inferno_cargahor))

	paraiso_numdisc = Dict(false => 2, true => 3)
	inferno_numdisc = Dict(false => 4, true => 5)
	numdisc = ParaisoInfernoCustoMarginal(paraiso_numdisc, inferno_numdisc, custoMarginal(paraiso_numdisc, inferno_numdisc))

	paraiso_distintas = Dict(false => 1, true => 2)
	inferno_distintas = Dict(false => 3, true => 4)
	distintas = ParaisoInfernoCustoMarginal(paraiso_distintas, inferno_distintas, custoMarginal(paraiso_distintas, inferno_distintas))

	paraiso_trn_cheios = Dict(false => 0, true => 1)
	inferno_trn_cheios = Dict(false => 2, true => 5)
	trn_cheios = ParaisoInfernoCustoMarginal(paraiso_trn_cheios, inferno_trn_cheios, custoMarginal(paraiso_trn_cheios, inferno_trn_cheios))

	paraiso_turnos = Dict(false => 2, true => 5)
	inferno_turnos = Dict(false => 4, true => 10)
	turnos = ParaisoInfernoCustoMarginal(paraiso_turnos, inferno_turnos, custoMarginal(paraiso_turnos, inferno_turnos))	

	chesp_efetivo_anual = 20
	chesp_temporario_anual = 40

	return ParametrosConvencionados(
	chmax_efetivo_anual,
	chmax_efetivo_semestral,		
	chmax_temporario_anual,
	chmax_temporario_semestral,
	chmax_diaria,
	chmin_efetivo_anual,
	chmin_temporario_anual,

	chmin_graduacao,
	numdiscmax_temporario,

	cargahor,
	numdisc,
	distintas,
	trn_cheios,
	turnos,

	chesp_efetivo_anual,
	chesp_temporario_anual)
end

# conv = defineParametrosConvencionados()

opt = OptimizerOptions(7200.0, 0.6, "alforria.sol", 0, :fobj2)