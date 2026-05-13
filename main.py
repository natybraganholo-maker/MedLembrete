"""
MedLembrete — Alertas de Medicação
=====================================
Projeto 2 do portfólio: cuidado de idosos

Conceitos NOVOS em relação ao Projeto 1:
- Dicionários aninhados (remédio tem nome, dose, horários...)
- JSON para salvar estruturas mais complexas
- while True com time.sleep() para loop contínuo
- datetime para comparar horários
- Múltiplos horários por remédio
- Histórico de doses tomadas/perdidas
"""

import time
from datetime import datetime
from remedios import carregar_remedios, salvar_remedios, adicionar_remedio, remover_remedio
from alertas import verificar_alertas, registrar_dose
from historico import mostrar_historico, mostrar_adesao


# ─── Funções de exibição ────────────────────────────────────────────────────

def linha():
    print("─" * 52)

def cabecalho(titulo):
    print()
    linha()
    print(f"  💊  {titulo}")
    linha()

def menu_principal():
    cabecalho("MedLembrete — Alertas de Medicação")
    print()
    print("  1.  Monitorar alertas (modo ativo)")
    print("  2.  Cadastrar novo remédio")
    print("  3.  Ver remédios cadastrados")
    print("  4.  Remover remédio")
    print("  5.  Histórico de doses")
    print("  6.  Relatório de adesão")
    print("  7.  Sair")
    print()
    linha()

    while True:
        opcao = input("  Escolha [1-7]: ").strip()
        if opcao in ("1", "2", "3", "4", "5", "6", "7"):
            return opcao
        print("  ⚠  Digite um número de 1 a 7.")


# ─── Tela de cadastro de remédio ────────────────────────────────────────────

def tela_cadastrar():
    """
    Coleta as informações do remédio com o cuidador.
    Retorna um dicionário com todos os dados ou None se cancelar.
    """
    cabecalho("Cadastrar Remédio")
    print("  (pressione Enter em branco para cancelar)\n")

    # Nome do remédio
    nome = input("  Nome do remédio: ").strip()
    if not nome:
        return None

    # Dose
    dose = input("  Dose (ex: 1 comprimido, 5ml): ").strip()
    if not dose:
        return None

    # Horários — aceita múltiplos separados por vírgula
    print("  Horários (formato 24h, separe por vírgula)")
    print("  Exemplo: 08:00, 14:00, 20:00")
    horarios_raw = input("  Horários: ").strip()
    if not horarios_raw:
        return None

    # Processa e valida cada horário digitado
    horarios = []
    for h in horarios_raw.split(","):
        h = h.strip()
        if validar_horario(h):
            horarios.append(h)
        else:
            print(f"  ⚠  Horário inválido ignorado: '{h}' (use formato HH:MM)")

    if not horarios:
        print("  Nenhum horário válido informado. Cancelando.")
        return None

    # Instruções opcionais
    instrucoes = input("  Instruções (ex: tomar com água, após refeição): ").strip()

    # Monta o dicionário do remédio
    # Esse é um dicionário aninhado: a chave "horarios" tem uma lista como valor
    remedio = {
        "nome": nome,
        "dose": dose,
        "horarios": horarios,                          # lista de strings "HH:MM"
        "instrucoes": instrucoes if instrucoes else None,
        "ativo": True,
        "cadastrado_em": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    return remedio


def validar_horario(horario):
    """
    Valida se uma string está no formato HH:MM válido.
    Retorna True se válido, False se não.

    Exemplos:
        "08:00" → True
        "25:00" → False (hora inválida)
        "8:0"   → False (formato errado)
        "abc"   → False
    """
    try:
        # strptime tenta converter a string para datetime
        # Se não conseguir, lança ValueError
        datetime.strptime(horario, "%H:%M")
        return True
    except ValueError:
        return False


# ─── Tela de listagem de remédios ───────────────────────────────────────────

def tela_listar():
    """Exibe todos os remédios cadastrados de forma organizada."""
    remedios = carregar_remedios()

    cabecalho("Remédios Cadastrados")

    if not remedios:
        print("\n  Nenhum remédio cadastrado ainda.")
        print("  Use a opção 2 para adicionar o primeiro.\n")
        linha()
        return

    print(f"\n  {len(remedios)} remédio(s) cadastrado(s):\n")

    for i, remedio in enumerate(remedios, start=1):
        # enumerate(lista, start=1) retorna (índice, item) começando do 1
        status = "✓ ativo" if remedio.get("ativo") else "✗ inativo"
        horarios_fmt = ", ".join(remedio["horarios"])
        # ", ".join() une os itens de uma lista com ", " entre eles

        print(f"  [{i}] {remedio['nome']}")
        print(f"       Dose: {remedio['dose']}")
        print(f"       Horários: {horarios_fmt}")
        if remedio.get("instrucoes"):
            print(f"       Instruções: {remedio['instrucoes']}")
        print(f"       Status: {status}")
        print()

    linha()


# ─── Tela de remoção ────────────────────────────────────────────────────────

def tela_remover():
    """Permite ao cuidador remover um remédio da lista."""
    remedios = carregar_remedios()

    cabecalho("Remover Remédio")

    if not remedios:
        print("\n  Nenhum remédio cadastrado.\n")
        linha()
        return

    # Mostra lista numerada para escolha
    for i, r in enumerate(remedios, start=1):
        print(f"  [{i}] {r['nome']} — {', '.join(r['horarios'])}")

    print()
    escolha = input("  Número do remédio para remover (ou Enter para cancelar): ").strip()

    if not escolha:
        return

    try:
        indice = int(escolha) - 1  # -1 porque lista inicia em 0, mas mostramos de 1
        if 0 <= indice < len(remedios):
            nome = remedios[indice]["nome"]
            confirmar = input(f"  Remover '{nome}'? [S/N]: ").strip().upper()
            if confirmar == "S":
                remover_remedio(indice)
                print(f"  ✓ '{nome}' removido.\n")
        else:
            print("  ⚠  Número inválido.")
    except ValueError:
        print("  ⚠  Digite apenas o número.")


# ─── Modo de monitoramento ──────────────────────────────────────────────────

def modo_monitorar():
    """
    Loop principal de monitoramento.

    Fica rodando continuamente, verificando a cada 30 segundos
    se algum remédio precisa ser tomado agora.

    Conceito importante: while True + time.sleep()
    O programa não "trava" — ele verifica, dorme 30s, verifica de novo.
    """
    cabecalho("Modo Monitoramento Ativo")
    print()
    print("  Verificando alertas a cada 30 segundos.")
    print("  Pressione Ctrl+C para voltar ao menu.\n")
    linha()

    try:
        # try/except aqui captura o Ctrl+C (KeyboardInterrupt)
        while True:
            agora = datetime.now()
            hora_atual = agora.strftime("%H:%M")
            timestamp = agora.strftime("%H:%M:%S")

            print(f"\n  🕐  {timestamp} — verificando alertas...")

            alertas = verificar_alertas(hora_atual)

            if alertas:
                for alerta in alertas:
                    print()
                    print(f"  🔔  HORA DO REMÉDIO!")
                    print(f"  {'─'*40}")
                    print(f"  💊  {alerta['nome']}")
                    print(f"  📏  Dose: {alerta['dose']}")
                    if alerta.get("instrucoes"):
                        print(f"  📝  {alerta['instrucoes']}")
                    print(f"  {'─'*40}")

                    # Pergunta se tomou o remédio
                    resposta = input("  Tomou o remédio? [S/N]: ").strip().upper()
                    tomou = (resposta == "S")

                    # Registra no histórico
                    registrar_dose(
                        nome=alerta["nome"],
                        horario_previsto=alerta["horario"],
                        tomou=tomou
                    )

                    if tomou:
                        print("  ✓ Dose registrada!\n")
                    else:
                        print("  ⚠ Dose perdida registrada. Consulte o médico se necessário.\n")
            else:
                print("  Nenhum alerta no momento.")

            # Dorme 30 segundos antes de verificar de novo
            # time.sleep(segundos) pausa a execução
            time.sleep(30)

    except KeyboardInterrupt:
        # Ctrl+C lança KeyboardInterrupt — capturamos para sair limpo
        print("\n\n  Monitoramento pausado. Voltando ao menu...\n")


# ─── Ponto de entrada ───────────────────────────────────────────────────────

def main():
    while True:
        menu_principal()
        opcao = menu_principal()

        if opcao == "1":
            remedios = carregar_remedios()
            if not remedios:
                print("\n  ⚠  Cadastre pelo menos um remédio antes de monitorar.\n")
            else:
                modo_monitorar()

        elif opcao == "2":
            remedio = tela_cadastrar()
            if remedio:
                adicionar_remedio(remedio)
                print(f"\n  ✓ '{remedio['nome']}' cadastrado com sucesso!\n")

        elif opcao == "3":
            tela_listar()

        elif opcao == "4":
            tela_remover()

        elif opcao == "5":
            mostrar_historico()

        elif opcao == "6":
            mostrar_adesao()

        elif opcao == "7":
            print("\n  Até logo! Cuide bem. 💙\n")
            break

        input("  [Enter para continuar]")


if __name__ == "__main__":
    main()
