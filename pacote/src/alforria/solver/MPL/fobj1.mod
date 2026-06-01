#############################            FUNÇÃO OBJETIVO              ################################

minimize insatisfacao_maxima: 
	max_das_insat +
	1000000 * gap_ch_graduacao + 
        10000   * gap_horario_max +
        100     * gap_ch_tt;

##########################################################################################    
    
solve;
    
end;
