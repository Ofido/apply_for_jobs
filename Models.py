import random
import string
from datetime import datetime, timedelta


class Generator:
    dead = False

    def __init__(self, description, limit_access, limit_time, have_strings, have_numbers, have_special_characters,
                 total_characters=20, password=None, open_times=0, identifier=None, creation_date_time=datetime.now()):
        """Método criador que gerencia e Define a senha de acordo com os parameters utilizados.

        :param description: descrição para documentar o motivo do requerimento,
                            futuramente pode ser integrado com um sistema de chamado, se tornando um identificador.
        :param limit_access: quantidade de acessos para a visualização da senha.
        :param limit_time: quantidade de horas que a senha será valida.
        :param have_strings: 0 ⇉ não; 1 ⇉ minúsculas; 2 ⇉ maiúsculas; 3 ⇉ ambas.
        :param have_numbers: tem numero.
        :param have_special_characters: tem caractere especial.
        :param total_characters: número de caracteres da senha.
        :param password: senha gerada de acordo com os parameters.
        :param open_times: quantidade de visualizações da senha.
        :param identifier: identificador.
        :param creation_date_time: data e hora da criação
        """
        self.total_characters = total_characters
        self.have_special_characters = have_special_characters
        self.have_numbers = have_numbers
        self.have_strings = have_strings
        self.description = description
        if type(limit_time) != datetime:
            limit_time = creation_date_time + timedelta(hours=limit_time)
        self.limit_time = limit_time
        self.limit_access = limit_access
        self.open_times = open_times
        self.creation_date_time = creation_date_time
        self.identifier = identifier
        self.password = (password or self.generate_password())
        self.kill = False

    def generate_password(self):
        letras = ''
        if self.have_special_characters:
            letras += string.punctuation
        if self.have_numbers:
            letras += string.digits
        if self.have_strings != 0:
            if self.have_strings == 1:
                letras += string.ascii_lowercase
            elif self.have_strings == 2:
                letras += string.ascii_uppercase
            elif self.have_strings == 3:
                letras += string.ascii_letters

        password = ''
        if len(letras) != 0:
            for char in random.choices(letras, k=self.total_characters):
                password += char
        else:
            password = 'Erro ao gerar senha'

        return password

    def kill(self, why):
        """ Método usado para destruir a senha.
        :param why: motivo da senha estar sendo destruída.
         """
        self.dead = True
        self.description += ' ' + why
        self.password = ""

    def alive(self):
        """ Método usado para verificar se a senha ainda é valida.
         """
        return self.dead

    def __str__(self):
        return self.password
