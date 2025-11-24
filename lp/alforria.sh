#/bin/bash

# Numero de threads. Deixe vazio para usar todas
NUM_THREADS=6

# Criterio de parada. Termina quando o GAP ficar abaixo desse valor
MIPGAP=0.6

# Inicializa o arquivo de excluidos
echo "set P_OUT := ;" > alforria2.dat

# For HiGHS
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/:/opt/gurobi/gurobi1101/linux64/lib
export PATH=$PATH:/opt/gurobi/gurobi1101/linux64/bin

python3 ../bin/antes.py

if [ $# -gt 0 ]; then
    if [ $1 -gt "1" ]; then

    echo "Entrou"

    # Numero de iteracoes do processo
    NUM_ITERACOES=$1

    # Prepara para a primeira fase de otimizacao
    echo -e "/* Este arquivo foi gerado automaticamente por alforria.sh nao adianta edita-lo. */" > alforria.mod
    cat alforria_restr.mod fobj1.mod > alforria.mod
    #cat alforria_restr.mod fobj2.mod >> alforria.mod

    for i in `seq 1 ${NUM_ITERACOES}`; do

	time nice -n 19 glpsol -m alforria.mod -d alforria.dat -d alforria2.dat --check --wlp alforria.lp;
	time nice -n 19 gurobi_cl Threads=${NUM_THREADS} MIPGap=${MIPGAP} ResultFile=alforria.sol alforria.lp;
	# time nice -n 19 highs --parallel on --presolve on --solution_file alforria.sol --model_file alforria.lp;

	python3 ../bin/depois.py;

    done;

fi;

fi

# Prepara para a segunda fase de otimizacao
echo -e "/* Este arquivo foi gerado automaticamente por alforria.sh nao adianta edita-lo. */" > alforria.mod
cat alforria_restr.mod fobj2.mod >> alforria.mod

time nice -n 19 glpsol -m alforria.mod -d alforria.dat -d alforria2.dat --check --wlp alforria.lp;
time nice -n 19 gurobi_cl Threads=${NUM_THREADS} MIPGap=${MIPGAP} ResultFile=alforria.sol alforria.lp;
# time nice -n 19 highs --parallel on --presolve on --solution_file alforria.sol --model_file alforria.lp --mip_heuristic_effort 1;

python3 ../bin/depois.py;
