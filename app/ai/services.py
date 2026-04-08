from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from inbox.models import InboxItem


@dataclass(frozen=True, slots=True)
class InboxItemSuggestions:
    categoria: str
    urgencia: str
    proxima_acao: str
    resposta_inicial: str


class InboxSuggestionService:
    CATEGORY_KEYWORDS = {
        InboxItem.Categoria.FINANCEIRO: (
            "boleto",
            "fatura",
            "pagamento",
            "cobranca",
            "nota fiscal",
            "nota",
            "financeiro",
            "reembolso",
            "vencimento",
        ),
        InboxItem.Categoria.AGENDAMENTO: (
            "agendar",
            "agendamento",
            "agenda",
            "reagendar",
            "horario",
            "disponibilidade",
            "visita",
            "reuniao",
            "marcar",
        ),
        InboxItem.Categoria.SUPORTE: (
            "erro",
            "problema",
            "falha",
            "suporte",
            "nao funciona",
            "travou",
            "travado",
            "bug",
            "acesso",
            "instabilidade",
            "sistema caiu",
        ),
        InboxItem.Categoria.COMERCIAL: (
            "proposta",
            "orcamento",
            "preco",
            "valor",
            "contratar",
            "plano",
            "comercial",
            "comprar",
            "condicoes",
            "negociacao",
        ),
        InboxItem.Categoria.DUVIDA: (
            "duvida",
            "como",
            "qual",
            "quais",
            "informacao",
            "informacoes",
            "entender",
            "explicar",
            "posso",
        ),
    }
    HIGH_URGENCY_KEYWORDS = (
        "urgente",
        "agora",
        "imediato",
        "imediatamente",
        "hoje",
        "asap",
        "parado",
        "travado",
        "travou",
        "sistema caiu",
        "sem acesso",
        "critico",
    )
    MEDIUM_URGENCY_KEYWORDS = (
        "quando",
        "retorno",
        "pendente",
        "amanha",
        "esta semana",
        "prazo",
        "prioridade",
    )

    def suggest(self, item: InboxItem) -> InboxItemSuggestions:
        normalized_text = self._normalize_text(item)
        categoria = self._suggest_category(normalized_text)
        urgencia = self._suggest_urgency(normalized_text, categoria)
        proxima_acao = self._suggest_next_action(categoria, urgencia)
        resposta_inicial = self._suggest_short_reply(item, categoria, urgencia)

        return InboxItemSuggestions(
            categoria=categoria,
            urgencia=urgencia,
            proxima_acao=proxima_acao,
            resposta_inicial=resposta_inicial,
        )

    def _normalize_text(self, item: InboxItem) -> str:
        chunks = [
            item.contato_nome,
            item.empresa,
            item.tags,
            item.conteudo,
            item.canal_origem,
        ]
        raw_text = " ".join(chunk for chunk in chunks if chunk)
        normalized = unicodedata.normalize("NFKD", raw_text).encode(
            "ascii", "ignore"
        ).decode("ascii")
        normalized = normalized.lower()
        return re.sub(r"\s+", " ", normalized).strip()

    def _suggest_category(self, text: str) -> str:
        best_category = InboxItem.Categoria.OUTRO
        best_score = 0

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_category = category
                best_score = score

        if best_score == 0 and "?" in text:
            return InboxItem.Categoria.DUVIDA

        return best_category

    def _suggest_urgency(self, text: str, categoria: str) -> str:
        if any(keyword in text for keyword in self.HIGH_URGENCY_KEYWORDS):
            return InboxItem.Urgencia.ALTA

        if categoria == InboxItem.Categoria.SUPORTE and (
            "erro" in text or "nao funciona" in text
        ):
            return InboxItem.Urgencia.ALTA

        if any(keyword in text for keyword in self.MEDIUM_URGENCY_KEYWORDS):
            return InboxItem.Urgencia.MEDIA

        if categoria in {
            InboxItem.Categoria.COMERCIAL,
            InboxItem.Categoria.FINANCEIRO,
            InboxItem.Categoria.AGENDAMENTO,
        }:
            return InboxItem.Urgencia.MEDIA

        return InboxItem.Urgencia.BAIXA

    def _suggest_next_action(self, categoria: str, urgencia: str) -> str:
        if urgencia == InboxItem.Urgencia.ALTA:
            urgency_prefix = "Priorizar o retorno ainda hoje e registrar um responsavel."
        elif urgencia == InboxItem.Urgencia.MEDIA:
            urgency_prefix = "Registrar a triagem e alinhar o proximo retorno no ciclo atual."
        else:
            urgency_prefix = "Registrar a demanda e organizar a resposta no proximo bloco de atendimento."

        by_category = {
            InboxItem.Categoria.COMERCIAL: "Entender o escopo, confirmar interesse e enviar os proximos passos comerciais.",
            InboxItem.Categoria.SUPORTE: "Coletar contexto do problema, validar impacto e orientar a primeira acao tecnica.",
            InboxItem.Categoria.FINANCEIRO: "Checar a pendencia financeira no sistema e responder com a posicao objetiva.",
            InboxItem.Categoria.AGENDAMENTO: "Verificar disponibilidade e oferecer opcoes de data e horario.",
            InboxItem.Categoria.DUVIDA: "Responder a duvida de forma objetiva e identificar se existe acao complementar.",
            InboxItem.Categoria.OUTRO: "Revisar o contexto e definir a melhor fila operacional antes do proximo contato.",
        }

        return f"{urgency_prefix} {by_category[categoria]}"

    def _suggest_short_reply(
        self,
        item: InboxItem,
        categoria: str,
        urgencia: str,
    ) -> str:
        saudacao = f"Ola, {item.contato_nome}." if item.contato_nome else "Ola."

        by_category = {
            InboxItem.Categoria.COMERCIAL: "Recebi seu contato e vou revisar os detalhes para te responder com os proximos passos comerciais.",
            InboxItem.Categoria.SUPORTE: "Recebi seu relato e vou verificar o problema para te retornar com a primeira orientacao.",
            InboxItem.Categoria.FINANCEIRO: "Recebi sua mensagem e vou conferir essa pendencia financeira para te responder com clareza.",
            InboxItem.Categoria.AGENDAMENTO: "Recebi sua solicitacao e vou verificar as opcoes de agenda para te retornar em seguida.",
            InboxItem.Categoria.DUVIDA: "Recebi sua pergunta e vou te responder de forma objetiva em seguida.",
            InboxItem.Categoria.OUTRO: "Recebi sua mensagem e vou analisar o contexto para te orientar no proximo retorno.",
        }

        by_urgency = {
            InboxItem.Urgencia.ALTA: "Vou tratar isso com prioridade e retorno ainda hoje.",
            InboxItem.Urgencia.MEDIA: "Vou verificar isso agora e retorno em breve.",
            InboxItem.Urgencia.BAIXA: "Vou registrar isso e retorno com a proxima atualizacao.",
        }

        return f"{saudacao} {by_category[categoria]} {by_urgency[urgencia]}"
