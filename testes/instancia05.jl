G :: Set{String} = Set{String}(["G1", "G2"])

G_CANONICOS :: Set{String} = Set{String}(["G1", "G2"])

T :: Set{String} = Set{String}(["T1", "T2", "T3"])

T_PRE :: Set{String} = Set{String}()

P_OUT :: Set{String} = Set{String}()

P :: Set{String} = Set{String}(["P1", "P2"])

conj = ConjuntosAlforria(P, T, 2:7, 1:16, 1:2, G, 1:3, G_CANONICOS, T_PRE, P_OUT)

# --- SAR ---

C =     Set([
        ("T1", 1, 3, 6), ("T1", 1, 3, 7),   # T1: semestre 1, terça, h=6 e h=7
        ("T2", 2, 3, 6), ("T2", 2, 3, 7),   # T2: semestre 1, quarta, h=8 e h=9
        ("T3", 2, 5, 6), ("T3", 2, 5, 7),   # T3: semestre 2, quinta, h=6 e h=7
])

vinculadas = Set{Tuple{String,String}}(
    [("T1", "T2")]
)

sar = ParametrosSAR(
    C,
    Dict{String, Int64}(),      # ch  — preenchido automaticamente por preencheSAR!
    Dict{String, Int64}(),      # ch1 — idem
    Dict{String, Int64}(),      # ch2 — idem
    vinculadas,
    Dict("T1" => "G1", "T2" => "G1", "T3" => "G2")  # turma_grupo
)

licenca :: Set{Tuple{String, Int64}} = Set{Tuple{String, Int64}}([
	("A1", 1)
])

inapto :: Set{Tuple{String, String}} = Set{Tuple{String, String}}([("P1", "G1")])

form = ParametrosFormulario(
    Set(["P2"]),                    # temporario
    Dict{String, Int64}(),          # chprevia1  (zerado → preenchido por preencheFormulario!)
    Dict{String, Int64}(),          # chprevia2
    licenca,     # licenca (nenhuma)
    Set{Tuple{String,String}}(),    # pre_atribuida (nenhuma)
    inapto,
    Dict{Tuple{String,String}, Float64}(),      # pref_grupo
    Dict{Tuple{String,Int64,Int64}, Float64}(), # pref_hor
    Set{String}(),                  # pref_janelas
    Set{Tuple{String,Int64,Int64,Int64}}(),     # impedimento
    Dict("P1" => 5.0, "P2" => 5.0),  # peso_disciplinas
    Dict("P1" => 5.0, "P2" => 5.0),  # peso_numdisc
    Dict("P1" => 5.0, "P2" => 5.0),  # peso_cargahor
    Dict("P1" => 5.0, "P2" => 5.0),  # peso_horario
    Dict("P1" => 5.0, "P2" => 5.0),  # peso_distintas
    Dict("P1" => 5.0, "P2" => 5.0),  # peso_manha_noite
    Dict("P1" => 5.0, "P2" => 5.0),  # peso_janelas
    Dict{String, Int64}(),  # chmax  (preenchido por preencheFormulario!)
    Dict{String, Int64}(),  # chmax1
    Dict{String, Int64}(),  # chmax2
    Dict{String, Int64}(),  # chmin
)

conv = defineParametrosConvencionados()

opt = OptimizerOptions(
    300.0,          # cputime: 5 minutos
    0.01,           # mip_gap: 1%
    "solucao.sol",  # solfile
    0,              # threads (0 = todos)
    :fobj1          # função objetivo
)

# --- RODAR ---

mod, var, varInsat = alforria(conj, sar, form, conv, opt)

# optimize!(mod)

# println("\n=== RESULTADO ===")
# println("Status         : ", termination_status(mod))
# println("Valor obj.     : ", objective_value(mod))
# println("max_das_insat  : ", value(var.max_das_insat))
# println("gap_ch_tt      : ", value(var.gap_ch_tt))
# println("gap_horario_max: ", value(var.gap_horario_max))
# println("gap_ch_grad    : ", value(var.gap_ch_graduacao))

# println("\n=== ALOCAÇÃO (x[p,t]) ===")
# for p in conj.P, t in conj.T
#     v = value(var.x[p, t])
#     if v > 0.5
#         println("  $p => $t")
#     end
# end