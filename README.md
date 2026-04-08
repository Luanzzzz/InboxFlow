# InboxFlow

**InboxFlow** é um sistema Django para triagem e organização operacional de mensagens e demandas. Ele transforma entradas dispersas em uma fila operacional clara, com classificação por categoria e urgência, sugestões heurísticas de próxima ação e um dashboard mínimo para acompanhar o fluxo.

---

## Visão geral

Operações pequenas e médias frequentemente não têm um sistema dedicado para tratar mensagens e demandas recebidas. O resultado prático é caos: urgências misturadas com baixa prioridade, mensagens perdidas, falta de visão operacional e dificuldade de decidir o que atender primeiro.

O InboxFlow resolve isso com um sistema Django estruturado que registra cada entrada, classifica categoria e urgência, sugere próxima ação e organiza tudo em filas operacionais com um dashboard de acompanhamento.

O MVP foi construído para ser pequeno, explicável e útil de verdade — com foco no domínio de triagem, não em tecnologia por tecnologia.

---

## Objetivo do projeto

### Objetivo de produto

Oferecer uma fila operacional clara para quem recebe mensagens e demandas em volume, sem conseguir organizar e priorizar o que precisa de resposta.

### Objetivo técnico

- Demonstrar Django com modelagem de domínio real
- Aplicar IA como camada de sugestão sobre problema concreto
- Construir um app com cara de sistema operacional, não só um CRUD

### Objetivo de portfólio

- Mostrar critério de escopo e decisão de engenharia
- Entregar um projeto postável, executável e explicável
- Provar domínio em Django + IA aplicada + automação operacional

---

## Problema que o projeto resolve

Muitas operações recebem mensagens e demandas por vários canais — WhatsApp, e-mail, Instagram, ligação — sem nenhuma fila clara para tratar isso.

O resultado é:

- urgências misturadas com mensagens de baixa prioridade
- mensagens esquecidas ou sem resposta
- falta de visão sobre o que está pendente
- dificuldade de decidir o que responder primeiro
- nenhuma separação entre "novo", "em andamento" e "resolvido"

O InboxFlow resolve exatamente essa dor: transforma entradas espalhadas em uma fila operacional organizada.

---

## Solução proposta

O sistema:

1. **Registra** cada mensagem ou demanda como um `InboxItem`
2. **Classifica** automaticamente categoria e urgência com base no conteúdo (heurística no MVP)
3. **Sugere** próxima ação e resposta inicial curta para cada item
4. **Organiza** os itens em filas operacionais por status
5. **Exibe** um dashboard com visão rápida de pendências, novos e urgentes
6. **Permite** triagem manual quando necessário, com aplicação das sugestões com um clique

---

## Principais funcionalidades

- Cadastro manual de mensagens e demandas
- Classificação por categoria: dúvida, comercial, suporte, financeiro, agendamento
- Classificação por urgência: baixa, média, alta
- Status operacional: novo → triado → aguardando resposta → resolvido
- Canal de origem modelado: WhatsApp, Instagram, e-mail, manual
- Sugestão heurística de categoria, urgência, próxima ação e resposta inicial
- Aplicação das sugestões com um clique, com avanço automático de status
- Filtros por status, categoria e urgência
- Dashboard com contadores operacionais e visão das filas
- Seed de dados de demo para apresentação
- Django Admin como painel operacional de apoio

---

## Regras de negócio principais

- Todo item entra com status **novo** por padrão
- Itens com urgência **alta** aparecem destacados na fila operacional
- A sugestão de próxima ação reflete o impacto operacional real — não é só um label
- Ao aplicar sugestões em um item com status `novo`, o sistema avança automaticamente para `triado`
- O canal WhatsApp é modelado no domínio, mas **sem integração real** no MVP — a arquitetura está preparada para isso ser adicionado no futuro
- Tags seguem como texto simples nesta fase — sem sistema de etiquetas complexo
- A camada de sugestão usa heurística sobre o conteúdo, não um modelo de linguagem dedicado no MVP

---

## Demonstração / Screenshots

> _Screenshots e GIFs serão adicionados na próxima iteração do projeto._

### Fluxo de demo recomendado

1. Acesse `http://127.0.0.1:8000/`
2. Veja os cards do dashboard: total, novos, urgentes, aguardando resposta, resolvidos
3. Navegue pelas filas operacionais
4. Abra um item e veja as sugestões heurísticas
5. Aplique categoria e urgência sugeridas com um clique
6. Observe o item avançar automaticamente de `novo` para `triado`
7. Crie um novo item manualmente e veja o fluxo completo

---

## Stack utilizada

| Camada         | Tecnologia                                   |
| -------------- | -------------------------------------------- |
| Framework      | Django 6.0.2                                 |
| Banco de dados | SQLite (MVP)                                 |
| Templates      | Django Templates                             |
| IA / Sugestão  | Heurística (camada `ai/` preparada para LLM) |
| Admin          | Django Admin                                 |
| Testes         | Django TestCase                              |

---

## Arquitetura / Estrutura do projeto

```text
InboxFlow/
├── app/
│   ├── ai/               ← camada de sugestão heurística
│   ├── core/             ← configuração Django (settings, urls raiz)
│   ├── inbox/            ← domínio principal do sistema
│   │   ├── management/   ← comandos customizados (seed, create_demo_admin)
│   │   ├── migrations/
│   │   ├── models.py     ← InboxItem e enums do domínio
│   │   ├── views.py      ← triagem, listagem, sugestões
│   │   ├── forms.py      ← formulários de criação e triagem
│   │   ├── urls.py       ← rotas do app
│   │   ├── admin.py      ← painel admin configurado
│   │   └── tests.py      ← testes do domínio
│   └── manage.py
├── templates/
│   └── inbox/            ← templates HTML do sistema
├── static/               ← arquivos estáticos
├── doc/
│   └── documentos/       ← documentação do projeto
├── requirements.txt
└── README.md
```

### Papel de cada parte

- **`inbox/`** → domínio principal: modelo, lógica de status, triagem e sugestão
- **`ai/`** → camada de sugestão: isolada e pronta para ser evoluída com LLM real
- **`core/`** → configuração central do Django
- **`templates/inbox/`** → interface operacional do sistema
- **`management/`** → comandos para seed de demo e setup local

---

## Fluxo principal do sistema

```
1. Uma nova mensagem ou demanda chega
         ↓
2. O usuário registra o item (manual ou futuramente via canal integrado)
         ↓
3. O sistema gera sugestões: categoria, urgência, próxima ação, resposta
         ↓
4. O usuário revisa e aplica as sugestões com um clique
         ↓
5. O item avança de "novo" para "triado" automaticamente
         ↓
6. O item entra nas filas operacionais corretas
         ↓
7. O dashboard reflete a situação geral em tempo real
```

---

## Rotas principais

| Rota                             | Descrição                                             |
| -------------------------------- | ----------------------------------------------------- |
| `/`                              | Dashboard + listagem principal com filtros            |
| `/items/create/`                 | Criar novo item manualmente                           |
| `/items/<id>/suggestions/`       | Gerar sugestões heurísticas para o item               |
| `/items/<id>/apply-suggestions/` | Aplicar as sugestões ao item                          |
| `/items/<id>/triage/`            | Triagem manual: atualizar status, categoria, urgência |
| `/admin/`                        | Django Admin como painel operacional de apoio         |

---

## Como rodar localmente

```powershell
# 1. Clonar o repositório
git clone https://github.com/Luanzzzz/InboxFlow.git
cd InboxFlow

# 2. Criar ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Aplicar migrations
python app/manage.py migrate

# 5. Rodar o servidor
python app/manage.py runserver
```

Acesse em: `http://127.0.0.1:8000/`

---

## Como rodar os testes

```powershell
python app/manage.py test inbox
```

Ou para verificar integridade do projeto:

```powershell
python app/manage.py check
```

---

## Seed / dados de exemplo

Para popular o sistema com dados variados para demo ou apresentação:

```powershell
# Cria o usuário de demo (teste / 123@)
python app/manage.py create_demo_admin

# Popula o banco com 6 itens de exemplo variados
python app/manage.py seed_demo_inbox --reset
```

O `--reset` limpa os `InboxItem` existentes antes de recriar a base.

Os itens criados cobrem:

- diferentes status (novo, triado, aguardando resposta, resolvido)
- diferentes urgências (baixa, média, alta)
- diferentes canais de origem
- sugestões heurísticas já preenchidas
- dashboard populado com dados reais de demo

**Credenciais locais de teste:**

- Usuário: `teste`
- Senha: `123@`

> Essas credenciais existem apenas para ambiente local. Não usar em produção.

---

## Fluxo local completo para demo

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app/manage.py migrate
python app/manage.py seed_demo_inbox --reset
python app/manage.py create_demo_admin
python app/manage.py check
python app/manage.py runserver
```

---

## Decisões de engenharia

### Django como framework principal

Django foi escolhido deliberadamente — não por ser o mais fácil, mas por mostrar repertório além de FastAPI e APIs simples. Um sistema de triagem operacional tem mais a ganhar com a estrutura de app, admin e ORM do Django do que com um microframework.

### SQLite no MVP

Reduz atrito de setup ao mínimo. O valor do projeto está no domínio e na operação, não na infraestrutura. A troca para PostgreSQL é direta quando fizer sentido.

### IA como camada de sugestão, não arquitetura agentic

A camada `ai/` existe e está isolada, mas o MVP usa heurística sobre o conteúdo — sem chamar nenhum LLM. Isso mantém o projeto executável sem dependências externas e deixa a evolução para IA real como próximo passo natural.

### WhatsApp modelado, não integrado

O canal WhatsApp existe no domínio (`canal_origem = whatsapp`) mas sem integração real no MVP. Isso é honestidade técnica: agrega valor narrativo e prepara a arquitetura sem explodir o escopo.

### UI simples e funcional

O valor principal do InboxFlow está no domínio de triagem e na operação, não na interface. Django Templates cumprem o papel sem reinventar frontend pesado no MVP.

### Escopo controlado por design

O projeto nasceu com uma especificação funcional, regras claras de fora-do-MVP e um protocolo operacional. Isso não é detalhe — é a razão pela qual o MVP fechou.

---

## O que ficou fora do MVP

Por decisão de escopo — não por falta de capacidade técnica:

- Integração real com WhatsApp (modelado, mas sem webhook/API)
- Integração real com Instagram e E-mail
- Sistema de notificações (e-mail ou push)
- Multiusuário avançado com permissões granulares
- Autenticação completa com recuperação de senha
- Workflow automático entre status
- Analytics avançados e relatórios
- Camada de produção completa (Postgres, Gunicorn, nginx)

---

## Roadmap / Próximos passos

- [ ] Integração real com WhatsApp via API (Twilio ou Meta Cloud API)
- [ ] Integração com e-mail (IMAP/SMTP para capturar demandas)
- [ ] Substituir heurística por chamada real a LLM na camada `ai/`
- [ ] Sistema de notificações para itens urgentes sem resposta
- [ ] Multiusuário com times e atribuição de responsável
- [ ] Analytics: tempo médio de resposta, volume por canal, taxa de resolução
- [ ] API REST para integração com outros sistemas
- [ ] Deploy em produção com PostgreSQL e Gunicorn

---

## Aprendizados do projeto

- **Modelagem de fila operacional** tem regras de negócio específicas — não é só um CRUD com status
- **Separar urgência, categoria e status** parece óbvio, mas exige decisão clara de domínio para não virar bagunça
- **IA aplicada a problema real** começa com heurística simples, não com arquitetura agentic. O valor está no caso de uso, não na complexidade técnica
- **Escopo pequeno e validável** é uma decisão de engenharia — não uma limitação. O MVP fechou porque o escopo foi definido com critério antes de escrever a primeira linha
- **Django Admin como ativo operacional** — quando configurado com cuidado, substitui um painel inteiro no MVP
- **Documentar antes de codificar** mudou a qualidade do desenvolvimento assistido por IA — o projeto nasceu com context.md, spec, architecture e engineering decisions antes do primeiro `manage.py startapp`

---

## Sobre o autor

**Luan**
Desenvolvedor com foco em projetos que resolvem problemas reais com tecnologia clara e critério de engenharia.

- GitHub: [github.com/Luanzzzz](https://github.com/Luanzzzz)
- LinkedIn: https://www.linkedin.com/in/luan-valentino-dos-santos-a2059928b/
- Instagram: luanvalentino.dev

---

## Licença

Este projeto é de uso livre para fins de estudo e portfólio.
