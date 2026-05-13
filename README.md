# MedLembrete

Alertas de medicação para cuidadores de idosos — controle de doses e adesão ao tratamento.

## O problema

Erros de medicação são uma das principais causas de internação em idosos. Dose esquecida, horário errado, remédio trocado — tudo isso acontece no dia a dia de quem cuida. O MedLembrete monitora ativamente os horários e registra cada dose para que nenhuma seja esquecida.

## O que o app faz

- Cadastro de remédios com múltiplos horários por dia
- Alertas automáticos no terminal com janela de 5 minutos
- ✓/✗ Confirmação de dose tomada ou perdida
- Histórico completo de todas as doses
- Relatório de adesão por remédio (últimos 7 dias)
- Alerta quando adesão cai abaixo de 80%

## Como rodar

```bash
git clone https://github.com/seu-usuario/medlembrete.git
cd medlembrete
python main.py
```

## Como usar

1. Vá em **opção 2** para cadastrar um remédio com nome, dose e horários
2. Vá em **opção 1** para ativar o monitoramento (deixe rodando)
3. Quando chegar a hora, o alerta aparece automaticamente
4. Confirme se tomou o remédio — o registro é salvo
5. Use **opção 6** para ver o relatório de adesão semanal

## Estrutura do projeto

```
medlembrete/
├── main.py          # Fluxo principal e menus
├── remedios.py      # CRUD de remédios (salvar, carregar, remover)
├── alertas.py       # Lógica de verificação de horários
├── historico.py     # Histórico de doses e relatório de adesão
├── dados/
│   ├── remedios.json            # Remédios cadastrados
│   ├── historico_doses.json     # Registro de cada dose
│   └── alertas_disparados.json  # Controle anti-duplicação
└── README.md
```

## Conceitos de Python praticados

| Conceito | Onde aparece |
|---|---|
| Dicionários aninhados | Estrutura de remédio em `remedios.py` |
| `json.load` / `json.dump` | Todos os módulos de dados |
| `while True` + `time.sleep()` | Loop de monitoramento em `main.py` |
| `datetime` e `timedelta` | Janela de alertas em `alertas.py` |
| `try/except` com `KeyboardInterrupt` | Saída limpa do monitoramento |
| Agrupamento de dados com dicionário | Relatório de adesão em `historico.py` |
| Validação de formato com `strptime` | Horários em `main.py` |
| `enumerate()` | Listagem numerada de remédios |
| `reversed()` e fatiamento `[-20:]` | Histórico em `historico.py` |
| Funções internas com prefixo `_` | `_salvar_todos()` em `remedios.py` |

## Evolução planejada

- [ ] Notificações sonoras (biblioteca `playsound`)
- [ ] Exportar relatório mensal em PDF
- [ ] Suporte a múltiplos pacientes
- [ ] Integração com o CuidaCheck (Projeto 1)

---

Segundo projeto de um portfólio focado em soluções para cuidadores de idosos.
Projeto anterior: [CuidaCheck](https://github.com/natybraganholo-maker/cuidacheck)
