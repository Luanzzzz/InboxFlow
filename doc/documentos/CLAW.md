# CLAW.md — InboxFlow

## Objetivo do projeto

InboxFlow é um sistema Django + IA + automação para triagem e organização operacional de mensagens/demandas, criado como projeto de portfólio com foco em clareza de domínio e utilidade prática.

## Resultado esperado do agente

O agente deve ajudar a:

- manter escopo pequeno
- estruturar o domínio com clareza
- evitar overengineering
- implementar em fatias pequenas
- validar antes de concluir
- manter o WhatsApp como integração futura, não dependência atual

## Stack oficial

- Django
- SQLite
- templates simples
- camada leve de IA/sugestão

## Regras de trabalho

- seguir spec-first
- seguir o Método Akita
- não abrir integração real com WhatsApp agora
- não expandir escopo silenciosamente
- não construir arquitetura complexa desnecessária
- preferir clareza e velocidade

## Formato padrão de resposta

1. Entendimento
2. Plano
3. Execução
4. Validação
5. Próximo passo
