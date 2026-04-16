import Pkg
Pkg.add("JuMP")
Pkg.add("HiGHS")
# Pkg.add("Gurobi")
include("structs.jl")

using JuMP, HiGHS
#using Gurobi

function custoMarginal(paraiso::Dict{Bool, Int64}, inferno::Dict{Bool, Int64})::Dict{Bool, Float64}
	return Dict(k => 5 / (inferno[k] - paraiso[k]) for k in [false, true])
end

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

function chmax_padrao(p, form, conv)
	temporario = p in form.temporario
	em_licenca = ((p, 1) in form.licenca) + ((p, 2) in form.licenca) > 0
	
	if temporario
		return em_licenca ? conv.chmax_temporario_semestral : conv.chmax_temporario_anual
	else
		return em_licenca ? conv.chmax_efetivo_semestral : conv.chmax_efetivo_anual
	end
end

function chmaxS_padrao(p, form, conv, s)
	temporario = p in form.temporario
	em_licenca = ((p, s) in form.licenca)

	return em_licenca ? 0 : (temporario ? conv.chmax_temporario_semestral : conv.chmax_efetivo_semestral)
end

function chmin_padrao(p, form, conv)
	temporario = p in form.temporario
	em_licenca = ((p, 1) in form.licenca) + ((p, 2) in form.licenca) > 0
	
	if temporario
		return em_licenca ? div(conv.chmin_temporario_anual,2) : conv.chmin_temporario_anual
	else
		return em_licenca ? div(conv.chmin_efetivo_anual,2) : conv.chmin_efetivo_anual
	end     
end

function preencheSAR!(sar::ParametrosSAR, conj::ConjuntosAlforria) 
	for t in conj.T
		if !haskey(sar.ch, t)
			sar.ch[t] = sum(1 for s in conj.S, d in conj.D, h in conj.H if (t, s, d, h) in sar.c)
		end

		if !haskey(sar.ch1, t)
			sar.ch1[t] = sum(Int64[1 for d in conj.D, h in conj.H if (t, conj.S[1], d, h) in sar.c])
		end

		if !haskey(sar.ch2, t)
			sar.ch2[t] = sum(Int64[1 for d in conj.D, h in conj.H if (t, conj.S[2], d, h) in sar.c])
		end
	end
end

function preencheFormulario!(
	sar::ParametrosSAR,
	form::ParametrosFormulario,
	conj::ConjuntosAlforria,
	conv::ParametrosConvencionados)
	
	for p in conj.P
		if !haskey(form.chprevia1, p)
			form.chprevia1[p] = 0.0
		end

		if !haskey(form.chprevia2, p)
			form.chprevia2[p] = 0.0
		end
        
		if !haskey(form.peso_disciplinas, p)
			form.peso_disciplinas[p] = 0.0
		end
        
        if !haskey(form.peso_numdisc, p)
            form.peso_numdisc[p] = 5.0
        end
		
		if !haskey(form.peso_cargahor, p)
		   form.peso_cargahor[p] = 5.0
		end
	
		if !haskey(form.peso_horario, p)
			form.peso_horario[p] = 5.0
		end

		if !haskey(form.peso_distintas, p)
			form.peso_distintas[p] = 5.0
		end

		if !haskey(form.peso_manha_noite, p)
			form.peso_manha_noite[p] = 5.0
		end
		
		if !haskey(form.peso_janelas, p)
			form.peso_janelas[p] = 5.0
		end
	
		for g in conj.G
			if ((p, g) in form.inapto && (sum((p, t) in form.pre_atribuida for t in conj.T if (sar.turma_grupo[t] == g),init=0) >= 1))
				delete!(form.inapto, (p, g))
			end    

			if !haskey(form.pref_grupo, (p, g))
				form.pref_grupo[(p,g)] = 0.0
			end
		end

		for d in conj.D, h in conj.H
			if !haskey(form.pref_hor, (p, d, h))
				form.pref_hor[(p, d, h)] = 5.0
			end
		end

		if !haskey(form.chmax, p)
			form.chmax[p] = chmax_padrao(p, form, conv)
		end

		if !haskey(form.chmax1, p)
			form.chmax1[p] = chmaxS_padrao(p, form, conv, 1)
		end

		if !haskey(form.chmax2, p)
			form.chmax2[p] = chmaxS_padrao(p, form, conv, 2)
		end

		if !haskey(form.chmin, p)
			form.chmin[p] = chmin_padrao(p, form, conv)
		end
	end
end

function parametrosDerivados(
	conj::ConjuntosAlforria,
	form::ParametrosFormulario,
	sar::ParametrosSAR,
	conv::ParametrosConvencionados
	)::ParametrosDerivados

	chprevia_tt = Dict(p => (form.chprevia1[p]  + form.chprevia2[p]) for p in conj.P)

	prop =  Dict(p => (0.5*(2 - ((p, 1) in form.licenca) - ((p,2) in form.licenca))) for p in conj.P)

	pref_turma = Dict((p, t) => 
	((t ∉ keys(sar.turma_grupo)) || (p, sar.turma_grupo[t]) in form.inapto) 
	? 0 : form.pref_grupo[p, sar.turma_grupo[t]] for p in conj.P, t in conj.T)

	horario_turno = Dict(h => (h <= 5 ? 1 : h <= 10 ? 2 : 3) for h in conj.H)

	semestralidade = Set([(t, s) for t in conj.T, s in conj.S if sum(((t, s, d, h) in sar.c) for d in conj.D, h in conj.H) >= 1])

	ajuste_hor = Dict(p => 
	begin
		s = sum(form.pref_hor[p, d, h] for d in conj.D, h in conj.H)
		s == 0 ? 0 : div(400, s)
	end for p in conj.P)
	
	chprevia_total =sum(chprevia_tt[p] for p in conj.P)

	chesp = Dict(p => p in form.temporario ?
		conv.chesp_temporario_anual
		: ((p, 1) in form.licenca) + ((p, 2) in form.licenca) == 0 ?
			conv.chesp_efetivo_anual
			: conv.chesp_efetivo_anual / 2
	for p in conj.P)

	peso_total_inv = Dict(p =>
	(1/ (form.peso_disciplinas[p]+form.peso_numdisc[p]+form.peso_cargahor[p]+form.peso_horario[p]
	+form.peso_distintas[p]+form.peso_manha_noite[p]+form.peso_janelas[p])) for p in conj.P)

	return ParametrosDerivados(chprevia_tt, prop, pref_turma, horario_turno, semestralidade, ajuste_hor, chprevia_total, chesp, peso_total_inv)
end

function declaraVariaveis!(mod::Model, conj::ConjuntosAlforria)::Variaveis
	@variables(mod, begin
	max_das_insat
	insat[conj.P]
	ch_atendida
	gap_ch_tt
	gap_horario_max
	gap_ch_graduacao
	end)

	@variable(mod, x[conj.P, conj.T], Bin) # 1 se o professor P é alocado na turma T

	@variables(mod,
	begin
	lec_grp[conj.P, conj.G, conj.S], Bin               # 1 se o professor P leciona displina do grupo G no semestre S
	lec_trn[conj.P, conj.S, conj.D, conj.TURNOS], Bin    # Indica se P leciona no semestre S, dia D, turno TURNOS
	trn_cheio[conj.P, conj.S, conj.D, conj.TURNOS], Bin  # O respectivo turno é cheio
	end)

	@variables(mod,
	begin
	noite[conj.P, conj.S], Bin        # p leciona a noite em s
	manha[conj.P, conj.S], Bin        # p leciona de manha em s
	noitext[conj.P, conj.S], Bin      # p leciona no extremo da noite em s
	manhaxt[conj.P, conj.S], Bin      # p leciona no extremo da manha em s
	mnh_nt[conj.P, conj.S], Bin       # p leciona na manha e noite em s
	mnh_ntxt[conj.P, conj.S], Bin     # p leciona na manha e extremo da noite em s
	nt_mnhxt[conj.P, conj.S], Bin     # p leciona na noite e extremo da manha em s
	end)

	return Variaveis(
		max_das_insat, insat, ch_atendida, gap_ch_tt, gap_horario_max, gap_ch_graduacao,
		x,
		lec_grp, lec_trn, trn_cheio,
		noite, manha, noitext, manhaxt, mnh_nt, mnh_ntxt, nt_mnhxt)
end

function adicionaRestricoesEssenciais!(
	mod::Model,
	conj::ConjuntosAlforria,
	form::ParametrosFormulario,
	sar::ParametrosSAR,
	deriv::ParametrosDerivados,
	conv::ParametrosConvencionados,
	var::Variaveis)
	# Um professor nao leciona em duas turmas ao mesmo tempo
	@constraint(mod, rest1[p in conj.P, s in conj.S, d in conj.D, h in conj.H],
	sum(((t,s,d,h) in sar.c) * var.x[p,t] for t in conj.T) <= 1)

	# Professores inaptos nao ministram as respectivas disciplinas
	restt2 = [(p, t) for p in conj.P, t in conj.T if (t ∈ keys(sar.turma_grupo)) && ((p, sar.turma_grupo[t]) in form.inapto)]
	@constraint(mod, rest2[(p, t) in restt2], var.x[p,t] == 0)

	# Cada turma tem, no maximo, um professor #
	@constraint(mod, rest3[t in conj.T],
	sum(var.x[p,t] for p in conj.P) <= 1) #------------------------------------------------------------------------FORÇANDO TODOS

	# Limita superiormente a carga horaria anual e semestral de um professor
	@constraint(mod, rest4_1[p in conj.P],
	deriv.chprevia_tt[p] + sum(sar.ch[t]*var.x[p,t] for t in conj.T) <= max(0, form.chmax[p]))

	@constraint(mod, rest4_2[p in conj.P],
	form.chprevia1[p] + sum(sar.ch1[t]*var.x[p,t] for t in conj.T) <= max(0, form.chmax1[p]))

	@constraint(mod, rest4_3[p in conj.P],
	form.chprevia2[p] + sum(sar.ch2[t]*var.x[p,t] for t in conj.T) <= max(0, form.chmax2[p]))

	# Limita inferiormente a carga horaria anual de um professor
	# @constraint(mod, rest5[p in conj.P], chprevia_tt[p] + sum(sar.ch_in[t]*var.x[p,t] for t in conj.T) >= chmin_in[p])
	# ! Lembrar de retirar isso na hora de entrar em produção!!
	@constraint(mod, rest5[p in conj.P], sum(sar.ch[t]*var.x[p,t] for t in conj.T) >= 1)

	# Professor nao pode dar aulas em horarios conflitantes com outras atividades
	rett6 = [(p, t, s, d, h) for p in conj.P, t in conj.T, s in conj.S, d in conj.D, h in conj.H if ((p,s,d,h) in form.impedimento && (t,s,d,h) in sar.c)]
	@constraint(mod, rest6[(p,t,s,d,h) in rett6], var.x[p,t] == ((p,t) in form.pre_atribuida)) #? pode dar problema??

	# Deve haver um intervalo maior ou igual que 11h entre jornadas de trabalho em dias consecutivos
	#! Verificar se precisa ir até 7
	rett7 = [(p,d,s,h1,h2) for p in conj.P, d in 2:6, s in conj.S, h1 in 14:16, h2 in 1:3 if h1 - h2 >= 13]
	@constraint(mod, rest7[(p, d, s, h1, h2) in rett7],
	sum(((t,s,d,h1) in sar.c) * var.x[p,t] for t in conj.T if !(t in conj.T_PRE)) + sum(((t,s,d + 1,h2) in sar.c) * var.x[p,t] for t in conj.T if !(t in conj.T_PRE)) <= 1)

	# Respeita as disciplinas pre-atribuidas
	@constraint(mod, rest8[(p,t) in form.pre_atribuida], var.x[p,t] == 1)

	# Maximo de horas de aula diarias
	@constraint(mod, rest9[p in conj.P, s in conj.S, d in conj.D], sum(var.x[p,t] * ((t,s,d,h) in sar.c) for t in conj.T, h in conj.H) <= conv.chmax_diaria)

	# Vincula as duas metades de uma disciplina anual
	@constraint(mod, rest10[p in conj.P, (t1, t2) in sar.vinculadas], var.x[p,t1] == var.x[p,t2])

	# Maximo de numero de disciplinas para temporarios
	@constraint(mod, rest11[p in form.temporario], sum(var.x[p,t] for t in conj.T) <= conv.numdiscmax_temporario)

	# Maximo de numero de grupos para temporarios
	@constraint(mod, rest12[p in form.temporario, s in conj.S], sum(var.lec_grp[p,g,s] for g in conj.G) <= 2)

end

function defineVariaveisDemanda!(mod::Model,
	conj::ConjuntosAlforria,
	form::ParametrosFormulario,
	sar::ParametrosSAR,
	deriv::ParametrosDerivados,
	conv::ParametrosConvencionados,
	var::Variaveis)

	previa_liquida = Dict(p => (form.chprevia1[p] + form.chprevia2[p] + sum(((p, t) in form.pre_atribuida)*sar.ch[t] for t in conj.T)) for p in conj.P)

	capacidade_pessoal = Dict(p => p in form.temporario ?
	max(previa_liquida[p], conv.chesp_temporario_anual)
	: max(previa_liquida[p], conv.chesp_efetivo_anual)
	for p in conj.P)

	capacidade_total = sum(capacidade_pessoal[p] for p in conj.P) - deriv.chprevia_total

	demanda = sum(sar.ch[t] for t in conj.T)

	@constraint(mod, def_gap_ch_tt1, var.gap_ch_tt >= min(demanda, capacidade_total) - sum(sar.ch[t] * var.x[p, t] for t in conj.T, p in conj.P)) #blablabla - oferta
	@constraint(mod, def_gap_ch_tt2, var.gap_ch_tt >= 0)
	@constraint(mod, def_gap_horario_max1[p in conj.P], var.gap_horario_max >= form.chmin[p] - (deriv.chprevia_tt[p] + sum(sar.ch[t] * var.x[p,t] for t in conj.T)))
	@constraint(mod, def_gap_horario_max2, var.gap_horario_max >= 0)

	licencaP0 = [p for p in conj.P if (((p, 1) in form.licenca) + ((p, 2) in form.licenca) == 0)]
	@constraint(mod, def_gap_ch_grad1[p in licencaP0],
	var.gap_ch_graduacao >= conv.chmin_graduacao - sum(sar.ch[t] * var.x[p, t] for t in conj.T))

	licencaP1 = [p for p in conj.P if (((p, 1) in form.licenca) + ((p, 2) in form.licenca) == 1)]
	@constraint(mod, def_gap_ch_grad2[p in licencaP1],
	var.gap_ch_graduacao >= div(conv.chmin_graduacao, 2) - sum(sar.ch[t] * var.x[p, t] for t in conj.T))

	@constraint(mod, def_gap_ch_grad3, var.gap_ch_graduacao >= 0)

end

function defineVariaveisAuxiliares!(mod::Model,
	conj::ConjuntosAlforria,
	form::ParametrosFormulario,
	sar::ParametrosSAR,
	deriv::ParametrosDerivados,
	var::Variaveis)

	# Define as variáveis auxiliares de lecionar grupo, lecionar turno, turno cheio, manha, noite, etc.
	@constraint(mod, def_lec_grp_inapto[(p, g) in form.inapto, s in conj.S], var.lec_grp[p, g, s] == 0)

	inapto0 = [(p, g) for p in conj.P, g in conj.G if !((p, g) in form.inapto)]
	@constraint(mod, def_lec_grp_up[(p, g) in inapto0, s in conj.S],
				var.lec_grp[p, g, s] <= sum((g == sar.turma_grupo[t])*var.x[p,t] for t in conj.T if (t, s) in deriv.semestralidade))
	down = [(p, g, t, s) for (p, g) in inapto0, (t, s) in deriv.semestralidade if  (g == sar.turma_grupo[t])]
	@constraint(mod, def_lec_grp_down[(p, g, t, s) in down],
				var.lec_grp[p,g,s] >= var.x[p,t])

	# Definicao da variavel auxiliar lec_trn (Indica se p leciona so memestre s, dia d, turno u)
	@constraint(mod, def_lec_trn_up[p in conj.P, s in conj.S, d in conj.D, u in conj.TURNOS],
				var.lec_trn[p,s,d,u] <= sum(var.x[p,t] for t in conj.T, h in conj.H if (u == deriv.horario_turno[h] && (t,s,d,h) in sar.c)))
	downt = [(p, s, t, d, h, deriv.horario_turno[h]) for p in conj.P, s in conj.S, t in conj.T, d in conj.D, h in conj.H if (t, s, d, h) in sar.c]
	@constraint(mod, def_lec_trn_down[(p, s, t, d, h, u) in downt],
				var.lec_trn[p,s,d,u] >= var.x[p,t])

	# Definicao da variavel auxiliar trn_cheio (Indica se p leciona so memestre s, dia d, turno u)
	@constraint(mod, def_trn_cheio_up[p in conj.P, s in conj.S, d in conj.D, u in conj.TURNOS],
				4 * var.trn_cheio[p,s,d,u] <= sum(var.x[p,t] for t in conj.T, h in conj.H if u == deriv.horario_turno[h] && (t,s,d,h) in sar.c))
	@constraint(mod, def_trn_cheio_down[p in conj.P, s in conj.S, d in conj.D, u in conj.TURNOS],
				var.trn_cheio[p,s,d,u] >= -3 + 0.5*sum(var.x[p,t] for t in conj.T, h in conj.H if (u == deriv.horario_turno[h] && (t,s,d,h) in sar.c)))

	# Manha[p,s] : p leciona pela manha em s
	@constraint(mod, def_manha_up[p in conj.P, s in conj.S], var.manha[p,s] <= sum(var.lec_trn[p,s,d,1] for d in conj.D))
	@constraint(mod, def_manha_low[p in conj.P, s in conj.S, d in conj.D], var.manha[p,s] >= var.lec_trn[p,s,d,1])

	# Noite[p,s] : p leciona pela noite em s
	@constraint(mod, def_noite_up[p in conj.P, s in conj.S], var.noite[p,s] <= sum(var.lec_trn[p,s,d,3] for d in conj.D))
	@constraint(mod, def_noite_low[p in conj.P, s in conj.S, d in conj.D], var.noite[p,s] >= var.lec_trn[p,s,d,3])

	# noitext[p,s]: p leciona no extremo da noite em s
	#! Atenção que o horário extremo é 15-16 e não 13-14
	@constraint(mod, def_noitext_up[p in conj.P, s in conj.S],
	var.noitext[p,s] <= sum(((t,s,d,13) in sar.c) * var.x[p,t] + ((t,s,d,14) in sar.c) * var.x[p,t] for t in conj.T, d in conj.D))
	@constraint(mod, def_noitext_down[p in conj.P, s in conj.S],
	12 * var.noitext[p,s] >= sum(((t,s,d,13) in sar.c) * var.x[p,t] + ((t,s,d,14) in sar.c) * var.x[p,t] for t in conj.T, d in conj.D))

	# manhaxt[p,s]: p leciona no extremo da manha em s (horario 1 ou 2)
	@constraint(mod, def_manhaxt_up[p in conj.P, s in conj.S],
	var.manhaxt[p,s] <= sum(((t,s,d,1) in sar.c) * var.x[p,t] + ((t,s,d,2) in sar.c) * var.x[p,t] for t in conj.T, d in conj.D))
	@constraint(mod, def_manhaxt_down[p in conj.P, s in conj.S],
	12 * var.manhaxt[p,s] >= sum(((t,s,d,1) in sar.c) * var.x[p,t] + ((t,s,d,2) in sar.c) * var.x[p,t] for t in conj.T, d in conj.D))

	# mnh_nt[p,s] pe leciona de manha E de noite em s
	@constraint(mod, def_mnh_nt_1[p in conj.P, s in conj.S], var.mnh_nt[p,s] <= var.manha[p,s])
	@constraint(mod, def_mnh_nt_2[p in conj.P, s in conj.S], var.mnh_nt[p,s] <= var.noite[p,s])
	@constraint(mod, def_mnh_nt_3[p in conj.P, s in conj.S], var.mnh_nt[p,s] >= var.manha[p,s] + var.noite[p,s] - 1)

	# mnh_ntxt[x,p]: p leciona na manha e extremo da noite noite em s
	@constraint(mod, def_mnh_ntxt_1[p in conj.P, s in conj.S], var.mnh_ntxt[p,s] <= var.mnh_nt[p,s])
	@constraint(mod, def_mnh_ntxt_2[p in conj.P, s in conj.S], var.mnh_ntxt[p,s] <= var.noitext[p,s])
	@constraint(mod, def_mnh_ntxt_3[p in conj.P, s in conj.S], var.mnh_ntxt[p,s] >= var.mnh_nt[p,s] + var.noitext[p,s] - 1)

	# nt_mnhxt[x,p]: p leciona na noite e extremo da manha em s
	@constraint(mod, def_nt_mnhxt_1[p in conj.P, s in conj.S], var.nt_mnhxt[p,s] <= var.mnh_nt[p,s])
	@constraint(mod, def_nt_mnhxt_2[p in conj.P, s in conj.S], var.nt_mnhxt[p,s] <= var.manhaxt[p,s])
	@constraint(mod, def_nt_mnhxt_3[p in conj.P, s in conj.S], var.nt_mnhxt[p,s] >= var.mnh_nt[p,s] + var.manhaxt[p,s] - 1)

end

function defineRestricoesVariaveis!(mod::Model,
	conj::ConjuntosAlforria,
	form::ParametrosFormulario,
	sar::ParametrosSAR,
	deriv::ParametrosDerivados,
	conv::ParametrosConvencionados,
	var::Variaveis)

	ub_insat = Dict(p => 100 for p in conj.P) #? qual a utilidade se todo ub é 100?

	@constraint(mod, limitante_insatisfacao[p in conj.P],
	var.insat[p] <= ub_insat[p])

	@variable(mod, carga_horaria[conj.P])
	@variable(mod, numero_de_disciplinas[conj.P])
	@variable(mod, insat_disciplinas[conj.P])
	@variable(mod, insat_cargahor[conj.P])
	@variable(mod, insat_numdisc[conj.P])
	@variable(mod, insat_horario[conj.P])
	@variable(mod, insat_distintas[conj.P])
	@variable(mod, insat_manha_noite[conj.P])
	@variable(mod, insat_janelas[conj.P])

	@constraint(mod, def_carga_horaria[p in conj.P], carga_horaria[p] == sum(sar.ch[t]*var.x[p,t] for t in conj.T) + deriv.chprevia_tt[p])
	@constraint(mod, def_numero_de_disciplinas[p in conj.P], numero_de_disciplinas[p] == sum(var.x[p,t] for t in conj.T))

	@constraint(mod, def_insat_disciplinas[p in conj.P], insat_disciplinas[p] ==
	(1/deriv.chesp[p]) * sum(deriv.pref_turma[p, t] * sar.ch[t]*var.x[p,t] for t in conj.T))

	@constraint(mod, def_insat_cargahor[p in conj.P], insat_cargahor[p] ==
	conv.cargahor.customarginal[p in form.temporario] * ((sum(sar.ch[t]*var.x[p,t] for t in conj.T) + deriv.chprevia_tt[p])-2*conv.cargahor.paraiso[p in form.temporario]))

	@constraint(mod, def_insat_numdisc[p in conj.P], insat_numdisc[p] ==
	conv.numdisc.customarginal[p in form.temporario] * ((sum(var.x[p, t] for t in conj.T) + (deriv.chprevia_tt[p] / 6) - 2 * conv.numdisc.paraiso[p in form.temporario])))

	@constraint(mod, def_insat_horario[p in conj.P], insat_horario[p] ==
	var.ajuste_hor[p] * (1 / deriv.chesp[p]) * sum(((t,s,d,h) in sar.c)*form.pref_hor[p,d,h]*var.x[p,t] for t in conj.T, s in conj.S, d in conj.D, h in conj.H))

	@constraint(mod, def_insat_distintas[p in conj.P], insat_distintas[p] ==
	conv.distintas.customarginal[p in form.temporario] * ((sum(var.lec_grp[p,g,s] for g in conj.G, s in conj.S) + (deriv.chprevia_tt[p]/6))-2*conv.distintas.paraiso[p in form.temporario]))

	@constraint(mod, def_insat_manha_noite[p in conj.P], insat_manha_noite[p] == 5*(var.mnh_nt[p,1]+var.mnh_nt[p,2]))

	@constraint(mod, def_insat_janelas[p in conj.P],
	insat_janelas[p] == (p in form.pref_janelas) * conv.trn_cheios.customarginal[p in form.temporario]*
	(sum(var.trn_cheio[p,s,d,u] for s in conj.S, d in conj.D, u in conj.TURNOS) - 2*conv.trn_cheios.paraiso[p in form.temporario])
	+(1-(p in form.pref_janelas)) * conv.turnos.customarginal[p in form.temporario]*
	(sum(var.lec_trn[p,s,d,u] for s in conj.S, d in conj.D, u in conj.TURNOS) - 2 * conv.turnos.paraiso[p in form.temporario]))

	return VariaveisInsat(
		carga_horaria, numero_de_disciplinas, insat_disciplinas, insat_cargahor, insat_numdisc, insat_horario, insat_distintas, insat_manha_noite, insat_janelas)
end

function defineInsatisfacao!(mod::Model,
	conj::ConjuntosAlforria,
	deriv::ParametrosDerivados,
	form::ParametrosFormulario,
	var::Variaveis,
	varInsat::VariaveisInsat)

	# ###############################         INSATISFACAO DEFINICAO         ####################

	#Escala aproximada de zero a 10
	@constraint(mod, insat_def[p in conj.P], var.insat[p] ==
	(1 - 0.2*(p in form.temporario)) * deriv.peso_total_inv[p] * (1/deriv.prop[p]) * (
		  (form.peso_disciplinas[p] * varInsat.insat_disciplinas[p])
		+ (form.peso_cargahor[p]    * varInsat.insat_cargahor[p])
		+ (form.peso_numdisc[p]     * varInsat.insat_numdisc[p])
		+ (form.peso_horario[p]     * varInsat.insat_horario[p])
		+ (form.peso_distintas[p]   * varInsat.insat_distintas[p])
		+ (form.peso_manha_noite[p] * varInsat.insat_manha_noite[p])
		+ (form.peso_janelas[p]     * varInsat.insat_janelas[p])
	))

	# @contraint(mod, insat_def[p in conj.P], insat[p] == insat_disciplinas[p])

	maxx = [p for p in conj.P if !(p in conj.P_OUT)]
	@constraint(mod, max_das_insat_def[p in maxx], var.max_das_insat >= var.insat[p])

end

function alforria(
	conj:: ConjuntosAlforria,
	sar:: ParametrosSAR,
	form:: ParametrosFormulario,
	conv::ParametrosConvencionados,
    opt::OptmizerOptions)



    # alforria_mod = Model(HiGHS.Optimizer)

    # set_attribute(alforria_mod, "parallel", "on")
    # set_attribute(alforria_mod, "presolve", "on")
    # set_attribute(alforria_mod, "mip_rel_gap", 0.6)
    # set_attribute(alforria_mod, "time_limit", 7200.0)
    # set_attribute(alforria_mod, "solution_file", "alforria.sol")
    # set_attribute(alforria_mod, "write_solution_to_file", true)
    # set_attribute(alforria_mod, "mip_heuristic_effort", 1.0)

    # alforria_mod = Model(Gurobi.Optimizer)

    # set_attribute(alforria_mod, "TimeLimit", opt.cputime)
    # set_attribute(alforria_mod, "MIPGap", opt.mip_gap)
    # set_attribute(alforria_mod, "ResultFile", opt.solfile)
    # set_attribute(alforria_mod, "Threads", opt.threads)

    #     turma_grupo_in = Dict{String, String}( t => "__NOGROUP__" for t in T)
    # push!(turma_grupo_in, turma_grupo...)

    # G_in = Set{String}(["__NOGROUP__"])
    # push!(G_in, G...)

	preencheSAR!(sar, conj)
	preencheFormulario!(sar, form, conj, conv)

	alforria_mod = Model(HiGHS.Optimizer)
	
	deriv = parametrosDerivados(conj, form, sar, conv)

	var = declaraVariaveis!(alforria_mod, conj)

	adicionaRestricoesEssenciais!(alforria_mod, conj, form, sar, deriv, conv, var)
	defineVariaveisDemanda!(alforria_mod, conj, form, sar, deriv, conv, var)
	defineVariaveisAuxiliares!(alforria_mod, conj, form, sar, deriv, var)

	varInsat = defineRestricoesVariaveis!(alforria_mod, conj, form, sar, deriv, conv, var)

	defineInsatisfacao!(alforria_mod, conj, deriv, form, var, varInsat)

# if fobj == :fobj1

#         @objective(alforria_mod, Min,
#         	max_das_insat +
#         	1000000 * gap_ch_graduacao + 
#             10000   * gap_horario_max +
#             100     * gap_ch_tt
#         )

#     elseif fobj == :fobj2

#         @objective(alforria_mod, Min,
#            (1 / length(P)) * sum(insat[p] for p in setdiff(P, P_OUT), init = 0) +
#         	1000000 * gap_ch_graduacao + 
#             10000   * gap_horario_max +
#             100     * gap_ch_tt
#         )

	return alforria_mod, var, varInsat

end



# mod, x = alforria(;T=T, P=P, G=G, T_PRE=T_PRE,
#                   chmax_efetivo_anual=chmax_efetivo_anual, chmax_efetivo_semestral=chmax_efetivo_semestral,
#                   chmax_temporario_anual=chmax_temporario_anual, chmax_temporario_semestral=chmax_temporario_semestral,
#                   chmin_efetivo_anual=chmin_efetivo_anual, chmin_temporario_anual=chmin_temporario_anual, chmin_graduacao=chmin_graduacao,
#                   pre_atribuida=pre_atribuida,
#                   c=c, ch=ch, ch1=ch1, ch2=ch2, vinculadas=vinculadas, turma_grupo,
#                   temporario=temporario, chprevia1=chprevia1, chprevia2=chprevia2, licenca=licenca,
#                   peso_disciplinas=peso_disciplinas, peso_numdisc=peso_numdisc, peso_cargahor=peso_cargahor,
#                   peso_horario=peso_horario, peso_distintas=peso_distintas, peso_manha_noite=peso_manha_noite, peso_janelas=peso_janelas,
#                   inapto=inapto,
#                   pref_grupo=pref_grupo, pref_hor=pref_hor, pref_janelas=pref_janelas, impedimento=impedimento,
#                   chmax=chmax, chmax1=chmax1, chmax2=chmax2, chesp_efetivo_anual=chesp_efetivo_anual, chesp_temporario_anual=chesp_temporario_anual
#                   )

# optimize!(mod)