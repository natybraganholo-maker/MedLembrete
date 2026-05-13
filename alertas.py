"""
alertas.py — Lógica de verificação de alertas
===============================================
Conceito novo: comparar horários para disparar alertas
Conceito novo: janela de tempo (não só exatamente HH:MM)

Problema real: se o loop verifica a cada 30s, pode pular
exatamente o minuto do remédio. Solução: janela de 5 minutos.
Se o horário do remédio está entre "agora - 5min" e "agora",
o alerta dispara.
"""

import json
import os
from datetime import datetime, timedelta
from remedios import carregar_remedios

PASTA_DADOS = os.path.join(os.path.dirname(__file__), "dados")
ARQUIVO_HISTORICO = os.path.join(PASTA_DADOS, "historico_doses.json")
ARQUIVO_ALERTAS_DISPARADOS = os.path.join(PASTA_DADOS, "alertas_disparados.json")


def garantir_pasta():
    if not os.path.exists(PASTA_DADOS):
        os.makedirs(PASTA_DADOS)


def carregar_alertas_disparados():
    """
    Carrega registro de quais alertas já foram disparados hoje.
    Formato: {"2024-01-15": ["Losartana_08:00", "Atenolol_20:00"]}
    Isso evita que o mesmo alerta dispare várias vezes.
    """
    garantir_pasta()
    try:
        with open(ARQUIVO_ALERTAS_DISPARADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def marcar_alerta_disparado(nome_remedio, horario):
    """Registra que o alerta de um remédio já foi exibido hoje."""
    disparados = carregar_alertas_disparados()
    hoje = datetime.now().strftime("%Y-%m-%d")
    chave = f"{nome_remedio}_{horario}"

    if hoje not in disparados:
        disparados[hoje] = []

    if chave not in disparados[hoje]:
        disparados[hoje].append(chave)

    garantir_pasta()
    with open(ARQUIVO_ALERTAS_DISPARADOS, "w", encoding="utf-8") as f:
        json.dump(disparados, f, indent=2, ensure_ascii=False)


def alerta_ja_disparado(nome_remedio, horario):
    """Retorna True se esse alerta já foi mostrado hoje."""
    disparados = carregar_alertas_disparados()
    hoje = datetime.now().strftime("%Y-%m-%d")
    chave = f"{nome_remedio}_{horario}"
    return chave in disparados.get(hoje, [])


def verificar_alertas(hora_atual_str):
    """
    Verifica quais remédios precisam de alerta agora.

    Lógica da janela de tempo:
    - Converte hora_atual_str ("08:32") para objeto datetime
    - Para cada remédio e cada horário, verifica se está na janela
    - Janela: do horário previsto até 5 minutos depois
    - Ex: remédio às 08:30 → alerta dispara entre 08:30 e 08:35

    Retorna lista de dicionários com os alertas ativos.
    """
    remedios = carregar_remedios()
    alertas_ativos = []

    # Converte hora atual para objeto datetime (data de hoje + hora)
    hoje = datetime.now().strftime("%Y-%m-%d")
    try:
        agora = datetime.strptime(f"{hoje} {hora_atual_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return []

    for remedio in remedios:
        if not remedio.get("ativo", True):
            continue  # pula remédios inativos

        for horario in remedio.get("horarios", []):
            # Pula se alerta já foi disparado hoje para esse remédio+horário
            if alerta_ja_disparado(remedio["nome"], horario):
                continue

            try:
                # Converte horário do remédio para datetime de hoje
                horario_remedio = datetime.strptime(f"{hoje} {horario}", "%Y-%m-%d %H:%M")
            except ValueError:
                continue

            # Calcula a janela: horário previsto até +5 minutos
            janela_fim = horario_remedio + timedelta(minutes=5)
            # timedelta(minutes=5) representa 5 minutos de duração

            # Verifica se agora está dentro da janela
            if horario_remedio <= agora <= janela_fim:
                alertas_ativos.append({
                    "nome": remedio["nome"],
                    "dose": remedio["dose"],
                    "horario": horario,
                    "instrucoes": remedio.get("instrucoes"),
                })
                # Marca como disparado para não repetir
                marcar_alerta_disparado(remedio["nome"], horario)

    return alertas_ativos


def registrar_dose(nome, horario_previsto, tomou):
    """
    Salva no histórico se o remédio foi tomado ou não.

    Estrutura de cada registro:
    {
        "data": "2024-01-15",
        "hora_prevista": "08:00",
        "hora_registrada": "08:03",
        "remedio": "Losartana",
        "tomou": true
    }
    """
    garantir_pasta()

    # Carrega histórico existente
    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            historico = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        historico = []

    agora = datetime.now()
    registro = {
        "data": agora.strftime("%Y-%m-%d"),
        "hora_prevista": horario_previsto,
        "hora_registrada": agora.strftime("%H:%M"),
        "remedio": nome,
        "tomou": tomou,
    }

    historico.append(registro)

    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)
