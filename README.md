# Documentação da API - Sistema de Ensino com IA

## Visão Geral

Esta API fornece um sistema de ensino assistido por IA que combina análise de código e respostas pedagógicas. A API utiliza agentes especializados (code analyser e teacher) para fornecer feedback educacional sobre código.

## Configuração

- **Framework**: FastAPI
- **CORS**: Habilitado para todas as origens
- **Streaming**: Suporte a respostas em tempo real

## Endpoints

### 1. POST `/fake_stream`

**Descrição**: Endpoint de teste que simula streaming de texto com mensagens pré-definidas.

**Request Body**:
```json
{
  "session_id": "string (opcional)",
  "question": "string",
  "code": "string"
}
```

**Response**:
- **Tipo**: `text/plain` (streaming)
- **Headers**: `X-Session-ID` (UUID gerado automaticamente)
- **Conteúdo**: Stream de mensagens de teste em português

**Exemplo de uso**:
```bash
curl -X POST "http://localhost:8000/fake_stream" \
  -H "Content-Type: application/json" \
  -d '{"question": "teste", "code": "print(\"hello\")"}'
```

### 2. POST `/call/`

**Descrição**: Processa perguntas usando o sistema LangChain básico (resposta única).

**Request Body**:
```json
{
  "session_id": "string (opcional)",
  "question": "string",
  "code": "string"
}
```

**Response**:
- **Tipo**: JSON
- **Conteúdo**: Resposta processada pelo LangChain

### 3. POST `/call/agno/`

**Descrição**: Endpoint principal que utiliza o sistema completo com agentes especializados.

**Fluxo de processamento**:
1. Cria nova sessão se `session_id` não fornecido
2. Salva mensagem do estudante no banco
3. Executa análise de código via `code_analyser_agent`
4. Salva análise no banco
5. Gera resposta pedagógica via `teacher_agent`
6. Salva resposta do professor no banco
7. Retorna resposta em streaming

**Request Body**:
```json
{
  "session_id": "string (opcional)",
  "question": "string",
  "code": "string"
}
```

**Response**:
- **Tipo**: `text/plain` (streaming)
- **Headers**: `X-Session-ID` (ID da sessão)
- **Conteúdo**: Resposta do agente professor em streaming

**Exemplo de uso**:
```bash
curl -X POST "http://localhost:8000/call/agno/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Como posso melhorar este código?",
    "code": "def soma(a, b):\n    return a + b"
  }'
```

### 4. POST `/call/langchain/`

**Descrição**: Utiliza LangChain com streaming para respostas em tempo real.

**Request Body**:
```json
{
  "session_id": "string (opcional)",
  "question": "string",
  "code": "string"
}
```

**Response**:
- **Tipo**: `text/plain` (streaming)
- **Headers**: `X-Session-ID` (UUID gerado se não fornecido)
- **Conteúdo**: Resposta do LangChain em streaming

## Modelos de Dados

### RequestBodyQuestion
```python
{
  "session_id": "string | null",
  "question": "string",
  "code": "string"
}
```

## Arquitetura do Sistema

### Componentes Principais

1. **Code Analyser Agent**: Analisa o código fornecido
2. **Teacher Agent**: Gera respostas pedagógicas baseadas na análise
3. **Database Layer**: Persiste sessões, mensagens e análises
4. **LangChain Integration**: Processamento alternativo de linguagem natural

### Fluxo de Dados (Endpoint Principal `/call/agno/`)

```
Requisição → Criação/Recuperação de Sessão → Salvamento da Mensagem
    ↓
Análise de Código → Salvamento da Análise → Geração de Resposta Pedagógica
    ↓
Salvamento da Resposta → Streaming da Resposta ao Cliente
```

## Gerenciamento de Sessões

- Sessões são criadas automaticamente se não fornecidas
- Cada sessão mantém histórico de mensagens e análises
- Session ID é retornado no header `X-Session-ID`

## Tratamento de Erros

A API utiliza as convenções padrão do FastAPI para tratamento de erros:
- **422**: Erro de validação dos dados de entrada
- **500**: Erro interno do servidor

## Dependências

- **FastAPI**: Framework web
- **LangChain**: Processamento de linguagem natural
- **Agents**: Módulos especializados para análise e ensino
- **Database**: Sistema de persistência (via SessionDep)

## Considerações de Performance

- Endpoints com streaming (`/fake_stream`, `/call/agno/`, `/call/langchain/`) são otimizados para respostas em tempo real
- O endpoint `/call/agno/` inclui múltiplas operações de banco de dados que são executadas sequencialmente

## Segurança

- CORS habilitado para todas as origens (considere restringir em produção)
- Headers personalizados expostos via `expose_headers`