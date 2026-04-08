# InboxFlow — arquitetura inicial

## Objetivo de engenharia

Criar um projeto Django pequeno, claro e explicável, com domínio bem definido e boa performance para desenvolvimento assistido por IA.

## Stack recomendada

- Django
- SQLite no MVP
- Django templates ou interface simples
- camada leve de serviços para IA/classificação

## Estrutura sugerida

```text
inboxflow/
  CLAW.md
  docs/
    context.md
    spec.md
    architecture.md
    engineering-decisions.md
  app/
    core/
    inbox/
    classification/
    dashboard/
    ai/
  templates/
  static/
  tests/
```

## Apps sugeridos

### `inbox`

Responsável por:

- modelo principal
- criação/listagem
- atualização básica

### `classification`

Responsável por:

- regras de categoria
- regras de urgência
- classificação manual/assistida

### `dashboard`

Responsável por:

- métricas
- filas operacionais
- visão geral

### `ai`

Responsável por:

- serviço de sugestão
- sugestão de categoria
- sugestão de urgência
- sugestão de próxima ação/resposta

## Regra importante

Não acoplar o MVP a integração real com WhatsApp.
Modelar o canal, mas manter a integração como evolução futura.
