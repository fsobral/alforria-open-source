#coding=utf8

"""14-06-03 Joao:
Definicao da matricula como id do professor a fim de evitar duplicatas
Inclusao do item vinculada na classe Turma
Inclusao do item cliente/servidor na classe turma
Utilizacao do nome completo do professor, facilitara corresponder nomes em diferentes documentos, que podem apresenta-los inconsistentemente. Uma rotina nome foi adicionada.
"""

"""
14-08-08 Francisco
Conserto da funcao nome() de professor
Volta de id() de professor para nome, enquanto a matricula esta vazia
"""

"""
14-11-07 Francisco
Adicao de novos atributos e atualizacao da funcao que imprime o prof.
id() do professor agora eh a matricula
"""

"""
14-11-12 Francisco
funcao totex() na classe Professor
"""

"""
14-11-20 Francisco
- Melhoria na funcao totex()
"""

"""
14-11-26 Francisco
- Adicionado tratamento de licencas
- Preferencia por reuniao implica em impedimento para efetivo e insatisfacao maxima para temporario
"""

"""
14-11-11 Francisco
- Colocando '\' em caracteres nao numericos na hora de escrever o LaTeX
"""

"""
16-03-04 Francisco
- Ignorando notas de horarios com impedimento da hora do LaTeX
- Melhorando a saida do LaTeX
"""

"""
17-03-08 Francisco
- Adicionado atributo 'tel' e 'pos' em Professor
- Adicionado atributo carga horaria em Turma
- Modificando metodo carga_horaria em Turma
"""

import numpy
import re

class Paths:  ##################################################################################################
    def __init__(self):
        self.GRUPOSPATH = None
        self.PREFPATH = None
        self.SARPATH = None
        self.ATRIBPATH = None
        self.FANTPATH = None
        self.DATPATH = None
        self.SOLPATH = None
        self.preenchida = False

class Grupo: ##################################################################################################
    def __init__(self):
        self.id = None
        self.canonico = False
        self.disciplinas = []
    def __str__(self):
        return str(self.id) + ' ' + str(self.canonico) + ' ' + str(self.disciplinas)



class Turma: ##################################################################################################
    def __init__(self):
        self.codigo = None
        self.turma = None
        self.codigo = None
        self.nome = None
        self.semestralidade = None # 1 ou 2
        self.horarios = [] # Lista de pares (dia,horario)
        self.grupo = None # Objeto Grupo
        self.professor = None # Objeto Professor ou Nome do Professor ????
        self.vinculada=False
        self.eh_cliente = False #Indica se a turma eh uma turma cliente ou "fantasma" e tera suas aulas juntamente com outra
        self.turmas_clientes = [] #Lista de turmas que sao clientes desta
        self.pos = False
        self.ch = 0
        self.dini = None
        self.dend = None
        self.curso = ""
        
    #----------------------------------------------------------------------------------------------------
    def id(self):
        return str(self.codigo) + '_' + str(self.turma) + '_S' + str(self.semestralidade)
    #----------------------------------------------------------------------------------------------------
    def __str__(self):
        if self.professor is None:
            return self.id() + ' Sem professor ' + ' CH: ' + str(self.ch) + ' ' + str(self.horarios)
        else:
            return self.id() + ' ' + self.professor.id() + ' CH: ' + str(self.ch) + ' ' + str(self.horarios)
    #----------------------------------------------------------------------------------------------------
    def carga_horaria(self):

        if self.ch > 0:
            return self.ch
        else:
            return len(self.horarios)
    #----------------------------------------------------------------------------------------------------
    def add_professor(self, p):
        """Add a relation with professor 'p'."""
        self.professor = p

    def remove_professor(self, p):
        """Remove the relation with professor 'p'."""
        self.professor = None

class Professor:##################################################################################################
    def __init__(self):
        self.nome_completo = None
        self.matricula = None
        self.email = None
        self.tel = None
        self.chprevia1 = 0.0
        self.chprevia2 = 0.0
        self.licenca1 = False
        self.licenca2 = False
        self.discriminacao_chprevia = None
        self.temporario = False
        self.impedimentos = numpy.zeros((17,8))
        self.peso_disciplinas = 0.0
        self.peso_disciplinas_bruto = 0.0
        self.peso_horario = 0.0
        self.peso_horario_bruto = 0.0
        self.peso_cargahor = 0.0
        self.peso_distintas = 0.0
        self.peso_janelas = 0.0
        self.peso_janelas_bruto = 0.0
        self.peso_numdisc = 0.0
        self.peso_manha_noite = 0.0
        self.inapto = []	# Lista de ids de grupos
        self.pref_grupos_bruto = {}         # Mapa id de grupo para preferencia
        self.pref_reuniao = False
        self.pref_janelas = False
        self.pref_horarios_bruto = numpy.zeros((17,8))
        self.pref_grupos = {}
        self.pref_horarios = numpy.zeros((17,8))
        self.lista_impedimentos = []
        self.chmax = None
        self.chmax1 = None
        self.chmax2 = None
        self.fantasma = False
        self.pos = False
        self.observacoes = ""

    #--------------------------------Valores lidos no arquivo de solucao---------------------
        self.turmas_a_lecionar = []
        self.carga_horaria = 0.0;
        self.insatisfacao = 0.0;
        self.insat_disciplinas = 0.0;
        self.insat_cargahor = 0.0;
        self.insat_numdisc = 0.0;
        self.insat_horario = 0.0;
        self.insat_distintas = 0.0;
        self.insat_manha_noite = 0.0;
        self.insat_janelas = 0.0;

    def can_teach(self, t):
        """ Return true if professor is able and available to teach class 't'.
        """

        return not (any(self.impedimentos[h, d] for (d, h) in t.horarios) or
                    (t.grupo and t.grupo.id in self.inapto))

    #----------------------------------------------------------------------------------------------------
    def add_course(self, t):

        self.turmas_a_lecionar.append(t)


    def remove_course(self, t):

        if t in self.turmas_a_lecionar:

            self.turmas_a_lecionar.remove(t)


    #----------------------------------------------------------------------------------------------------
    def carga_horaria_atrib(self):

        ch = 0

        for t in self.turmas_a_lecionar:

                ch += t.carga_horaria()

        return ch

    def _carga_horaria_s(self, semestre):

        ch = 0

        for t in [turma for turma in self.turmas_a_lecionar
                  if turma.semestralidade is semestre]:

            ch += t.carga_horaria()

        return ch

    def carga_horaria_s1(self):

        return self.chprevia1 + self._carga_horaria_s(1)

    def carga_horaria_s2(self):

        return self.chprevia2 + self._carga_horaria_s(2)
    
    #----------------------------------------------------------------------------------------------------
    def carga_horaria_total(self):

        return self.chprevia1 + self.chprevia2 + \
                self.carga_horaria_atrib()

    #----------------------------------------------------------------------------------------------------
    def id(self):
        # O certo sera return self.matricula, mas ainda nao funciona
        return self.nome()
    #----------------------------------------------------------------------------------------------------
    def nome(self):
        tok = self.nome_completo.split()
        n = ''
        for palavra in tok:
            if len(palavra) != 0:
                if n != '':
                    n += '_' + palavra
                else:
                    n += palavra
        return n
    #----------------------------------------------------------------------------------------------------
    def __eq__(self, p):

        return True if (self.id() == p.id()) else False

    #----------------------------------------------------------------------------------------------------
    def __hash__(self):

        return hash(self.id())

    #----------------------------------------------------------------------------------------------------
    def __str__(self):
        s = str(self.nome_completo) + ' ' + str(self.matricula) + ' ' + str(self.email) + '\n'
        s += 'Temporario: ' + str(self.temporario) + ' Pref. Janelas: ' + str(self.pref_janelas) + '\n'
        s += 'Carga horaria previa - S1: ' + str(self.chprevia1) + ' S2: ' + str(self.chprevia2) + '\n'
        s += 'Pesos db=' + str(self.peso_disciplinas_bruto) + ' d=' + str(self.peso_disciplinas) + \
            ' hb=' + str(self.peso_horario_bruto) + ' h=' + str(self.peso_horario) + \
            ' c=' + str(self.peso_cargahor) + ' dist=' + str(self.peso_distintas) + \
            ' jb=' + str(self.peso_janelas_bruto) + ' j=' + str(self.peso_janelas) + \
            ' n=' + str(self.peso_numdisc) + ' mn=' + str(self.peso_manha_noite) + '\n'
        s += 'Inapto=' + str(self.inapto) + '\n'
        s += 'Impedimentos=\n' + str(self.impedimentos[1:17,2:8]) + '\n'
        s += 'Pref. Grupos Bruto=\n' + str(self.pref_grupos_bruto) + '\n'
        s += 'Pref. Grupos=\n' + str(self.pref_grupos) + '\n'
        s += 'Pref. Horarios Bruto\n' + str(self.pref_horarios_bruto[1:17,2:8]) + '\n'
        s += 'Pref. Horarios\n' + str(self.pref_horarios[1:17,2:8])
        return s
    #----------------------------------------------------------------------------------------------------
    def ajustar(self):
        # Ajuste do impedimento caso seja um titular que queira participar da reuniao
        if self.pref_reuniao and not self.temporario:
            for h in range(1,6):
                self.impedimentos[h,3] = 1

        # Ajuste da preferencia por horarios
        maximo = 0
        for j in range(2,8):
            fim = 17
            if j == 7:
                fim = 11
            for i in range(1,fim):
                if self.pref_horarios_bruto[i,j] > maximo and \
                        not self.impedimentos[i,j]:
                    maximo = self.pref_horarios_bruto[i,j]
        minimo = 10
        for j in range(2,8):
            fim = 17
            if j == 7:
                fim = 11
            for i in range(1,fim):
                if self.pref_horarios_bruto[i,j] < minimo and \
                        not self.impedimentos[i,j]:
                    minimo = self.pref_horarios_bruto[i,j]
        if maximo == minimo:
            self.peso_horario = 0.0
        else:
            self.peso_horario = self.peso_horario_bruto
            for j in range(2,8):
                for i in range(1,17):
                    self.pref_horarios[i,j] = - 10 * (self.pref_horarios_bruto[i,j] - maximo) / (maximo - minimo)
            # Se o temporario deseja participar da reuniao, entao coloca insatisfacao maxima no horario
            if self.pref_reuniao and self.temporario:
                for h in range(1,6):
                    self.pref_horarios[h,3] = 10
        # Ajuste da preferencia por grupos
        maximo = 0
        for g in self.pref_grupos_bruto.keys():
            if self.pref_grupos_bruto[g] > maximo and \
                    g not in self.inapto:
                maximo = self.pref_grupos_bruto[g]
        minimo = 10
        for g in self.pref_grupos_bruto.keys():
            if self.pref_grupos_bruto[g] < minimo and \
                    g not in self.inapto:
                minimo = self.pref_grupos_bruto[g]
        if maximo == minimo:
            self.peso_disciplinas = 0.0
        else:
            self.peso_disciplinas = self.peso_disciplinas_bruto
            for g in self.pref_grupos_bruto.keys():
                self.pref_grupos[g] = - 10 * (self.pref_grupos_bruto[g] - maximo) / (maximo - minimo)
    #----------------------------------------------------------------------------------------------------
    def display(self):
        s = self.nome()
        if self.pos:
            s += " P"
        s += " (Ch. previa: %d (1S) %d (2S), " % (int(self.chprevia1), int(self.chprevia2))
        s += "Ch. total: %d (1S) %d (2S))\n" % (self.carga_horaria_s1(), self.carga_horaria_s2())
        for t in self.turmas_a_lecionar:
            s += " "
            s += str(t)
            s += "\n"
        return s
    #----------------------------------------------------------------------------------------------------
    def totex(self,arquivo=None):

        """
        Criam um arquivo .tex cujo nome eh a matricula, contendo os comandos tex para analisar os resultados.
        O arquivo precisa ser inserido na estrutura de um documento latex, via include, por exemplo.
        """

        if arquivo is None:
            arquivo = str(self.matricula).zfill(6) + '.tex'

        with open(arquivo, 'w') as f:
            f.write('\\section*{' + str(self.nome_completo) + '\\hfill ' + str(self.matricula).zfill(6) + '}\n')
            f.write('\\begin{itemize}\n \\item ' + re.sub("([_])","\\\\\\1",self.email) + '\n')
            if self.temporario:
                f.write('\\item Temporário \n')
            else:
                f.write('\\item Efetivo \n')

            f.write('\\item Aplicar carga horária mínima: ')
            if self.pos:
                f.write('Sim\n')
            else:
                f.write('Não\n')

            f.write('\\item Carga horária prévia: ' + str(self.chprevia1 + self.chprevia2))
            if len(self.discriminacao_chprevia.strip()) > 0:
                f.write(' (' + self.discriminacao_chprevia + ')')
            f.write('\n')                    
            f.write('\\item Carga horária anual (prévia + atribuída): ' + str(int(self.carga_horaria_total())) + '\n')

            if self.fantasma:
                    f.write('\\item Satisfação: --\n')
            else:
                    f.write('\\item Satisfação: {0:5.2f}\n'.format(10.0 - self.insatisfacao))
            f.write('\\begin{center} \\begin{tabular}{|l||r|r|r|r|r|r|r|} \\hline\n')
            f.write('& Disc. & Num. disc. & Disc. distintas & Hor. & Carga hor. & ')
            if self.pref_janelas:
                f.write('Janelas');
            else:
                f.write('Hor. compactos');
            f.write(' & Manhã e noite \\\\ \midrule\n')
            f.write('Pesos & {0:5.2f} & {1:5.2f} & {2:5.2f} & {3:5.2f} & {4:5.2f} & {5:5.2f} & {6:5.2f} \\\\\n'.\
                    format(self.peso_disciplinas, self.peso_numdisc, self.peso_distintas, self.peso_horario, \
                           self.peso_cargahor, self.peso_janelas, self.peso_manha_noite))
            if self.fantasma:
                    f.write('Satisfação & -- & -- & -- & -- & -- & -- & -- \\\\\n')
            else:
                    f.write('Satisfação & {0:5.2f} & {1:5.2f} & {2:5.2f} & {3:5.2f} & {4:5.2f} & {5:5.2f} & {6:5.2f} \\\\\n'.\
                    format(10.0 - self.insat_disciplinas, 10.0 - self.insat_numdisc, 10.0 - self.insat_distintas,\
                           10.0 - self.insat_horario, 10.0 - self.insat_cargahor, 10.0 - self.insat_janelas,\
                           10.0 - self.insat_manha_noite))
            f.write('\\hline \\end{tabular} \\end{center}\n')
            f.write('\\end{itemize}')

            ini = (176,176,176)
            dir = (-11,76,-61)

            f.write('\\begin{multicols}{2}\n \\scriptsize')
            for s in range(1,3):
                f.write('\\begin{center} \\begin{tabular}{|c|c|c|c|c|c|c|}\\toprule\n')
                f.write('\\multicolumn{7}{|c|}{' + str(s) + '$^\\circ$ semestre (' + str(self._carga_horaria_s(s)) + 'h/sem)} \\\\ \\midrule\n')
                f.write('& S & T & Q & Q & S & S \\\\ \\midrule\n')
                for i in range(1,17):
                    f.write(str(i) );
                    for j in range(2,8):
                        if self.impedimentos[i,j] or (self.licenca1 and s == 1) or \
                           (self.licenca2 and s == 2) or (j == 7 and i >= 11):
                            f.write('& \\cellcolor[gray]{1} ')
                        else:
                            m = (10.0 - self.pref_horarios[i,j]) / 10.0
                            f.write('& \\cellcolor[RGB]{')
                            for k in range(0,3):
                                f.write(str(int(ini[k] + m * dir[k])))
                                if k < 2:
                                    f.write(',')
                            f.write('}')
                        for t in self.turmas_a_lecionar:
                            if t.semestralidade == s and (j,i) in t.horarios:
                                f.write(str(t.codigo) + ' ' + str(t.turma))

                    f.write('\\\\ \\midrule \n')

                f.write('\\end{tabular} \\end{center}\n\n')

            f.write('\\end{multicols}\n')
            f.write('\\begin{multicols}{2}\n')
            f.write('\\begin{center} \\begin{tabular}{|lm{6cm}|}\n')
            f.write('\\multicolumn{2}{c}{Disciplinas a lecionar} \\\\ \\midrule \\midrule\n')
            f.write('\\multicolumn{2}{|c|}{1$^\\circ$ Semestre} \\\\ \\midrule \\midrule\n')
            for t in [i for i in self.turmas_a_lecionar if i.semestralidade == 1]:
                f.write(str(t.codigo) + ' & ' + t.nome + '\\\\ \\midrule\n')
            f.write('\\midrule\n')
            f.write('\\multicolumn{2}{|c|}{2$^\\circ$ Semestre} \\\\ \\midrule \\midrule\n')
            for t in [i for i in self.turmas_a_lecionar if i.semestralidade == 2]:
                f.write(str(t.codigo) + ' & ' + t.nome + '\\\\ \\midrule\n')
            f.write('\\end{tabular} \\end{center} \\vfill\\columnbreak\n')
            f.write('\\begin{center} \\begin{tabular}{|lr|}\n')
            f.write('\\multicolumn{2}{c}{Preferência de grupos} \\\\ \\midrule \\midrule\n')

            for (g,p) in sorted(self.pref_grupos.items(), key=lambda x: x[1]):
                if g not in self.inapto:
                    f.write(g + ' & ' + str(round(10 - p, 1)) + '\\\\ \\midrule \n')
            for g in self.inapto:
                f.write(g + '& INAPTO \\\\ \\midrule \n')

            f.write('\\end{tabular} \\end{center}\n \\end{multicols}\n')
            f.write('{\\normalsize \\textbf{OBS}: ' + self.observacoes + '}')

    #----------------------------------------------------------------------------------------------------
    def att_totex(self,arquivo=None):

        """
        Criam um arquivo .tex cujo nome eh a matricula, contendo apenas as atribuicoes.
        O arquivo precisa ser inserido na estrutura de um documento latex, via include, por exemplo.
        """

        if arquivo is None:
            arquivo = str(self.matricula).zfill(6) + '.tex'

        with open(arquivo, 'w') as f:
            f.write('\\section*{' + str(self.nome_completo) + '\\hfill ' + str(self.matricula).zfill(6) + '}\n')

            f.write('\\begin{multicols}{2}\n \\scriptsize')
            for s in range(1,3):
                f.write('\\begin{center} \\begin{tabular}{|c|c|c|c|c|c|c|}\\toprule\n')
                f.write('\\multicolumn{7}{|c|}{' + str(s) + '$^\\circ$ semestre} \\\\ \\midrule\n')
                f.write('& S & T & Q & Q & S & S \\\\ \\midrule\n')
                for i in range(1,17):
                    f.write(str(i) );
                    for j in range(2,8):

                        f.write('& ')

                        for t in self.turmas_a_lecionar:
                            if t.semestralidade == s and (j,i) in t.horarios:
                                f.write(str(t.codigo) + ' ' + str(t.turma))

                    f.write('\\\\ \\midrule \n')

                f.write('\\end{tabular} \\end{center}\n\n')

            f.write('\\end{multicols}\n')
            f.write('\\begin{multicols}{2}\n')
            f.write('\\begin{center} \\begin{tabular}{|lm{6cm}|}\n')
            f.write('\\multicolumn{2}{c}{Disciplinas a lecionar} \\\\ \\midrule \\midrule\n')
            f.write('\\multicolumn{2}{|c|}{1$^\\circ$ Semestre} \\\\ \\midrule \\midrule\n')
            for t in [i for i in self.turmas_a_lecionar if i.semestralidade == 1]:
                f.write(str(t.codigo) + ' & ' + t.nome + '\\\\ \\midrule\n')
            f.write('\\midrule\n')
            f.write('\\multicolumn{2}{|c|}{2$^\\circ$ Semestre} \\\\ \\midrule \\midrule\n')
            for t in [i for i in self.turmas_a_lecionar if i.semestralidade == 2]:
                f.write(str(t.codigo) + ' & ' + t.nome + '\\\\ \\midrule\n')
            f.write('\\end{tabular} \\end{center} \\vfill\\columnbreak\n')
            f.write('\\end{multicols}\n')

##################################################################################################
