# InboxFlow — decisões de engenharia

## Decisões iniciais

### 1. Framework

**Django**

Motivo:

- mostra repertório além de FastAPI
- ótimo para sistemas mais estruturados
- acelera CRUD/admin/modelagem inicial
- ajuda a construir um produto com cara de app real

### 2. Banco

**SQLite no MVP**

Motivo:

- simplicidade
- velocidade
- menor atrito para execução rápida

### 3. IA

**camada simples de sugestão, não arquitetura agentic complexa**

Motivo:

- foco em caso de uso
- reduz escopo
- melhora chance de fechar rápido

### 4. WhatsApp

**canal previsto, integração futura**

Motivo:

- agrega valor sem explodir escopo
- mantém honestidade técnica
- melhora narrativa de produto

### 5. UI

**simples e funcional**

Motivo:

- o valor principal está no domínio e na operação
- não vale reinventar frontend pesado no MVP
