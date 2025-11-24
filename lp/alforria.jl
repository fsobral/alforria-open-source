using JuMP, HiGHS
using Gurobi


"""
    _cria_ch_s(P, chmaxs, S, licenca, temporario, chmax_temporario_semestral, chmax_efetivo_semestral)

    Função auxiliar para criar carga horaria semestral. `S` deve ser 1 ou 2.
"""
function _cria_ch_s(P, chmaxs, s, licenca, temporario, chmax_temporario_semestral, chmax_efetivo_semestral)

    chmaxs_in = Dict(p => ((p, s) in licenca ? 0 : (p in temporario ? chmax_temporario_semestral : chmax_efetivo_semestral)) for p in P)
    for (p, i) in chmaxs
        chmaxs_in[p] = i
    end

    return chmaxs_in

end


function alforria(;
########################    CONJUNTOS    ###################
#* dá pra transformar esses primeiros em obrigatórios antes do ponto e vírgula (;)
#* porém, não será possível chamar a função com o nome deles
    P :: Set{String} = Set{String}(),
    T :: Set{String} = Set{String}(),
    D :: UnitRange{Int64} = 2:7,
    H :: UnitRange{Int64} = 1:16, 
    S :: UnitRange{Int64} = 1:2, 
    G :: Set{String} = Set{String}(),
    TURNOS :: UnitRange{Int64} = 1:3,
    G_CANONICOS :: Set{String} = Set{String}(),
    T_PRE :: Set{String} = Set{String}(),
    P_OUT :: Set{String} = Set{String}(),
    
    
#########################    PARÂMETROS      VARIÁVEIS    ##########################
    
    insatisfacao_almejada = 2,

###########################   PARÂMETROS      CONVENCIONADOS    ##########################
    chmax_efetivo_anual :: Int64 = 20,
    chmax_efetivo_semestral :: Int64 = 12,
    chmax_temporario_anual :: Int64 = 40,
    chmax_temporario_semestral :: Int64 = 22,
    chmax_diaria :: Int64 = 8,
    chmin_efetivo_anual :: Int64 = 16,
    chmin_temporario_anual :: Int64 = 24,
    chmin_graduacao :: Int64 = 8,
    numdiscmax_temporario :: Int64 = 8,


##########################    PARÂMETROS DE ORIGENS DIVERSAS        #######################

    # indica se a turma t está pré atribuída ao professor p
    pre_atribuida :: Set{Tuple{String, String}} = Set{Tuple{String, String}}(),


##########################   PARÂMETROS          SAR     ##############################

    # Indica se a turma t tem aula no semestre s, dia d, horario h 
    c :: Set{Tuple{String, Int64, Int64, Int64}} = Set{Tuple{String, Int64, Int64, Int64}}(), # [0 for t in T, s in S, d in D, h in H]
    # Carga horaria total de uma turma (horas/semana)
    ch :: Dict{String, Int64} = Dict{String, Int64}(), 
    # Carga horaria no primeiro semestre (horas/semana)
    ch1 :: Dict{String, Int64} = Dict{String, Int64}(), 
    # Carga horaria no segundo semestre (horas/semana)
    ch2 :: Dict{String, Int64} = Dict{String, Int64}(), 
    # Vincula a disciplina no primeiro semestre a ela mesma no segundo 
    vinculadas :: Set{Tuple{String, String}} = Set{Tuple{String, String}}(),
    # Indica se a turma t esta no grupo G (não é coletado do sar mas informado pelo programa que faz a coleta)
    turma_grupo :: Dict{String, String} = Dict{String, String}(), 

##########################	PARÂMETROS   DE    FORMULÁRIO	   ##########################

    # só os professores temporarios estão em temporario
    temporario :: Set{String} = Set{String}(),
    # professor p => horas 
    chprevia1 :: Dict{String, Int64} = Dict{String, Int64}(),
    chprevia2 :: Dict{String, Int64} = Dict{String, Int64}(),
    
    licenca :: Set{Tuple{String, Int64}} = Set{Tuple{String, Int64}}(),
    
    peso_disciplinas :: Dict{String, Int64} = Dict{String, Int64}(),
    peso_numdisc     :: Dict{String, Int64} = Dict{String, Int64}(),
    peso_cargahor    :: Dict{String, Int64} = Dict{String, Int64}(),
    peso_horario     :: Dict{String, Int64} = Dict{String, Int64}(),
    peso_distintas   :: Dict{String, Int64} = Dict{String, Int64}(),
    peso_manha_noite :: Dict{String, Int64} = Dict{String, Int64}(),
    peso_janelas     :: Dict{String, Int64} = Dict{String, Int64}(),

    # O professor P é inapto a lecionar para o grupo G
    inapto :: Set{Tuple{String, String}} = Set{Tuple{String, String}}(),

    # Parametro de preferencia de um professor por lecionar em um grupo
    #! Modificar as preferencias de INT para FLOAT
    pref_grupo :: Dict{Tuple{String, String}, Float64} = Dict{Tuple{String, String}, Float64}(),
    # Parametro de preferencia de um professor por lecionar em um horario
    pref_hor :: Dict{Tuple{String, Int64, Int64}, Float64} = Dict{Tuple{String, Int64, Int64}, Float64}(),
    # Prefere janelas está, prefere não ter janelas não está
    pref_janelas :: Set{String} = Set{String}(), 
    # O professor nao pode lecionar no horario dado por S, D e H 
    impedimento :: Set{Tuple{String, Int64, Int64, Int64}} = Set{Tuple{String, Int64, Int64, Int64}}(), 


############################    PARÂMETROS DEPENDENTES - COM EXCEÇÕES         ########################
    # Carga horaria maxima anual de um professor (horas/semana)
    chmax :: Dict{String, Int64} = Dict{String, Int64}(),

    # Carga horaria maxima no primeiro semestre (horas/semana)
    chmax1 :: Dict{String, Int64} = Dict{String, Int64}(),
    
    # Carga horaria maxima no segundo semestre (horas/semana)
    chmax2 :: Dict{String, Int64} = Dict{String, Int64}(),

    # Carga horaria minima anual (horas/semana)
    chmin :: Dict{String, Int64} = Dict{String, Int64}()
    )

################! Corpo da função
    # alforria_mod = Model(HiGHS.Optimizer)
    alforria_mod = Model(Gurobi.Optimizer)

###########################   PARÂMETROS      CONVENCIONADOS    ##########################
    # false: efetivo -- true: temporario
    
    paraiso_cargahor = Dict(k => 9k + 8 for k in [false, true]) # 8, 16 
    inferno_cargahor = Dict(k => 10 + 11*k for k in [false, true]) # 12, 20 

    paraiso_numdisc = Dict(k => 2 + k for k in [false, true]) # 2, 3
    inferno_numdisc = Dict(k => 4 + k for k in [false, true]) # 4, 5

    paraiso_distintas = Dict(k => 1 + k for k in [false, true]) # 1, 2
    inferno_distintas = Dict(k => 3 + k for k in [false, true]) # 3, 4

    paraiso_trn_cheios = Dict(k => 0 + k for k in [false, true]) #  0, 1
    inferno_trn_cheios = Dict(k => 2 + 3k for k in [false, true]) # 2, 5

    paraiso_turnos = Dict(k => 2 + 3k for k in [false, true]) # 2, 5
    inferno_turnos = Dict(k => 4 + 6k for k in [false, true]) # 4, 10


##########################   PARÂMETROS          SAR     ##############################

    ch_in = Dict(t => sum(1 for s in S, d in D, h in H if (t, s, d, h) in c) for t in T)
    for (t, i) in ch
        ch[t] = i
    end

    ch1_in = Dict(t => sum(Int64[1 for d in D, h in H if (t, S[1], d, h) in c]) for t in T)
    for (t, i) in ch1
        ch1_in[t] = i
    end

    ch2_in = Dict(t => sum(Int64[1 for d in D, h in H if (t, S[2], d, h) in c]) for t in T)
    for (t, i) in ch2
        ch2_in[t] = i
    end


##########################	PARÂMETROS   DE    FORMULÁRIO	   ##########################

    chprevia1_in = Dict(p => 0 for p in P)
    for (p, i) in chprevia1
        chprevia1_in[p] = i
    end
    
    chprevia2_in = Dict(p => 0 for p in P)
    for (p, i) in chprevia2
        chprevia2_in[p] = i
    end

    peso_disciplinas_in = Dict(p => 0 for p in P)
    for (p, i) in peso_disciplinas
        peso_disciplinas[p] = i
        end

    peso_numdisc_in     = Dict(p => 5 for p in P)
    for (p, i) in peso_numdisc
        peso_numdisc_in[p] = i
        end
    peso_cargahor_in    = Dict(p => 5 for p in P)
    for (p, i) in peso_cargahor
        peso_cargahor_in[p] = i
        end
    peso_horario_in     = Dict(p => 5 for p in P)
    for (p, i) in peso_horario
        peso_horario_in[p] = i
        end
    peso_distintas_in   = Dict(p => 5 for p in P)
    for (p, i) in peso_distintas
        peso_distintas_in[p] = i
        end
    peso_manha_noite_in = Dict(p => 5 for p in P)
    for (p, i) in peso_manha_noite
        peso_manha_noite_in[p] = i
        end
    peso_janelas_in     = Dict(p => 5 for p in P)
    for (p, i) in peso_janelas
        peso_janelas_in[p] = i
        end
    
    chprevia_tt = Dict(p => (chprevia1_in[p]  + chprevia2_in[p]) for p in P)

    prop =  Dict(p => (0.5*(2 - ((p, 1) in licenca) - ((p,2) in licenca))) for p in P)

    for p in P, g in G
        if ((p, g) in inapto && (sum((p, t) in pre_atribuida for t in T if turma_grupo[t] == g) >= 1))
            delete!(inapto, (p, g))
        end
    end

    pref_grupo_in = Dict((p, g) => 0 for p in P, g in G)
    for ((p, g), i) in pref_grupo
        pref_grupo_in[(p, g)] = i
    end
    
    pref_hor_in = Dict((p, d, h) => 5 for p in P, d in D, h in H)
    for ((p, d, h), i) in pref_hor
        pref_hor_in[(p, d, h)] = i
    end


############################    PARÂMETROS DEPENDENTES - COM EXCEÇÕES         ########################

    chmax_in = Dict(p => (p in temporario ? 
    (((p, 1) in licenca) + ((p, 2) in licenca) == 0 ? chmax_temporario_anual : chmax_temporario_semestral) : 
    (((p, 1) in licenca) + ((p, 2) in licenca) == 0 ? chmax_efetivo_anual : chmax_efetivo_semestral)) 
    for p in P)
    for (p, i) in chmax
        chmax_in[p] = i
    end


    chmax1_in = _cria_ch_s(P, chmax1, 1, licenca, temporario, chmax_temporario_semestral, chmax_efetivo_semestral)

    # chmax1_in = Dict(p => ((p, 1) in licenca ? 0 : (p in temporario ? chmax_temporario_semestral : chmax_efetivo_semestral)) for p in P)
    # for (p, i) in chmax1
    #     chmax1_in[p] = i
    # end

    chmax2_in = _cria_ch_s(P, chmax2, 2, licenca, temporario, chmax_temporario_semestral, chmax_efetivo_semestral)

    # chmax2_in = Dict(p => ((p, 2) in licenca ? 0 : (p in temporario ? chmax_temporario_semestral : chmax_efetivo_semestral)) for p in P)
    # for (p, i) in chmax2
    #     chmax2_in[p] = i
    # end

    chmin_in = Dict(p => (p in temporario ? 
    (((p, 1) in licenca) + ((p, 2) in licenca) == 0 ? chmin_temporario_anual : chmin_temporario_anual/2) :
    (((p, 1) in licenca) + ((p, 2) in licenca) == 0 ? chmin_efetivo_anual : chmin_efetivo_anual/2))
    for p in P)
    for (p, i) in chmin
        chmin_in[p] = i
    end

###########################    PARÂMETROS DEPENDENTES - SEM EXCEÇÕES        ########################
    
    # Parametro de preferencia de um professor por uma turma (depende dos parametros pre_atribuida, pref_grupo, e turma-grupo) 
    #!! A intuição de pref_turma é que ela dá um valor para a preferência do professor p para a turma t, com base na preferência do seu respectivo grupo.
    # TODO Pensar em como melhorar isso, pois não faz sentido descontar a preferência quando a turma é pre-atribuída
    pref_turma = Dict((p, t) => ((t ∉ keys(turma_grupo)) || (p, turma_grupo[t]) in inapto) ? 0 : pref_grupo_in[p, turma_grupo[t]] for p in P, t in T)

    # Indica se o horário h pertence ao turno u 
    # ! Temos que verificar se u=3 deveria ser com h >= 11 ou h>=14!
    horario_turno = Dict(h => (h <= 5 ? 1 : h <= 10 ? 2 : 3) for h in H)


    customarginal_cargahor   = Dict(k => 5/(inferno_cargahor[k] - paraiso_cargahor[k]) for k in [false, true])
    customarginal_numdisc    = Dict(k => 5/(inferno_numdisc[k] - paraiso_numdisc[k]) for k in [false, true])
    customarginal_distintas  = Dict(k => 5/(inferno_distintas[k] - paraiso_distintas[k]) for k in [false, true])
    customarginal_trn_cheios = Dict(k => 5/(inferno_trn_cheios[k] - paraiso_trn_cheios[k]) for k in [false, true])
    customarginal_turnos     = Dict(k => 5/(inferno_turnos[k] - paraiso_turnos[k]) for k in [false, true])

    # parametro de decisão: se t tem aula no semestre 
    semestralidade = Set([(t, s) for t in T, s in S if sum(((t, s, d, h) in c) for d in D, h in H) >= 1])

    # Ajustes de preferências por horários
    ajuste_hor = Dict(p => sum(pref_hor_in[p, d, h] for d in D, h in H) == 0 ? 0 : 400 / (sum(pref_hor_in[p,d,h] for d in D, h in H)) for p in P)
        

 #########################    PARÂMETROS      DE        CARGA        HORARIA       ##########################

    # Carga horaria maxima que o departamento consegue atender
    # capacidade_departamento_sup = sum(chmax_in[p] for p in P)
    # capacidade_departamento_inf = aproveitamento_minimo*(sum(chmax[p] for p in P)),
    # Carga horária média (esperada)
    chesp_efetivo_anual = 18
    chesp_temporario_anual = 36

    # Carga horária esperada 
    chesp = Dict(p => p in temporario ? 
        chesp_efetivo_anual 
        : ((p, 1) in licenca) + ((p, 2) in licenca) == 0 ?
            chesp_efetivo_anual
            : chesp_efetivo_anual / 2
    for p in P)

    # Carga horária esperada total
    
    # chesp_tt = sum(chesp[p] for p in P)
    chprevia_total = sum(chprevia_tt[p] for p in P)

    # Carga horária de todas as disciplinas somadas
    # demanda_de_ch = sum(ch_in[t] for t in T) + chprevia_total
    
    
#############################    COEFICIENTES DA FUNÇÃO INSTISFAÇÃO    ##########################
    peso_total_inv = Dict(p => 
    (1/ (peso_disciplinas_in[p]+peso_numdisc_in[p]+peso_cargahor_in[p]+peso_horario_in[p]
    +peso_distintas_in[p]+peso_manha_noite_in[p]+peso_janelas_in[p])) for p in P)
    

#############################        DECLARAÇÃO DE VARIÁVEIS       ##########################

    @variables(alforria_mod, begin 
    max_das_insat         #  Maximo das insatisfações
    insat[P]              # insat[P] - Insatisfação de cada professor 
    ch_atendida           # Carga horária atendida
    gap_ch_tt             # Mínimo da ch pretendida e ch atendida
    gap_horario_max       # Máximo dos gaps entre a carga horária do professor e seu limite mínimo legal.
    gap_ch_graduacao      # Maximo dos gaps entre a carga horaria minima da graduacao e a realizada 
    end) 

    @variable(alforria_mod, x[P, T], Bin) # 1 se o professor P é alocado na turma T

    @variables(alforria_mod, 
    begin
    lec_grp[P, G, S], Bin               # 1 se o professor P leciona displina do grupo G no semestre S
    lec_trn[P, S, D, TURNOS], Bin    # Indica se P leciona no semestre S, dia D, turno TURNOS
    trn_cheio[P, S, D, TURNOS], Bin  # O respectivo turno é cheio 
    end)

    @variables(alforria_mod, 
    begin
    noite[P, S], Bin        # p leciona a noite em s 
    manha[P, S], Bin        # p leciona de manha em s 
    noitext[P, S], Bin      # p leciona no extremo da noite em s 
    manhaxt[P, S], Bin      # p leciona no extremo da manha em s 
    mnh_nt[P, S], Bin       # p leciona na manha e noite em s
    mnh_ntxt[P, S], Bin     # p leciona na manha e extremo da noite em s
    nt_mnhxt[P, S], Bin     # p leciona na noite e extremo da manha em s
    end)


#############################          RESTRIÇÕES NÃO ESSENCIAIS          ######################

    #Nos dois horarios imediatamente antes e apos uma refeicao, no maximo em apenas um deles um professor leciona
    #=
    for p in P, s in S, d in D
        @constraint(alforria_mod, sum(x[p, t] * c[t, s, d, 5] + x[p, t] * c[t, s, d, 6] for t in T if !(t in T_PRE)) <= 1) # rest10_1
        @constraint(alforria_mod, sum(x[p, t] * c[t, s, d, 10] + x[p, t] * c[t, s, d, 11] for t in T if t ∉ T_PRE) <= 1) # rest10_2
    end
    =#


############################# 	DEFINIÇÃO DE VARIÁVEIS DE DEMANDA      ##########################

    previa_liquida = Dict(p => (chprevia1_in[p] + chprevia2_in[p] + sum(((p, t) in pre_atribuida)*ch_in[t] for t in T)) for p in P)
    
    capacidade_pessoal = Dict(p => p in temporario ?
    max(previa_liquida[p], chesp_temporario_anual)
    : max(previa_liquida[p], chesp_efetivo_anual)
    for p in P)

    capacidade_total = sum(capacidade_pessoal[p] for p in P) - chprevia_total
    
    demanda = sum(ch_in[t] for t in T)

    @constraint(alforria_mod, def_gap_ch_tt1, gap_ch_tt >= min(demanda, capacidade_total) - sum(ch_in[t] * x[p, t] for t in T, p in P)) #blablabla - oferta
    @constraint(alforria_mod, def_gap_ch_tt2, gap_ch_tt >= 0)
    @constraint(alforria_mod, def_gap_horario_max1[p in P], gap_horario_max >= chmin_in[p] - (chprevia_tt[p] + sum(ch_in[t] * x[p,t] for t in T)))
    @constraint(alforria_mod, def_gap_horario_max2, gap_horario_max >= 0)
    
    licencaP0 = [p for p in P if (((p, 1) in licenca) + ((p, 2) in licenca) == 0)]
    @constraint(alforria_mod, def_gap_ch_grad1[p in licencaP0],
    gap_ch_graduacao >= chmin_graduacao - sum(ch_in[t] * x[p, t] for t in T))
    
    licencaP1 = [p for p in P if (((p, 1) in licenca) + ((p, 2) in licenca) == 1)]
    @constraint(alforria_mod, def_gap_ch_grad2[p in licencaP1],
    gap_ch_graduacao >= (chmin_graduacao / 2) - sum(ch_in[t] * x[p, t] for t in T))
    
    @constraint(alforria_mod, def_gap_ch_grad3, gap_ch_graduacao >= 0)
    


############################       DEFINIÇÃO DE VARIÁVEIS AUXILIARES        ###########################
    @constraint(alforria_mod, def_lec_grp_inapto[(p, g) in inapto, s in S], lec_grp[p, g, s] == 0)

    inapto0 = [(p, g) for p in P, g in G if !((p, g) in inapto)]
    @constraint(alforria_mod, def_lec_grp_up[(p, g) in inapto0, s in S],
                lec_grp[p, g, s] <= sum((g == turma_grupo[t])*x[p,t] for t in T if (t, s) in semestralidade))
    down = [(p, g, t, s) for (p, g) in inapto0, (t, s) in semestralidade if  (g == turma_grupo[t])]
    @constraint(alforria_mod, def_lec_grp_down[(p, g, t, s) in down],
                lec_grp[p,g,s] >= x[p,t])
    
    # Definicao da variavel auxiliar lec_trn (Indica se p leciona so memestre s, dia d, turno u)
    @constraint(alforria_mod, def_lec_trn_up[p in P, s in S, d in D, u in TURNOS],
                lec_trn[p,s,d,u] <= sum(x[p,t] for t in T, h in H if (u == horario_turno[h] && (t,s,d,h) in c)))
    downt = [(p, s, t, d, h, horario_turno[h]) for p in P, s in S, t in T, d in D, h in H if (t, s, d, h) in c]
    @constraint(alforria_mod, def_lec_trn_down[(p, s, t, d, h, u) in downt],
                lec_trn[p,s,d,u] >= x[p,t])

    # Definicao da variavel auxiliar trn_cheio (Indica se p leciona so memestre s, dia d, turno u) 
    @constraint(alforria_mod, def_trn_cheio_up[p in P, s in S, d in D, u in TURNOS],
                4 * trn_cheio[p,s,d,u] <= sum(x[p,t] for t in T, h in H if u == horario_turno[h] && (t,s,d,h) in c))
    @constraint(alforria_mod, def_trn_cheio_down[p in P, s in S, d in D, u in TURNOS],
                trn_cheio[p,s,d,u] >= -3 + 0.5*sum(x[p,t] for t in T, h in H if (u == horario_turno[h] && (t,s,d,h) in c)))
     
    # Manha[p,s] : p leciona pela manha em s 
    @constraint(alforria_mod, def_manha_up[p in P, s in S], manha[p,s] <= sum(lec_trn[p,s,d,1] for d in D))
    @constraint(alforria_mod, def_manha_low[p in P, s in S, d in D], manha[p,s] >= lec_trn[p,s,d,1])

    # Noite[p,s] : p leciona pela noite em s 
    @constraint(alforria_mod, def_noite_up[p in P, s in S], noite[p,s] <= sum(lec_trn[p,s,d,3] for d in D))
    @constraint(alforria_mod, def_noite_low[p in P, s in S, d in D], noite[p,s] >= lec_trn[p,s,d,3])
    
    # noitext[p,s]: p leciona no extremo da noite em s
    #! Atenção que o horário extremo é 15-16 e não 13-14
    @constraint(alforria_mod, def_noitext_up[p in P, s in S],
    noitext[p,s] <= sum(((t,s,d,13) in c) * x[p,t] + ((t,s,d,14) in c) * x[p,t] for t in T, d in D))
    @constraint(alforria_mod, def_noitext_down[p in P, s in S],
    12 * noitext[p,s] >= sum(((t,s,d,13) in c) * x[p,t] + ((t,s,d,14) in c) * x[p,t] for t in T, d in D))

    # manhaxt[p,s]: p leciona no extremo da manha em s (horario 1 ou 2)
    @constraint(alforria_mod, def_manhaxt_up[p in P, s in S],
    manhaxt[p,s] <= sum(((t,s,d,1) in c) * x[p,t] + ((t,s,d,2) in c) * x[p,t] for t in T, d in D))
    @constraint(alforria_mod, def_manhaxt_down[p in P, s in S],
    12 * manhaxt[p,s] >= sum(((t,s,d,1) in c) * x[p,t] + ((t,s,d,2) in c) * x[p,t] for t in T, d in D))

    # mnh_nt[p,s] pe leciona de manha E de noite em s 
    @constraint(alforria_mod, def_mnh_nt_1[p in P, s in S], mnh_nt[p,s] <= manha[p,s])
    @constraint(alforria_mod, def_mnh_nt_2[p in P, s in S], mnh_nt[p,s] <= noite[p,s])
    @constraint(alforria_mod, def_mnh_nt_3[p in P, s in S], mnh_nt[p,s] >= manha[p,s] + noite[p,s] - 1)

    # mnh_ntxt[x,p]: p leciona na manha e extremo da noite noite em s
    @constraint(alforria_mod, def_mnh_ntxt_1[p in P, s in S], mnh_ntxt[p,s] <= mnh_nt[p,s])
    @constraint(alforria_mod, def_mnh_ntxt_2[p in P, s in S], mnh_ntxt[p,s] <= noitext[p,s])
    @constraint(alforria_mod, def_mnh_ntxt_3[p in P, s in S], mnh_ntxt[p,s] >= mnh_nt[p,s] + noitext[p,s] - 1)

    # nt_mnhxt[x,p]: p leciona na noite e extremo da manha em s
    @constraint(alforria_mod, def_nt_mnhxt_1[p in P, s in S], nt_mnhxt[p,s] <= mnh_nt[p,s])
    @constraint(alforria_mod, def_nt_mnhxt_2[p in P, s in S], nt_mnhxt[p,s] <= manhaxt[p,s])
    @constraint(alforria_mod, def_nt_mnhxt_3[p in P, s in S], nt_mnhxt[p,s] >= mnh_nt[p,s] + manhaxt[p,s] - 1)
    

#########################      RESTRIÇÕES  ESSENCIAIS       ############################

    # Um professor nao leciona em duas turmas ao mesmo tempo
    @constraint(alforria_mod, rest1[p in P, s in S, d in D, h in H],
    sum(((t,s,d,h) in c) * x[p,t] for t in T) <= 1)

    # Professores inaptos nao ministram as respectivas disciplinas
    restt2 = [(p, t) for p in P, t in T if (t ∈ keys(turma_grupo)) && ((p, turma_grupo[t]) in inapto)]
    @constraint(alforria_mod, rest2[(p, t) in restt2], x[p,t] == 0)

    # Cada turma tem, no maximo, um professor #
    @constraint(alforria_mod, rest3[t in T], 
    sum(x[p,t] for p in P) <= 1) #------------------------------------------------------------------------FORÇANDO TODOS

    # Limita superiormente a carga horaria anual e semestral de um professor 
    @constraint(alforria_mod, rest4_1[p in P], 
    chprevia_tt[p] + sum(ch_in[t]*x[p,t] for t in T) <= max(0, chmax_in[p]))

    @constraint(alforria_mod, rest4_2[p in P],
    chprevia1_in[p] + sum(ch1_in[t]*x[p,t] for t in T) <= max(0,chmax1_in[p]))

    @constraint(alforria_mod, rest4_3[p in P],
    chprevia2_in[p] + sum(ch2_in[t]*x[p,t] for t in T) <= max(0,chmax2_in[p]))

    # Limita inferiormente a carga horaria anual de um professor 
    # @constraint(alforria_mod, rest5[p in P], chprevia_tt[p] + sum(ch_in[t]*x[p,t] for t in T) >= chmin_in[p])
    # ! Lembrar de retirar isso na hora de entrar em produção!!
    @constraint(alforria_mod, rest5[p in P], sum(ch_in[t]*x[p,t] for t in T) >= 1)

    # Professor nao pode dar aulas em horarios conflitantes com outras atividades
    rett6 = [(p, t, s, d, h) for p in P, t in T, s in S, d in D, h in H if ((p,s,d,h) in impedimento && (t,s,d,h) in c)]
    @constraint(alforria_mod, rest6[(p,t,s,d,h) in rett6], x[p,t] == ((p,t) in pre_atribuida)) #? pode dar problema??

    # Deve haver um intervalo maior ou igual que 11h entre jornadas de trabalho em dias consecutivos
    #! Verificar se precisa ir até 7
    rett7 = [(p,d,s,h1,h2) for p in P, d in 2:6, s in S, h1 in 14:16, h2 in 1:3 if h1 - h2 >= 13]
    @constraint(alforria_mod, rest7[(p, d, s, h1, h2) in rett7],
    sum(((t,s,d,h1) in c) * x[p,t] for t in T if !(t in T_PRE)) + sum(((t,s,d + 1,h2) in c) * x[p,t] for t in T if !(t in T_PRE)) <= 1)
    
    # Respeita as disciplinas pre-atribuidas
    @constraint(alforria_mod, rest8[(p,t) in pre_atribuida], x[p,t] == 1)
    
    # Maximo de horas de aula diarias
    @constraint(alforria_mod, rest9[p in P, s in S, d in D], sum(x[p,t] * ((t,s,d,h) in c) for t in T, h in H) <= chmax_diaria)
    
    # Vincula as duas metades de uma disciplina anual
    @constraint(alforria_mod, rest10[p in P, (t1, t2) in vinculadas], x[p,t1] == x[p,t2])
    
    # Maximo de numero de disciplinas para temporarios
    @constraint(alforria_mod, rest11[p in temporario], sum(x[p,t] for t in T) <= numdiscmax_temporario)
    
    # Maximo de numero de grupos para temporarios
    @constraint(alforria_mod, rest12[p in temporario, s in S], sum(lec_grp[p,g,s] for g in G) <= 2)
    


    
#################################       RESTRIÇÕES   VARIÁVEIS        ##################################

    # @constraint(alforria_mod, capacidade_inf, sum(x[p,t]*ch_in[t] for p in P, t in T) >= min(capacidade_departamento_inf,demanda_de_ch)) 
    # @constraint(alforria_mod, capacidade_sup, sum(x[p,t]*ch_in[t] for p in P, t in T) <= capacidade_departamento_sup)
    
#########################################################################################################

################       RESTRICAO DE INSATISFACAO MAXIMA PARA ALGUNS PROFESSORES       ###################

    ub_insat = Dict(p => 100 for p in P) #? qual a utilidade se todo ub é 100?

    @constraint(alforria_mod, limitante_insatisfacao[p in P],
    insat[p] <= ub_insat[p])

#########################################################################################################

    @variable(alforria_mod, carga_horaria[P])
    @variable(alforria_mod, numero_de_disciplinas[P])
    @variable(alforria_mod, insat_disciplinas[P])
    @variable(alforria_mod, insat_cargahor[P])
    @variable(alforria_mod, insat_numdisc[P])
    @variable(alforria_mod, insat_horario[P])
    @variable(alforria_mod, insat_distintas[P])
    @variable(alforria_mod, insat_manha_noite[P])
    @variable(alforria_mod, insat_janelas[P])

    @constraint(alforria_mod, def_carga_horaria[p in P], carga_horaria[p] == sum(ch_in[t]*x[p,t] for t in T) + chprevia_tt[p])
    @constraint(alforria_mod, def_numero_de_disciplinas[p in P], numero_de_disciplinas[p] == sum(x[p,t] for t in T))

    @constraint(alforria_mod, def_insat_disciplinas[p in P], insat_disciplinas[p] ==
    (1/chesp[p]) * sum(pref_turma[p, t] * ch_in[t]*x[p,t] for t in T))

    @constraint(alforria_mod, def_insat_cargahor[p in P], insat_cargahor[p] ==
    customarginal_cargahor[p in temporario] * ((sum(ch_in[t]*x[p,t] for t in T) + chprevia_tt[p])-2*paraiso_cargahor[p in temporario]))

    @constraint(alforria_mod, def_insat_numdisc[p in P], insat_numdisc[p] ==
    customarginal_numdisc[p in temporario] * ((sum(x[p, t] for t in T) + (chprevia_tt[p] / 6) - 2 * paraiso_numdisc[p in temporario])))

    @constraint(alforria_mod, def_insat_horario[p in P], insat_horario[p] ==
    ajuste_hor[p] * (1 / chesp[p]) * sum(((t,s,d,h) in c)*pref_hor_in[p,d,h]*x[p,t] for t in T, s in S, d in D, h in H))
    
    @constraint(alforria_mod, def_insat_distintas[p in P], insat_distintas[p] ==
    customarginal_distintas[p in temporario] * ((sum(lec_grp[p,g,s] for g in G, s in S) + (chprevia_tt[p]/6))-2*paraiso_distintas[p in temporario]))

    @constraint(alforria_mod, def_insat_manha_noite[p in P], insat_manha_noite[p] == 5*(mnh_nt[p,1]+mnh_nt[p,2]))

    @constraint(alforria_mod, def_insat_janelas[p in P],
    insat_janelas[p] == (p in pref_janelas) * customarginal_trn_cheios[p in temporario]*
    (sum(trn_cheio[p,s,d,u] for s in S, d in D, u in TURNOS) - 2*paraiso_trn_cheios[p in temporario])
    +(1-(p in pref_janelas)) * customarginal_turnos[p in temporario]*
    (sum(lec_trn[p,s,d,u] for s in S, d in D, u in TURNOS) - 2 * paraiso_turnos[p in temporario]))


#############################    MAZELAS DAS PREATRIBUIDAS     ###############################

    # @variable(alforria_mod, mazela)
    # @constraint(alforria_mod, def_mazela, mazela == sum(((p,t) in pre_atribuida )* (1 - x[p,t]) for p in P, t in T))


# ###############################         INSATISFACAO DEFINICAO         ####################

    #Escala aproximada de zero a 10
    @constraint(alforria_mod, insat_def[p in P], insat[p] ==
    (1 - 0.2*(p in temporario)) * peso_total_inv[p] * (1/prop[p]) * ( 
          (peso_disciplinas_in[p] * insat_disciplinas[p]) 
        + (peso_cargahor_in[p]    * insat_cargahor[p]) 
        + (peso_numdisc_in[p]     * insat_numdisc[p])
        + (peso_horario_in[p]     * insat_horario[p])
        + (peso_distintas_in[p]   * insat_distintas[p])
        + (peso_manha_noite_in[p] * insat_manha_noite[p])
        + (peso_janelas_in[p]     * insat_janelas[p])
    ))

    # @contraint(alforria_mod, insat_def[p in P], insat[p] == insat_disciplinas[p])

    maxx = [p for p in P if !(p in P_OUT)]
    @constraint(alforria_mod, max_das_insat_def[p in maxx], max_das_insat >= insat[p])


############################## COLOCAR A FUNCAO OBJETIVO DESEJADA AQUI #########################


return alforria_mod, x

end

# mod, x = alforria(T=T, P=P, c=c)

# optimize!(mod)