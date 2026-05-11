include("structs.jl")
include("alforria.jl")
using JuMP

# ============================================================
#   INFRAESTRUTURA
# ============================================================

function instancia_base()
    conj = ConjuntosAlforria(
        Set(["P1", "P2"]),
        Set(["T1", "T2", "T3"]),
        2:7, 1:16, 1:2,
        Set(["G1", "G2"]),
        1:3,
        Set(["G1", "G2"]),
        Set{String}(),
        Set{String}()
    )

    sar = ParametrosSAR(
        Set([
            ("T1", 1, 3, 6), ("T1", 1, 3, 7),
            ("T2", 1, 4, 8), ("T2", 1, 4, 9),
            ("T3", 2, 5, 6), ("T3", 2, 5, 7),
        ]),
        Dict{String,Int64}(),
        Dict{String,Int64}(),
        Dict{String,Int64}(),
        Set{Tuple{String,String}}(),
        Dict("T1" => "G1", "T2" => "G1", "T3" => "G2")
    )

    form = ParametrosFormulario(
        Set(["P2"]),
        Dict("P1" => 0, "P2" => 0),
        Dict("P1" => 0, "P2" => 0),
        Set{Tuple{String,Int64}}(),
        Set{Tuple{String,String}}(),
        Set{Tuple{String,String}}(),
        Dict{Tuple{String,String},Float64}(),
        Dict{Tuple{String,Int64,Int64},Float64}(),
        Set{String}(),
        Set{Tuple{String,Int64,Int64,Int64}}(),
        Dict("P1" => 5.0, "P2" => 5.0),
        Dict("P1" => 5.0, "P2" => 5.0),
        Dict("P1" => 5.0, "P2" => 5.0),
        Dict("P1" => 5.0, "P2" => 5.0),
        Dict("P1" => 5.0, "P2" => 5.0),
        Dict("P1" => 5.0, "P2" => 5.0),
        Dict("P1" => 5.0, "P2" => 5.0),
        Dict{String,Int64}(),
        Dict{String,Int64}(),
        Dict{String,Int64}(),
        Dict{String,Int64}()
    )

    conv = defineParametrosConvencionados()

    opt = OptimizerOptions(120.0, 0.01, "solucao.sol", 0, :fobj1)

    return conj, sar, form, conv, opt
end

# DAT base como string — mesma instância, para o GLPK
function dat_base()
    return """
set P := P1 P2;
set T := T1 T2 T3;
set G := G1 G2;
set G_CANONICOS := G1 G2;
set T_PRE := T_DUMMY;
set P_OUT  := P_DUMMY;

param turma_grupo :
        G1  G2 :=
  T1     1   0
  T2     1   0
  T3     0   1
;
param c :=
  [T1,1,3,6] 1  [T1,1,3,7] 1
  [T2,1,4,8] 1  [T2,1,4,9] 1
  [T3,2,5,6] 1  [T3,2,5,7] 1
;
param temporario := P1 0  P2 1 ;
param peso_disciplinas := P1 5  P2 5 ;
param peso_numdisc     := P1 5  P2 5 ;
param peso_cargahor    := P1 5  P2 5 ;
param peso_horario     := P1 5  P2 5 ;
param peso_distintas   := P1 5  P2 5 ;
param peso_manha_noite := P1 5  P2 5 ;
param peso_janelas     := P1 5  P2 5 ;
"""
end

# ============================================================
#   RODAR JULIA
# ============================================================

function rodar_julia(conj, sar, form, conv, opt)
    # Recria cópias mutáveis dos dicts para não contaminar entre testes
    sar2  = ParametrosSAR(
        copy(sar.c), copy(sar.ch), copy(sar.ch1), copy(sar.ch2),
        copy(sar.vinculadas), copy(sar.turma_grupo)
    )
    form2 = ParametrosFormulario(
        copy(form.temporario), copy(form.chprevia1), copy(form.chprevia2),
        copy(form.licenca), copy(form.pre_atribuida), copy(form.inapto),
        copy(form.pref_grupo), copy(form.pref_hor), copy(form.pref_janelas),
        copy(form.impedimento),
        copy(form.peso_disciplinas), copy(form.peso_numdisc), copy(form.peso_cargahor),
        copy(form.peso_horario), copy(form.peso_distintas), copy(form.peso_manha_noite),
        copy(form.peso_janelas),
        copy(form.chmax), copy(form.chmax1), copy(form.chmax2), copy(form.chmin)
    )
    conj2 = ConjuntosAlforria(
        copy(conj.P), copy(conj.T), conj.D, conj.H, conj.S,
        copy(conj.G), conj.TURNOS, copy(conj.G_CANONICOS),
        copy(conj.T_PRE), copy(conj.P_OUT)
    )

    mod, var, _ = alforria(conj2, sar2, form2, conv, opt)
    optimize!(mod)

    status = termination_status(mod)
    if status == MOI.INFEASIBLE || status == MOI.INFEASIBLE_OR_UNBOUNDED
        return Dict("status" => string(status), "obj" => NaN, "x" => Dict())
    end

    alocacao = Dict(
        "$p->$t" => (value(var.x[p,t]) > 0.5 ? 1 : 0)
        for p in conj2.P, t in conj2.T
    )

    return Dict(
        "status"          => string(status),
        "obj"             => round(objective_value(mod), digits=4),
        "gap_ch_tt"       => round(value(var.gap_ch_tt), digits=4),
        "gap_horario_max" => round(value(var.gap_horario_max), digits=4),
        "gap_ch_grad"     => round(value(var.gap_ch_graduacao), digits=4),
        "x"               => alocacao
    )
end

# ============================================================
#   RODAR GLPK
# ============================================================

function rodar_glpk(dat_str::String; mod_file="alforria_restr.mod", fobj_file="fobj1.mod")
    dat_path = tempname() * ".dat"
    write(dat_path, dat_str)

    out = read(`glpsol --math $mod_file --data $dat_path --output /dev/stdout`, String)
    rm(dat_path)

    resultado = Dict{String,Any}()

    # Status
    if occursin("OPTIMAL", out)
        resultado["status"] = "OPTIMAL"
    elseif occursin("INFEASIBLE", out)
        resultado["status"] = "INFEASIBLE"
        resultado["obj"] = NaN
        return resultado
    else
        resultado["status"] = "UNKNOWN"
    end

    # Função objetivo
    m = match(r"obj\s*=\s*([\d.e+\-]+)", out)
    resultado["obj"] = m !== nothing ? round(parse(Float64, m.match[findfirst('=', m.match)+1:end]), digits=4) : NaN

    # Gaps
    for (key, pat) in [
        ("gap_ch_tt",       r"gap_ch_tt\s+\*?\s+([\d.e+\-]+)"),
        ("gap_horario_max", r"gap_horario_max\s+\*?\s+([\d.e+\-]+)"),
        ("gap_ch_grad",     r"gap_ch_graduacao\s+\*?\s+([\d.e+\-]+)"),
    ]
        m2 = match(pat, out)
        resultado[key] = m2 !== nothing ? round(parse(Float64, m2.captures[1]), digits=4) : NaN
    end

    # Alocação x[p,t]
    alocacao = Dict{String,Int}()
    for m3 in eachmatch(r"x\[(\w+),(\w+)\]\s+\*?\s+([\d.]+)", out)
        p, t, v = m3.captures
        alocacao["$p->$t"] = round(Int, parse(Float64, v))
    end
    resultado["x"] = alocacao

    return resultado
end

# ============================================================
#   COMPARAR
# ============================================================

function comparar(nome::String, julia::Dict, glpk::Dict)
    println("\n" * "="^60)
    println("TESTE: $nome")
    println("="^60)

    divergiu = false

    for key in ["status", "obj", "gap_ch_tt", "gap_horario_max", "gap_ch_grad"]
        jv = get(julia, key, "—")
        gv = get(glpk,  key, "—")
        match = isapprox_val(jv, gv)
        flag = match ? "✓" : "✗ DIVERGE"
        println("  $key: Julia=$jv  GLPK=$gv  $flag")
        if !match
            divergiu = true
        end
    end

    # Alocações
    jx = get(julia, "x", Dict())
    gx = get(glpk,  "x", Dict())
    todas = union(keys(jx), keys(gx))
    for k in sort(collect(todas))
        jv = get(jx, k, 0)
        gv = get(gx, k, 0)
        if jv != gv
            println("  x[$k]: Julia=$jv  GLPK=$gv  ✗ DIVERGE")
            divergiu = true
        end
    end

    println(divergiu ? "\n  ⚠ DIVERGÊNCIAS ENCONTRADAS" : "\n  ✓ RESULTADOS IDÊNTICOS")
end

function isapprox_val(a, b)
    a == b && return true
    try return isapprox(Float64(a), Float64(b), atol=1e-3) catch; return false end
end

# ============================================================
#   TESTES
# ============================================================

function teste_base()
    conj, sar, form, conv, opt = instancia_base()
    julia = rodar_julia(conj, sar, form, conv, opt)
    glpk  = rodar_glpk(dat_base())
    comparar("BASE", julia, glpk)
end

function teste_conflito_horario()
    conj, sar, form, conv, opt = instancia_base()
    # T1 e T2 no mesmo horário — nenhum professor pode pegar as duas
    sar2 = ParametrosSAR(
        Set([
            ("T1", 1, 3, 6), ("T1", 1, 3, 7),
            ("T2", 1, 3, 6), ("T2", 1, 3, 7),  # mesmo dia/horário que T1
            ("T3", 2, 5, 6), ("T3", 2, 5, 7),
        ]),
        Dict{String,Int64}(), Dict{String,Int64}(), Dict{String,Int64}(),
        copy(sar.vinculadas), copy(sar.turma_grupo)
    )
    julia = rodar_julia(conj, sar2, form, conv, opt)
    glpk  = rodar_glpk(dat_base() * """
param c :=
  [T1,1,3,6] 1  [T1,1,3,7] 1
  [T2,1,3,6] 1  [T2,1,3,7] 1
  [T3,2,5,6] 1  [T3,2,5,7] 1
;
""")
    comparar("CONFLITO DE HORÁRIO", julia, glpk)
end

function teste_licenca()
    conj, sar, form, conv, opt = instancia_base()
    form2 = ParametrosFormulario(
        copy(form.temporario), copy(form.chprevia1), copy(form.chprevia2),
        Set([("P1", 1)]),  # P1 em licença no semestre 1
        copy(form.pre_atribuida), copy(form.inapto), copy(form.pref_grupo),
        copy(form.pref_hor), copy(form.pref_janelas), copy(form.impedimento),
        copy(form.peso_disciplinas), copy(form.peso_numdisc), copy(form.peso_cargahor),
        copy(form.peso_horario), copy(form.peso_distintas), copy(form.peso_manha_noite),
        copy(form.peso_janelas), copy(form.chmax), copy(form.chmax1),
        copy(form.chmax2), copy(form.chmin)
    )
    julia = rodar_julia(conj, sar, form2, conv, opt)
    glpk  = rodar_glpk(dat_base() * "\nparam licenca := [P1,1] 1 ;\n")
    comparar("LICENÇA S1", julia, glpk)
end

function teste_vinculadas()
    conj, sar, form, conv, opt = instancia_base()
    # T1 semestre 1, T2 semestre 2 — vinculadas
    sar2 = ParametrosSAR(
        Set([
            ("T1", 1, 3, 6), ("T1", 1, 3, 7),
            ("T2", 2, 3, 6), ("T2", 2, 3, 7),
            ("T3", 1, 4, 8), ("T3", 1, 4, 9),
        ]),
        Dict{String,Int64}(), Dict{String,Int64}(), Dict{String,Int64}(),
        Set([("T1","T2")]),
        copy(sar.turma_grupo)
    )
    julia = rodar_julia(conj, sar2, form, conv, opt)
    glpk  = rodar_glpk(dat_base() * """
param c :=
  [T1,1,3,6] 1  [T1,1,3,7] 1
  [T2,2,3,6] 1  [T2,2,3,7] 1
  [T3,1,4,8] 1  [T3,1,4,9] 1
;
param vinculadas := [T1,T2] 1 ;
""")
    comparar("VINCULADAS", julia, glpk)
end

function teste_inapto()
    conj, sar, form, conv, opt = instancia_base()
    form2 = ParametrosFormulario(
        copy(form.temporario), copy(form.chprevia1), copy(form.chprevia2),
        copy(form.licenca), copy(form.pre_atribuida),
        Set([("P1", "G1")]),  # P1 inapto para G1
        copy(form.pref_grupo), copy(form.pref_hor), copy(form.pref_janelas),
        copy(form.impedimento),
        copy(form.peso_disciplinas), copy(form.peso_numdisc), copy(form.peso_cargahor),
        copy(form.peso_horario), copy(form.peso_distintas), copy(form.peso_manha_noite),
        copy(form.peso_janelas), copy(form.chmax), copy(form.chmax1),
        copy(form.chmax2), copy(form.chmin)
    )
    julia = rodar_julia(conj, sar, form2, conv, opt)
    glpk  = rodar_glpk(dat_base() * "\nparam inapto := [P1,G1] 1 ;\n")
    comparar("INAPTO G1", julia, glpk)
end

function teste_carga_previa()
    conj, sar, form, conv, opt = instancia_base()
    form2 = ParametrosFormulario(
        copy(form.temporario),
        Dict("P1" => 10, "P2" => 0),  # P1 quase no limite semestral
        copy(form.chprevia2),
        copy(form.licenca), copy(form.pre_atribuida), copy(form.inapto),
        copy(form.pref_grupo), copy(form.pref_hor), copy(form.pref_janelas),
        copy(form.impedimento),
        copy(form.peso_disciplinas), copy(form.peso_numdisc), copy(form.peso_cargahor),
        copy(form.peso_horario), copy(form.peso_distintas), copy(form.peso_manha_noite),
        copy(form.peso_janelas), copy(form.chmax), copy(form.chmax1),
        copy(form.chmax2), copy(form.chmin)
    )
    julia = rodar_julia(conj, sar, form2, conv, opt)
    glpk  = rodar_glpk(dat_base() * "\nparam chprevia1 := P1 10 ;\n")
    comparar("CARGA PRÉVIA", julia, glpk)
end

function teste_manha_noite()
    conj, sar, form, conv, opt = instancia_base()
    # T1 manhã (h=3,4), T2 noite (h=12,13) — mesmo semestre
    sar2 = ParametrosSAR(
        Set([
            ("T1", 1, 3, 3), ("T1", 1, 3, 4),
            ("T2", 1, 4, 12), ("T2", 1, 4, 13),
            ("T3", 2, 5, 6),  ("T3", 2, 5, 7),
        ]),
        Dict{String,Int64}(), Dict{String,Int64}(), Dict{String,Int64}(),
        copy(sar.vinculadas), copy(sar.turma_grupo)
    )
    julia = rodar_julia(conj, sar2, form, conv, opt)
    glpk  = rodar_glpk(dat_base() * """
param c :=
  [T1,1,3,3]  1  [T1,1,3,4]  1
  [T2,1,4,12] 1  [T2,1,4,13] 1
  [T3,2,5,6]  1  [T3,2,5,7]  1
;
""")
    comparar("MANHÃ E NOITE", julia, glpk)
end

# ============================================================
#   MAIN
# ============================================================

println("\nIniciando bateria de testes Julia vs GLPK...\n")

teste_base()
teste_conflito_horario()
teste_licenca()
teste_vinculadas()
teste_inapto()
teste_carga_previa()
teste_manha_noite()

println("\n" * "="^60)
println("Bateria concluída.")
println("="^60)