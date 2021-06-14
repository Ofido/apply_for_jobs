import atexit
from datetime import datetime

from itsdangerous.url_safe import URLSafeSerializer
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request
from Models import Generator

app = Flask(__name__)
s = URLSafeSerializer("daniel_ofido_bulhoes_totvs")  # Usando um serializador de URL para aumentar a segurança.
app.logger.setLevel("INFO")  # Definido para info possibilitando o logging via console.
# Senha para testes de acesso
gen0 = Generator('Senha Inicial para teste', 1, 1, 3, 1, 1, 20, identifier=0)
passwords = [gen0, ]


@app.route("/generate")
def settings_pass():
    # Correto seria ter uma integração com o serviço de autenticação para verificar se o usuário esta logado no sistema
    # da forma correta e possa fazer o uso da ferramenta de geração, ou certificar que ela esta alocada em uma
    # rede interna.
    for palavras in request.access_route:
        app.logger.log(20, "%s está tentando gerar uma senha.", palavras)

    return render_template('gera_senha.html')


@app.route("/generated", methods=['POST'])
def copping_pass():
    aux = len(passwords)
    passwords.append(Generator(description=request.form["description"],
                               limit_time=int(request.form["limit_time"]),
                               limit_access=int(request.form["limit_access"]),
                               total_characters=int(request.form["total_characters"]),
                               have_strings=int(request.form["have_strings"]),
                               have_numbers=(request.form["have_numbers"] == "True"),
                               have_special_characters=(request.form["have_special_characters"] == "True"),
                               identifier=aux))

    for rota in request.access_route:
        app.logger.log(20, "%s gerou a senha %s.", rota, aux)

    return render_template('view_senha.html', msg="Copie a URL e mande para o cliente.",
                           senha=(request.root_url + "?code_access=" + s.dumps(passwords[aux].identifier)))


@app.route("/")
def passwords_getter():
    aux = int(s.loads(request.args.get("code_access")))

    senha = "Acesso não permitido."
    msg = "Falha ao acessar a senha. "

    if passwords[aux].alive():
        if datetime.now() <= passwords[aux].limit_time:
            if passwords[aux].open_times < passwords[aux].limit_access:
                passwords[aux].open_times += 1
                for rota in request.access_route:
                    app.logger.log(20, "%s acessou a senha %s.", rota, aux)

                senha = passwords[aux].password
                msg = "Senha:"
            else:
                for rota in request.access_route:
                    app.logger.log(20, "%s tentou acessar a senha %s, mas não conseguiu. - expirou as tentativas.",
                                   rota, aux)

                passwords[aux].kill('tentativas')
                msg += "- expirou as tentativas."
        else:
            for rota in request.access_route:
                app.logger.log(20, "%s tentou acessar a senha %s, mas não conseguiu. - tempo acabou.", rota, aux)

            passwords[aux].kill('tempo')
            msg += "- tempo acabou."
    else:
        for rota in request.access_route:
            app.logger.log(20, "%s tentou acessar a senha %s, mas ela já foi apagada.", rota, aux)

        msg += "- senha inexistente."

    return render_template('view_senha.html', msg=msg, senha=senha)


def job_function():
    app.logger.log(20, "verificando senhas.")
    for aux in range(0, len(passwords)):
        if passwords[aux].alive() and datetime.now() <= passwords[aux].limit_time:
            app.logger.log(20, "senha %s apagada.", aux)
            passwords[aux].kill('tempo')


cronometro = BackgroundScheduler()
cronometro.add_job(job_function, 'interval', minutes=30)  # futuramente poderá ser feito um estudo para
# otimizar a verificação
cronometro.start()

atexit.register(lambda: cronometro.shutdown(wait=False))

if __name__ == "__main__":
    app.run(debug=True)
