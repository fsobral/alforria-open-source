#coding=utf8

import unidecode
import re
import classes
#############################################################################################################
##############################           funcao        get_paths         ####################################
#############################################################################################################

def get_paths():
	p=classes.Paths()
	with open("../paths.cnf","r") as f:
		for linha in f:
			tok=linha.split()
			if "GRUPOSPATH" == tok[0]:
				p.GRUPOSPATH=tok[1]
			if "PREFPATH" == tok[0]:
				p.PREFPATH=tok[1]
			if "SARPATH" == tok[0]:
				p.SARPATH=tok[1]
			if "ATRIBPATH" == tok[0]:
				p.ATRIBPATH=tok[1]
			if "FANPATH" == tok[0]:
				p.FANTPATH=tok[1]
			if "DATPATH" == tok[0]:
				p.DATPATH=tok[1]
			if "SOLPATH" == tok[0]:
				p.SOLPATH=tok[1]
	if (p.GRUPOSPATH != None) and (p.PREFPATH != None) and (p.SARPATH != None) and (p.ATRIBPATH != None) and (p.FANTPATH != None) and (p.DATPATH != None) and (p.SOLPATH != None):
		p.preenchida=True
	return p


#############################################################################################################
##############################           funcao        compara_nomes     ####################################
#############################################################################################################
def compara_nomes(nome1,nome2): #Diz se os nomes se referem a mesma pessoa, uniformizacao e necessaria eh retornada resposta positiva se as pessoas possuem dois nomes em comum
	tok1=nome1.split()
	tok2=nome2.split()
	ocorrencia=False
	for i in range(0,len(tok1)):
		for j in range(0,len(tok2)):
			if len(tok1[i])>0 and tok1[i]==tok2[j]:
				ococrrencia=True
				break
	if not ococrrencia:
		return False
	for k in range(i+1,len(tok1)):
		for l in range(0,len(tok2)):
			if len(tok1[i])>0 and tok1[k]==tok2[l]:
				return True
	return False

##
# Funcao que uniformiza strings: retira acentos e deixa todas as letras maiusculas.
##
def uniformize(s,encode='utf8'):
    return re.sub("[.']","",unidecode.unidecode(s).upper().strip())
