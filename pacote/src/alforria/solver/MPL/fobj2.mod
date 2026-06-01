#############################            FUNÇÃO OBJETIVO              ################################

minimize insatisfacao_maxima: 
        (1/card(P)) * (sum{p in P diff P_OUT} insat[p]) +
	1000000 * gap_ch_graduacao + 
        10000   * gap_horario_max +
        100     * gap_ch_tt;

##########################################################################################    
    
solve;
    
end;
