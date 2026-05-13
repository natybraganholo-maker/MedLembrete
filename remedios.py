"""
remedios.py — Gerenciamento de remédios cadastrados
=====================================================
CRUD básico: Create, Read, Update, Delete

Conceito novo: JSON com estruturas aninhadas
O arquivo remedios.json vai ter essa estrutura:
[
  {
    "nome": "Losartana",
    "dose": "1 comprimido",
    "horarios": ["08:00", "20:00"],
    "instrucoes": "tomar com água",
    "ativo": true,
    "cadastrado_em": "2024-01-15 08:30"
  }
]
"""

import json
import os

PASTA_DADOS = os.path.join(os.path.dirname(__file__), "dados")
ARQUIVO_REMEDIOS = os.path.join(PASTA_DADOS, "remedios.json")


def garantir_pasta():
    if not os.path.exists(PASTA_DADOS):
        os.makedirs(PASTA_DADOS)


def carregar_remedios():
    """
    Retorna lista de remédios cadastrados.
    Lista vazia se arquivo não existir.
    """
    garantir_pasta()
    try:
        with open(ARQUIVO_REMEDIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("  ⚠  Arquivo de remédios corrompido.")
        return []


def _salvar_todos(remedios):
    """
    Função interna (prefixo _ = uso interno do módulo).
    Salva a lista completa de remédios no arquivo.
    """
    garantir_pasta()
    with open(ARQUIVO_REMEDIOS, "w", encoding="utf-8") as f:
        json.dump(remedios, f, indent=2, ensure_ascii=False)


def salvar_remedios(remedios):
    """Alias público para salvar a lista completa."""
    _salvar_todos(remedios)


def adicionar_remedio(remedio):
    """Adiciona um novo remédio à lista e salva."""
    remedios = carregar_remedios()
    remedios.append(remedio)
    _salvar_todos(remedios)


def remover_remedio(indice):
    """Remove o remédio na posição 'indice' da lista."""
    remedios = carregar_remedios()
    if 0 <= indice < len(remedios):
        remedios.pop(indice)
        # pop(i) remove e retorna o item no índice i
        _salvar_todos(remedios)
