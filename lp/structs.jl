
	struct ConjuntosAlforria
		P :: Set{String}        # professores
		T :: Set{String}        # turmas
		D :: UnitRange{Int64}   # dias
		H :: UnitRange{Int64}   # horários
		S :: UnitRange{Int64}   # semestres
		G :: Set{String}        # grupos
		TURNOS :: UnitRange{Int64}
		G_CANONICOS :: Set{String}
		T_PRE :: Set{String}
		P_OUT :: Set{String}
	end

	struct ParametrosSAR
		c   :: Set{Tuple{String, Int64, Int64, Int64}}  # horários das turmas
		ch  :: Dict{String, Int64}                       # carga horária total
		ch1 :: Dict{String, Int64}                       # carga horária semestre 1
		ch2 :: Dict{String, Int64}                       # carga horária semestre 2
		vinculadas   :: Set{Tuple{String, String}}
		turma_grupo  :: Dict{String, String}
	end

	struct ParametrosFormulario
		temporario      :: Set{String}
		chprevia1       :: Dict{String, Int64}
		chprevia2       :: Dict{String, Int64}
		licenca         :: Set{Tuple{String, Int64}}
		pre_atribuida   :: Set{Tuple{String, String}}
		inapto          :: Set{Tuple{String, String}}
		pref_grupo      :: Dict{Tuple{String, String}, Float64}
		pref_hor        :: Dict{Tuple{String, Int64, Int64}, Float64}
		pref_janelas    :: Set{String}
		impedimento     :: Set{Tuple{String, Int64, Int64, Int64}}
		peso_disciplinas :: Dict{String, Int64}
		peso_numdisc     :: Dict{String, Int64}
		peso_cargahor    :: Dict{String, Int64}
		peso_horario     :: Dict{String, Int64}
		peso_distintas   :: Dict{String, Int64}
		peso_manha_noite :: Dict{String, Int64}
		peso_janelas     :: Dict{String, Int64}
		chmax  :: Dict{String, Int64}
		chmax1 :: Dict{String, Int64}
		chmax2 :: Dict{String, Int64}
		chmin  :: Dict{String, Int64}
	end

	struct ParaisoInfernoCustoMarginal
		paraiso :: Dict{Bool, Int64}
		inferno :: Dict{Bool, Int64}
		customarginal :: Dict{Bool, Float64}
	end

	struct ParametrosConvencionados
		chmax_efetivo_anual			:: Int64
		chmax_efetivo_semestral		:: Int64
		chmax_temporario_anual		:: Int64
		chmax_temporario_semestral	:: Int64
		chmax_diaria				:: Int64
		chmin_efetivo_anual			:: Int64
		chmin_temporario_anual		:: Int64
		
		chmin_graduacao				:: Int64
		numdiscmax_temporario		:: Int64

		cargahor					:: ParaisoInfernoCustoMarginal
		numdisc						:: ParaisoInfernoCustoMarginal
		distintas					:: ParaisoInfernoCustoMarginal
		trn_cheios					:: ParaisoInfernoCustoMarginal
		turnos						:: ParaisoInfernoCustoMarginal

		chesp_efetivo_anual			:: Int64
		chesp_temporario_anual		:: Int64
	end

	struct ParametrosDerivados
		chprevia_tt     :: Dict{String, Int64}
		prop            :: Dict{String, Float64}
		pref_turma      :: Dict{Tuple{String, String}, Float64} 
		horario_turno   :: Dict{Int64, Int64}
		semestralidade  :: Set{Tuple{String, Int64}}
		ajuste_hor      :: Dict{String, Float64}
		chprevia_total  :: Int64
		chesp           :: Dict{String, Int64}
		peso_total_inv  :: Dict{String, Float64}
	end

	struct Variaveis
		max_das_insat		#  Maximo das insatisfações
		insat				# insat[P] - Insatisfação de cada professor
		ch_atendida			# Carga horária atendida
		gap_ch_tt			# Mínimo da ch pretendida e ch atendida
		gap_horario_max		# Máximo dos gaps entre a carga horária do professor e seu limite mínimo legal.
		gap_ch_graduacao	# Maximo dos gaps entre a carga horaria minima da graduacao e a realizada

		x					# 1 se o professor P é alocado na turma T

		lec_grp				# 1 se o professor P leciona displina do grupo G no semestre S
		lec_trn				# Indica se P leciona no semestre S, dia D, turno TURNOS
		trn_cheio			# O respectivo turno é cheio
		
		noite				# p leciona a noite em s
		manha				# p leciona de manha em s
		noitext				# p leciona no extremo da noite em s
		manhaxt				# p leciona no extremo da manha em s
		mnh_nt				# p leciona na manha e noite em s
		mnh_ntxt			# p leciona na manha e extremo da noite em s
		nt_mnhxt			# p leciona na noite e extremo da manha em s

	end

	struct VariaveisInsat
		carga_horaria
		numero_de_disciplinas
		insat_disciplinas
		insat_cargahor
		insat_numdisc
		insat_horario
		insat_distintas
		insat_manha_noite
		insat_janelas
	end
