class Grupo:
    def __init__(self):
        self.id = None
        self.canonico = False
        self.disciplinas = []

    def __str__(self):
        return str(self.id) + " " + str(self.canonico) + " " + str(self.disciplinas)
