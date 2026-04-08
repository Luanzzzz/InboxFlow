# InboxFlow — especificação funcional do MVP

## Objetivo

Definir claramente o MVP do InboxFlow para maximizar qualidade de execução com IA.

## Problema que resolve

Operações com mensagens/demandas frequentemente sofrem com:

- falta de triagem
- falta de prioridade
- ausência de fila clara
- urgência misturada com baixa prioridade
- dificuldade de decidir o que responder primeiro

## Resultado esperado do MVP

O sistema deve permitir:

- registrar uma mensagem/demanda
- indicar origem/canal
- classificar categoria
- classificar urgência
- sugerir próxima ação com IA
- sugerir resposta inicial curta com IA
- organizar itens em filas operacionais
- exibir dashboard simples

## Entidade principal

### InboxItem

Campos sugeridos:

- id
- contato_nome
- empresa
- canal_origem
- conteudo
- categoria
- urgencia
- status
- tags
- sugestao_proxima_acao
- sugestao_resposta
- created_at
- updated_at

## Enums sugeridos

### CanalOrigem

- whatsapp
- instagram
- email
- manual

### Categoria

- duvida
- comercial
- suporte
- financeiro
- agendamento
- outro

### Urgencia

- baixa
- media
- alta

### Status

- novo
- triado
- aguardando_resposta
- resolvido

## Regras de negócio mínimas

- todo item entra com status inicial
- IA pode sugerir categoria e urgência
- urgência alta precisa aparecer destacada
- dashboard deve mostrar filas operacionais
- WhatsApp entra como canal modelado, mas não precisa de integração real no MVP

## Dashboard mínimo

- total de itens
- novos
- urgentes
- aguardando resposta
- resolvidos

## Fora do MVP

- integração real com WhatsApp
- autenticação complexa
- multiusuário avançado
- notificações reais
- workflow complexo
- múltiplos canais integrados de verdade

## Critério central

O InboxFlow deve parecer um sistema operacional real de triagem, não só um cadastro de mensagens.
