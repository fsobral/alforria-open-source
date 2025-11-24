/*Classes de parâmetros
VARIÁVEIS - Preenchido pelo ''shell'' ou executor do programa
CONVENCIONADOS - Definidos todos neste arquivo
ORIGENS DIVERSAS - Vem da documentação do DMA
    -Cadastro de professores
    -Licencas
    -Disciplinas pré-atribuidas
    -''SAR da Pós''
SAR - Lidos no arquivo SAR
DE FORMULÁRIO - São colhidos dos formulários depreferências preenchidos pelos professores
COMPOSTOS -  Dependem de cálculos envolvendo parâmetros diversos e de supervisão humana
DEPENDENTES COM EXCESSÕES - Têm seu valor padrão, mas devem ser revistos e ajustados manualmente
DEPENDENTES SEM EXCESSÕES - Ficam em função de outros parâmetros e não devem ser alterados diretamente por intervenção humana
*/


########################	CONJUNTOS	###################

set P; 	/*professores*/
set T;	/*turmas*/
set D := 2..7;	/*dias*/
set H := 1..16;	/*horários (conforme numeração do horário individual)*/
set S := 1..2;	/*semestre*/
set G;		/*grupos de disciplinas*/
set TURNOS := 1..3; /*resp., manhã, tarde e noite*/
set G_CANONICOS;
set T_PRE;
set P_OUT; /* professores ja otimizados */

#########################	PARÂMETROS      VARIÁVEIS	##########################
 
param insatisfacao_almejada, default 2;

/*A porcentagem de nossa capacidade de trabalho que usaremos aso necessário(em termos da capacidade anual)*/
#param aproveitamento_minimo, default 0.5;


###########################	PARÂMETROS      CONVENCIONADOS	     ##########################

param chmax_efetivo_anual, default 20;
param chmax_efetivo_semestral, default 12;
param chmax_temporario_anual, default 40;
param chmax_temporario_semestral, default 22;
param chmax_diaria, default 8;
param chmin_efetivo_anual, default 16;
param chmin_temporario_anual, default 24;

param chmin_graduacao, default 8;
param numdiscmax_temporario, default 10;

/* 0: efetivo, 1: temporario */
param paraiso_cargahor{k in 0..1}, default 9*k +8 ;  /* 8 , 16 */ #? 8*k inves de 9*k??
param inferno_cargahor{k in 0..1}, default 10 + 11*k; /* 12, 20 */ 

param paraiso_numdisc{k in 0..1} , default 2+k;  /* 2 , 3 */
param inferno_numdisc{k in 0..1} , default 4+k;  /* 4 , 5 */

param paraiso_distintas{k in 0..1}, default 1+k; /* 1 , 2 */
param inferno_distintas{k in 0..1}, default 3+k; /* 3,4 */

param paraiso_trn_cheios{k in 0..1}, default 0+k; /* 0 , 1 */
param inferno_trn_cheios{k in 0..1}, default 2+3*k; /* 2 , 5 */

param paraiso_turnos{k in 0..1}, default 2+ 3*k ; /* 2 , 5 */
param inferno_turnos{k in 0..1}, default 4+ 6*k;  /*4 , 10 */


##########################	PARÂMETROS DE ORIGENS DIVERSAS		#######################

param numero_de_grupos, default 13;

param pre_atribuida{P,T}, default 0;

##########################	PARÂMETROS          SAR 	##############################-

/* Indica se a turma t tem aula no semestre s, dia d, horario h */
param c{T,S,D,H}, default 0;
/* Carga horaria total de uma turma (horas/semana)*/
param ch{t in T}, default sum{s in S, d in D, h in H} c[t,s,d,h];
/* Carga horaria no primeiro semestre (horas/semana)*/
param ch1{t in T}, default sum{d in D, h in H} c[t,1,d,h];
/* Carga horaria no segundo semestre (horas/semana)*/
param ch2{t in T}, default sum{d in D, h in H} c[t,2,d,h];
/* Vincula a disciplina no primeiro semestre a ela mesma no segundo */
param vinculadas{T,T}, default 0;


/* Indica se a turma t esta no grupo G (não é coletado do sar mas informado pelo programa que faz a coleta) */
param turma_grupo{T,G}, default 0;

##########################	PARÂMETROS   DE    FORMULÁRIO	   ##########################-
param temporario{P}, default 0;
param chprevia1{P}, default 0;
param chprevia2{P}, default 0;
#######param reducaoch{P}, default 0;
param chprevia_tt{p in P}:= chprevia1[p]+ chprevia2[p];/*+reducaoch[p];*/
param licenca{P,S}, default 0;
param prop{p in P}, default 0.5*(2-licenca[p,1]-licenca[p,2]);

param peso_disciplinas{P}, default 0;
param peso_numdisc{P}, default 0;
param peso_cargahor{P}, default 0;
param peso_horario{P}, default 0;
param peso_distintas{P}, default 0;
param peso_manha_noite{P}, default 0;
param peso_janelas{P}, default 0;

/* O professor P é inapto a  lecionar para o grupo G*/
param inapto{p in P,g in G}, default 
    if g in G_CANONICOS then 0
    else(
	if (sum{t in T: turma_grupo[t,g]==1} pre_atribuida[p,t]) >=1 then 0
	else 0);
/* Parametro de preferencia de um professor por lecionar em um grupo */
param pref_grupo{P,G}, default 0;
/* Parametro de preferencia de um professor por lecionar em um horario*/
param pref_hor{P,D,H}, default 5;
/* Prefere janelas 1, prefere não ter janelas 0*/
param pref_janelas{P}, default 0;
/* O professor nao pode lecionar no horario dado por S, D e H */
param impedimento{P,S,D,H}, default 0;

############################	PARÂMETROS DEPENDENTES - COM EXCEÇÕES 	    ########################-

/* Carga horaria maxima anual de um professor (horas/semana)*/
param chmax{p in P}, default
    if (temporario[p]) then 
       if (licenca[p,1] + licenca[p,2] = 0)  then (chmax_temporario_anual)
       else (chmax_temporario_semestral)
    else
	if (licenca[p,1] + licenca[p,2] = 0)  then (chmax_efetivo_anual) 
	else (chmax_efetivo_semestral);

/* Carga horaria maxima no primeiro semestre (horas/semana)*/
param chmax1{p in P}, default
    if licenca[p,1] == 1 then 0
    else
       if temporario[p] == 1 then
       	  chmax_temporario_semestral
       else
          chmax_efetivo_semestral;
          
/* Carga horaria maxima no segundo semestre (horas/semana)*/
param chmax2{p in P}, default
    if licenca[p,2] == 1 then 0
    else
       if temporario[p] == 1 then
       	  chmax_temporario_semestral
       else
          chmax_efetivo_semestral;

/* Carga horaria minima anual (horas/semana)*/
param chmin{p in P}, default 
  if temporario[p]==1 then
      (if (licenca[p,1] + licenca[p,2] = 0) then (chmin_temporario_anual)
      else chmin_temporario_anual/2)
  else
      (if (licenca[p,1] + licenca[p,2] = 0) then (chmin_efetivo_anual) 
      else (chmin_efetivo_anual/2));

###########################	PARÂMETROS DEPENDENTES - SEM EXCEÇÕES    	########################-

/* Parametro de preferencia de um professor por uma turma (depende dos parametros pre_atribuida, pref_grupo, e turma-grupo) */
param pref_turma{p in P,t in T},       default 
      if pre_atribuida[p,t]==1 or (sum{g in G: turma_grupo[t,g]=1} inapto[p,g])>0
	      then 0 
      else
	( sum{g in G} turma_grupo[t,g]*pref_grupo[p,g] );

/* Indica se o horário h pertence ao turno u */
param horario_turno{h in H, u in TURNOS}, default
      if h<=5 and u==1 then 1 else
      if h>=6 and h<=10 and u=2 then 1 else
      if h>= 11 and u=3 then 1 else
      0;
 
param customarginal_cargahor{k in 0..1}, default 5/(inferno_cargahor[k] - paraiso_cargahor[k]);
param customarginal_numdisc{k in 0..1}, default 5/(inferno_numdisc[k] - paraiso_numdisc[k]);
param customarginal_distintas{k in 0..1}, default 5/(inferno_distintas[k] - paraiso_distintas[k]);
param customarginal_trn_cheios{k in 0..1}, default 5/(inferno_trn_cheios[k] - paraiso_trn_cheios[k]);
param customarginal_turnos{k in 0..1}, default 5/(inferno_turnos[k] - paraiso_turnos[k]);

/*parametro de decisão: se t tem aula no semestre s*/
param semestralidade{t in T, s in S}, default
    if (sum{d in D, h in H}c[t,s,d,h])>=1 then 1
    else 0;

/*Ajustes de preferências por horários*/
param ajuste_hor{p in P}, default if (sum{d in D, h in H}pref_hor[p,d,h])==0 then 0 else 400/(sum{d in D, h in H}pref_hor[p,d,h]);  #400=5 * ( 6*14 - 4 )




#########################	PARÂMETROS      DE        CARGA        HORARIA       ##########################

/* Carga horaria maxima que o departamento consegue atender*/
param capacidade_departamento_sup, default sum{p in P}chmax[p];
#param capacidade_departamento_inf, default aproveitamento_minimo*(sum{p in P}chmax[p]);
/* Carga horária média (esperada) */
param chesp_efetivo_anual, default 18;
param chesp_temporario_anual, default 36;

/* Carga hor´aria esperada */
param chesp{p in P}, default
       if temporario[p] == 1 then
       	  chesp_temporario_anual
       else
          (if (licenca[p,1] + licenca[p,2] == 0) then chesp_efetivo_anual else chesp_efetivo_anual/2);

/*Carga horária esperada total*/
param chesp_tt, default sum{p in P}chesp[p];
param chprevia_total, default sum{p in P}(chprevia_tt[p]);

/*arga horária tolerada*/
param ch_tolerada, default chesp_tt;

/*Carga horária de todas as disciplinas somadas*/
param demanda_de_ch, default sum{t in T}ch[t]+chprevia_total;

#############################	COEFICIENTES DA FUNÇÃO INSTISFAÇÃO	##########################

param peso_total_inv{p in P}, default 
    1/(peso_disciplinas[p]+peso_numdisc[p]+peso_cargahor[p]+peso_horario[p]
    +peso_distintas[p]+peso_manha_noite[p]+peso_janelas[p]);

/*
param co_x{p in  P, t in T}, default 
	    peso_total_inv[p]*prop[p]*(
	    peso_disciplinas[p] * (1/chesp[p]) * pref_turma[p,t] * ch[t]
	  + peso_cargahor[p]  * ch[t] *  customarginal_cargahor[temporario[p]]
	  + peso_numdisc[p] * customarginal_numdisc[temporario[p]]
	  + peso_horario[p] * ( sum{s in S, d in D, h in H} c[t,s,d,h]*pref_hor[p,d,h] )	);
	  
	  
param co_lec_grp{p in P,g in G,s in S}, default
	  peso_total_inv[p]*peso_distintas[p] * prop[p] * customarginal_distintas[temporario[p]];

param co_manha_noite{p in P}, default peso_total_inv[p]* 2.5 * peso_manha_noite[p];

param co_trn_cheio{p in  P,S,D,TURNOS} , default
    if (pref_janelas[p] = 1) then
	peso_total_inv[p]* peso_janelas[p] * prop[p] * customarginal_trn_cheios[temporario[p]]
    else 0;
	
param co_lec_trn{p in  P,S,D,TURNOS}, default
    if (pref_janelas[p] = 0) then
	peso_total_inv[p]* peso_janelas[p] * prop[p] * customarginal_turnos[temporario[p]]
    else 0;*/

#############################        DECLARAÇÃO DE VARIÁVEIS       ##########################

var max_das_insat;		/*Maximo das insatisfações*/
var insat{P};			/*Insatisfação de cada professor*/
var ch_atendida;		/*Carga horária atendida*/
var gap_ch_tt;		/*Mínimo da ch pretendida e ch atendida*/
var gap_horario_max;		/*Máximo dos gaps entre a carga horária do professor e seu limite mínimo legal*/
var gap_ch_graduacao; /* Maximo dos gaps entre a carga horaria minima da graduacao e a realizada */

var x{P,T}, binary;		/* x[p,t] p leciona para t */

var lec_grp{P,G,S}, binary; 		/* Indica se p leciona disciplina do grupo G em s */
var lec_trn{P,S,D,TURNOS}, binary; 	/* Indica se p leciona so memestre s, dia d, turno u */
var trn_cheio{P,S,D,TURNOS}, binary;	/*O respectivo truno é cheio*/ #! precisa de P?

var noite{P,S}, binary;			/* p leciona a noite em s */
var manha{P,S}, binary;			/* p leciona de manha em s */
var noitext{P,S}, binary;		/* p leciona no extremo da noite em s */
var manhaxt{P,S}, binary;		/* p leciona no extremo da manha em s */
var mnh_nt{P,S}, binary;		/* p leciona na manha e noite em s*/
var mnh_ntxt{P,S}, binary;		/* p leciona na manha e extremo da noite noite em s*/
var nt_mnhxt{P,S}, binary;		/* p leciona na noite e extremo da manha em s*/


#############################           RESTRIÇÕES NÃO ESSENCIAIS          ######################


/*Nos dois horarios imediatamente antes e apos uma refeicao, no maximo em apenas um deles um professor leciona*/
#s.t. rest10_1{p in P, s in S, d in D}:
#      sum{t in T diff T_PRE}( x[p,t]*c[t,s,d,5] + x[p,t]*c[t,s,d,6] )<= 1;
#s.t. rest10_2{p in P, s in S, d in D}:
#      sum{t in T diff T_PRE}( x[p,t]*c[t,s,d,10] + x[p,t]*c[t,s,d,11] )<= 1;

#########################	DEFINIÇÃO DE VARIÁVEIS DE DEMANDA      ##########################

param previa_liquida{p in P} := chprevia1[p]+chprevia2[p]+sum{t in T}pre_atribuida[p,t]*ch[t];
param capacidade_pessoal{p in P}, default
	if temporario[p]==0 then
		max(previa_liquida[p],chesp_efetivo_anual)
	else
		max(previa_liquida[p],chesp_temporario_anual);
param capacidade_total := (sum{p in P} capacidade_pessoal[p]) - chprevia_total;
param demanda := sum{t in T}ch[t];
# def_gap_ch_tt1: gap_ch_tt>= min(demanda,capacidade_total) - sum{t in T, p in P}ch[t]*x[p,t]; #blablabla - oferta
def_gap_ch_tt1: gap_ch_tt>= demanda - sum{t in T, p in P}ch[t]*x[p,t]; #blablabla - oferta
def_gap_ch_tt2: gap_ch_tt>=0;
def_gap_horario_max1{p in P}: gap_horario_max >= chmin[p]-(chprevia_tt[p]+sum{t in T}ch[t]*x[p,t]);
def_gap_horario_max2: gap_horario_max>=0;

def_gap_ch_grad1{p in P: licenca[p,1] + licenca[p,2] == 0}: gap_ch_graduacao >= chmin_graduacao - sum{t in T} ch[t] * x[p,t];
def_gap_ch_grad2{p in P: licenca[p,1] + licenca[p,2] == 1}: gap_ch_graduacao >= (chmin_graduacao / 2) - sum{t in T} ch[t] * x[p,t];
def_gap_ch_grad3{p in P: (temporario[p] == 1) and (licenca[p,1] + licenca[p,2] == 0)}: gap_ch_graduacao >= 18 - sum{t in T} ch[t] * x[p,t];
def_gap_ch_grad4{p in P: (temporario[p] == 1) and (licenca[p,1] + licenca[p,2] == 1)}: gap_ch_graduacao >= (18 / 2) - sum{t in T} ch[t] * x[p,t];

def_gap_ch_grad5: gap_ch_graduacao >= 0;



var demanda_var;
var capacidade_total_var;
var oferta_var;
s.t. demanda_def: demanda_var=demanda;
s.t. capacidade_total_def: capacidade_total_var=capacidade_total;
s.t. oferta_def: oferta_var=sum{t in T, p in P}ch[t]*x[p,t];

############################       DEFINIÇÃO DE VARIÁVEIS AUXILIARES        ###########################

# Definicao da variavel auxiliar lec_grp{P,G,S} (Indica se p leciona disciplina do grupo G em s) 
s.t. def_lec_grp_inapto{p in P, g in G, s in S: inapto[p,g]=1}:
    lec_grp[p,g,s]=0;
s.t. def_lec_grp_up{p in P, g in G, s in S: inapto[p,g]=0}: 
    lec_grp[p,g,s] <= ( sum{t in T: semestralidade[t,s]=1}(turma_grupo[t,g]*x[p,t]) );
s.t. def_lec_grp_down {p in P, g in G, t in T, s in S: inapto[p,g]=0 and semestralidade[t,s]=1 and turma_grupo[t,g]}:     
    lec_grp[p,g,s] >= x[p,t];
    
# Definicao da variavel auxiliar lec_trn (Indica se p leciona so memestre s, dia d, turno u) 
s.t. def_lec_trn_up {p in P, s in S, d in D, u in TURNOS}: 
    lec_trn[p,s,d,u] <= ( sum{t in T, h in H: horario_turno[h,u]=1 and c[t,s,d,h]=1}x[p,t] );   
s.t. def_lec_trn_down {p in P, s in S, t in T, d in D, h in H, u in TURNOS: horario_turno[h,u]=1 and c[t,s,d,h]==1}: 
    lec_trn[p,s,d,u] >= x[p,t];

# Definicao da variavel auxiliar trn_cheio (Indica se p leciona so memestre s, dia d, turno u) 
s.t. def_trn_cheio_up {p in P, s in S, d in D, u in TURNOS}: 
    4*trn_cheio[p,s,d,u] <= ( sum{t in T, h in H: horario_turno[h,u]=1 and c[t,s,d,h]=1}x[p,t] );   
s.t. def_trn_cheio_down {p in P, s in S, d in D, u in TURNOS}: 
    trn_cheio[p,s,d,u] >= -3 + 0.5*( sum{t in T, h in H: horario_turno[h,u]=1 and c[t,s,d,h]=1}x[p,t] ); 
        
# Manha[p,s] : p leciona pela manha em s 
s.t. def_manha_up {p in P, s in S}:
    manha[p,s] <= sum{d in D} lec_trn[p,s,d,1];
s.t. def_manha_low {p in P, s in S, d in D}:
    manha[p,s] >= lec_trn[p,s,d,1];

# Noite[p,s] : p leciona pela manha em s
s.t. def_noite_up{p in P, s in S}:
    noite[p,s] <= sum{d in D} lec_trn[p,s,d,3];
s.t. def_noite_low {p in P, d in D, s in S}:
    noite[p,s] >= lec_trn[p,s,d,3];   

# noitext[p,s]: p leciona no extremo da noite em s 
s.t. def_noitext_up {p in P, s in S}:
    noitext[p,s] <= sum{t in T, d in D}(c[t,s,d,13]*x[p,t]+c[t,s,d,14]*x[p,t]);
s.t. def_noitext_down {p in P, s in S}:
    12 * noitext[p,s] >= sum{t in T, d in D}(c[t,s,d,13]*x[p,t]+c[t,s,d,14]*x[p,t]);
    
# manhaxt[p,s]: p leciona no extremo da manha em s 
s.t. def_manhaxt_up {p in P, s in S}:
    manhaxt[p,s] <= sum{t in T, d in D}(c[t,s,d,1]*x[p,t]+c[t,s,d,2]*x[p,t]);    
s.t. def_manhaxt_down {p in P, s in S}:
    12 * manhaxt[p,s] >= sum{t in T, d in D}(c[t,s,d,1]*x[p,t]+c[t,s,d,2]*x[p,t]); 

# mnh_nt[p,s] pe leciona de manha E de noite em s 
s.t. def_mnh_nt_1 {p in P, s in S}:     mnh_nt[p,s] <= manha[p,s];
s.t. def_mnh_nt_2 {p in P, s in S}:     mnh_nt[p,s] <= noite[p,s];
s.t. def_mnh_nt_3 {p in P, s in S}:     mnh_nt[p,s] >= manha[p,s] + noite[p,s] - 1;

# mnh_ntxt[x,p]: p leciona na manha e extremo da noite noite em s
s.t. def_mnh_ntxt_1 {p in P, s in S}:     mnh_ntxt[p,s] <= mnh_nt[p,s];
s.t. def_mnh_ntxt_2 {p in P, s in S}:     mnh_ntxt[p,s] <= noitext[p,s];
s.t. def_mnh_ntxt_3 {p in P, s in S}:     mnh_ntxt[p,s] >= mnh_nt[p,s] + noitext[p,s] - 1;

# nt_mnhxt[x,p]: p leciona na noite e extremo da manha em s
s.t. def_nt_mnhxt_1 {p in P, s in S}:     nt_mnhxt[p,s] <= mnh_nt[p,s];
s.t. def_nt_mnhxt_2 {p in P, s in S}:     nt_mnhxt[p,s] <= manhaxt[p,s];
s.t. def_nt_mnhxt_3 {p in P, s in S}:     nt_mnhxt[p,s] >= mnh_nt[p,s] + manhaxt[p,s] - 1;


#########################      RESTRIÇÕES  ESSENCIAIS       ############################-


# Um professor nao leciona em duas turmas ao mesmo tempo #
s.t. rest1{p in P, s in S, d in D, h in H}:
     sum{t in T} c[t,s,d,h] * x[p,t] <= 1;

# Professores inaptos nao ministram as respectivas disciplinas #
s.t. rest2{p in P, t in T, g in G : inapto[p,g]==1 and turma_grupo[t,g]==1}:
     x[p,t] = 0;

# Cada turma tem, no maximo, um professor #
s.t. rest3{t in T}:
     sum{p in P} x[p,t] <= 1; #-----------------------------------------------------------------------------------------FORÇANDO TODOS

# Limita superiormente a carga horaria anual e semestral de um professor 
s.t. rest4_1{p in P}:
     chprevia_tt[p] + sum{t in T} ch[t]*x[p,t]<= max(0,chmax[p]);

s.t. rest4_2{p in P}:
     chprevia1[p] + sum{t in T} ch1[t]*x[p,t] <= max(0,chmax1[p]);
     
s.t. rest4_3{p in P}:
     chprevia2[p] + sum{t in T} ch2[t]*x[p,t] <= max(0,chmax2[p]);
     
# Limita inferiormente a carga horaria anual de um professor 
#s.t. rest5{p in P}: chprevia_tt[p] + sum{t in T} ch[t]*x[p,t]>= chmin[p];
#s.t. rest5{p in P}: sum{t in T} ch[t]*x[p,t]>= chmin_graduacao;
#s.t. rest5_1{p in P: temporario[p] == 1}: chprevia1[p] + sum{t in T} ch1[t]*x[p,t]>= 16;
#s.t. rest5_2{p in P: temporario[p] == 1}: chprevia2[p] + sum{t in T} ch2[t]*x[p,t]>= 16;

# Professor nao pode dar aulas em horarios conflitantes com outras atividades
s.t. rest6{p in P, t in T, s in S, d in D, h in H : impedimento[p,s,d,h] == 1 and c[t,s,d,h] == 1}: x[p,t] = pre_atribuida[p,t];

# Deve haver um intervalo maior ou igual que 11h entre jornadas de trabalho em dias consecutivos
s.t. rest7{p in P, d in 2..6, s in S, h1 in 14..16, h2 in 1..3 : h1 - h2 >= 14}:
     (sum{t in T} c[t,s,d,h1] * x[p,t]) + (sum{t in T} c[t,s,d + 1,h2] * x[p,t]) <= 1;

# Respeita as disciplinas pre-atribuidas
s.t. rest8{p in P, t in T : pre_atribuida[p,t] == 1}:     x[p,t] = 1;

# Maximo de horas de aula diarias
s.t. rest9{p in P, s in S, d in D}: sum{t in T, h in H} x[p,t] * c[t,s,d,h] <= chmax_diaria;
     
# Vincula as duas metades de uma disciplina anual
#s.t. rest10{p in P, t1 in T, t2 in T: vinculadas[t1,t2]==1}: x[p,t1]=x[p,t2];

# Maximo de numero de disciplinas para temporarios
s.t. rest11{p in P: temporario[p] == 1}: sum{t in T} x[p,t] <= numdiscmax_temporario;

# Maximo de numero de grupos para temporarios
s.t. rest12{p in P, s in S: temporario[p] == 1}: sum{g in G} lec_grp[p,g,s] <= 2;

#################################       RESTRIÇÕES   VARIÁVEIS        ##################################


#s.t. capacidade_inf:
#  sum{p in P, t in T} x[p,t]*ch[t] >= min(capacidade_departamento_inf,demanda_de_ch);
#s.t. capacidade_sup: sum{p in P, t in T} x[p,t]*ch[t] <= capacidade_departamento_sup;

#########################################################################################################

################       RESTRICAO DE INSATISFACAO MAXIMA PARA ALGUNS PROFESSORES       ###################

param ub_insat{P}, default 100;

s.t. limitante_insatisfacao{p in P}:
     insat[p] <= ub_insat[p];

#########################################################################################################



var carga_horaria{P};
def_carga_horaria{p in P}: carga_horaria[p]=sum{t in T}ch[t]*x[p,t] + chprevia_tt[p];
var numero_de_disciplinas{P};
def_numero_de_disciplinas{p in P}: numero_de_disciplinas[p]=sum{t in T}x[p,t];


var insat_disciplinas{P};
def_insat_disciplinas{p in P}: insat_disciplinas[p]=(1/chesp[p]) * (sum{t in T}pref_turma[p,t]*ch[t]*x[p,t]);

var insat_cargahor{P};
def_insat_cargahor{p in P}:insat_cargahor[p]=customarginal_cargahor[temporario[p]]*((sum{t in T}ch[t]*x[p,t] + chprevia_tt[p])-2*paraiso_cargahor[temporario[p]]);

var insat_numdisc{P};
def_insat_numdisc{p in P}:insat_numdisc[p] = 
	customarginal_numdisc[temporario[p]]*((sum{t in T}x[p,t])+(chprevia_tt[p]/6)-2*paraiso_numdisc[temporario[p]]);

var insat_horario{P};
def_insat_horario{p in P}:insat_horario[p] = 
	ajuste_hor[p]*(1/chesp[p])*(sum{t in T,s in S,d in D,h in H} c[t,s,d,h]*pref_hor[p,d,h]*x[p,t]);

var insat_distintas{P};
def_insat_distintas{p in P}:insat_distintas[p] = 
	customarginal_distintas[temporario[p]]*((sum{g in G, s in S}lec_grp[p,g,s]+(chprevia_tt[p]/6))-2*paraiso_distintas[temporario[p]]);
var insat_manha_noite{P};
def_insat_manha_noite{p in P}:insat_manha_noite[p]=5*(mnh_nt[p,1]+mnh_nt[p,2]);
var insat_janelas{P};
def_insat_janelas{p in P}:insat_janelas[p]=pref_janelas[p]*customarginal_trn_cheios[temporario[p]]*
    ((sum{s in S, d in D, u in TURNOS}trn_cheio[p,s,d,u])-2*paraiso_trn_cheios[temporario[p]])
    +(1-pref_janelas[p])*customarginal_turnos[temporario[p]]*
    ((sum{s in S, d in D, u in TURNOS}lec_trn[p,s,d,u])-2*paraiso_turnos[temporario[p]]);

#############################    MAZELAS DAS PREATRIBUIDAS     ###############################

#var mazela;
#s.t. def_mazela: mazela=sum{p in P, t in T}pre_atribuida[p,t]*(1-x[p,t]);


###############################         INSATISFACAO DEFINICAO         ####################


#Escala aproximada de zero a 10

s.t. insat_def{p in P}: insat[p] = (1-0.2*temporario[p])*peso_total_inv[p]*(1/prop[p])*(
peso_disciplinas[p]*insat_disciplinas[p]+
peso_cargahor[p]*insat_cargahor[p]+
peso_numdisc[p]*insat_numdisc[p]+
peso_horario[p]*insat_horario[p]+
peso_distintas[p]*insat_distintas[p]+
peso_manha_noite[p]*insat_manha_noite[p]+
peso_janelas[p]*insat_janelas[p]
);

#s.t. insat_def{p in P}: insat[p] = insat_disciplinas[p];

s.t. max_das_insat_def{p in P diff P_OUT}: max_das_insat>=insat[p];

############################## COLOCAR A FUNCAO OBJETIVO DESEJADA AQUI #########################
