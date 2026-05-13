"""
historico.py — Histórico de doses e relatório de adesão
=========================================================
Conceito novo: agrupar dados de uma lista por critério
Conceito novo: calcular porcentagem de adesão por remédio
"""

import json
import os
from datetime import datetime, timedelta

PASTA_DADOS = os.path.join(os.path.dirname(__file__), "dados")
ARQUIVO_HISTORICO = os.path.join(PASTA_DADOS, "historico_doses.json")


def carregar_historico_doses():
    """Retorna lista completa de registros de doses."""
    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def mostrar_historico():
    """Exibe os últimos 20 registros do histórico."""
    historico = carregar_historico_doses()

    print()
    print("─" * 52)
    print("  📋  HISTÓRICO DE DOSES")
    print("─" * 52)

    if not historico:
        print("\n  Nenhuma dose registrada ainda.\n")
        print("─" * 52)
        return

    # Mostra os últimos 20 registros (mais recentes primeiro)
    # [-20:] pega os últimos 20 itens da lista
    # reversed() inverte para mostrar o mais recente primeiro
    ultimos = list(reversed(historico[-20:]))

    print(f"\n  Últimos {len(ultimos)} registros:\n")

    for reg in ultimos:
        icone = "✓" if reg["tomou"] else "✗"
        data_fmt = datetime.strptime(reg["data"], "%Y-%m-%d").strftime("%d/%m")
        status = "Tomado" if reg["tomou"] else "Perdido"

        print(f"  {icone}  {data_fmt} {reg['hora_prevista']}  {reg['remedio']:<20} {status}")

    print()
    print("─" * 52)


def mostrar_adesao():
    """
    Calcula e exibe a taxa de adesão por remédio nos últimos 7 dias.
    Adesão = doses tomadas / doses previstas × 100
    """
    historico = carregar_historico_doses()

    print()
    print("─" * 52)
    print("  📊  RELATÓRIO DE ADESÃO — ÚLTIMOS 7 DIAS")
    print("─" * 52)

    if not historico:
        print("\n  Nenhuma dose registrada ainda.\n")
        print("─" * 52)
        return

    # Filtra registros dos últimos 7 dias
    hoje = datetime.now().date()
    sete_dias = hoje - timedelta(days=7)

    registros_recentes = []
    for reg in historico:
        try:
            data_reg = datetime.strptime(reg["data"], "%Y-%m-%d").date()
            if data_reg >= sete_dias:
                registros_recentes.append(reg)
        except ValueError:
            continue

    if not registros_recentes:
        print("\n  Sem registros nos últimos 7 dias.\n")
        print("─" * 52)
        return

    # Agrupa por remédio usando um dicionário
    # Estrutura: {"Losartana": {"tomou": 12, "total": 14}}
    por_remedio = {}

    for reg in registros_recentes:
        nome = reg["remedio"]

        # Se remédio não está no dicionário ainda, inicializa
        if nome not in por_remedio:
            por_remedio[nome] = {"tomou": 0, "total": 0}

        por_remedio[nome]["total"] += 1
        if reg["tomou"]:
            por_remedio[nome]["tomou"] += 1

    # Exibe resultado por remédio
    print()
    for nome, dados in por_remedio.items():
        total = dados["total"]
        tomou = dados["tomou"]
        adesao = (tomou / total) * 100 if total > 0 else 0

        # Ícone baseado na taxa de adesão
        if adesao >= 90:
            icone = "🟢"
        elif adesao >= 70:
            icone = "🟡"
        else:
            icone = "🔴"

        # Barra de progresso compacta
        preenchido = int(adesao / 10)  # 0 a 10 blocos
        barra = "█" * preenchido + "░" * (10 - preenchido)

        print(f"  {icone}  {nome}")
        print(f"       [{barra}] {adesao:.0f}%  ({tomou}/{total} doses)")
        print()

    # Alerta geral se adesão geral for baixa
    total_geral = sum(d["total"] for d in por_remedio.values())
    tomou_geral = sum(d["tomou"] for d in por_remedio.values())
    adesao_geral = (tomou_geral / total_geral) * 100 if total_geral > 0 else 0

    print(f"  Adesão geral: {adesao_geral:.0f}%")

    if adesao_geral < 80:
        print()
        print("  ⚠  Adesão abaixo de 80%. Considere conversar")
        print("     com o médico sobre o esquema de medicação.")

    print()
    print("─" * 52)
