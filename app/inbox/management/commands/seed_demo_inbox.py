from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from ai.services import InboxSuggestionService
from inbox.models import InboxItem


class Command(BaseCommand):
    help = "Cria ou atualiza dados de exemplo para demo local do InboxFlow."

    DEMO_ITEMS = [
        {
            "contato_nome": "Fernanda",
            "empresa": "Nexo Distribuicao",
            "canal_origem": InboxItem.CanalOrigem.WHATSAPP,
            "conteudo": "Preciso de uma proposta urgente para ampliar o plano empresarial ainda hoje.",
            "categoria": "",
            "urgencia": "",
            "status": InboxItem.Status.NOVO,
            "tags": "demo, comercial, proposta",
            "offset_hours": 1,
        },
        {
            "contato_nome": "Lucas",
            "empresa": "Clinica Aurora",
            "canal_origem": InboxItem.CanalOrigem.EMAIL,
            "conteudo": "O sistema caiu e a equipe esta sem acesso ao painel. Preciso de ajuda urgente.",
            "categoria": InboxItem.Categoria.SUPORTE,
            "urgencia": InboxItem.Urgencia.ALTA,
            "status": InboxItem.Status.AGUARDANDO_RESPOSTA,
            "tags": "demo, suporte, incidente",
            "offset_hours": 3,
        },
        {
            "contato_nome": "Paula",
            "empresa": "Studio Vento",
            "canal_origem": InboxItem.CanalOrigem.INSTAGRAM,
            "conteudo": "Quero reagendar a visita tecnica para a proxima semana. Tem outro horario?",
            "categoria": InboxItem.Categoria.AGENDAMENTO,
            "urgencia": InboxItem.Urgencia.MEDIA,
            "status": InboxItem.Status.TRIADO,
            "tags": "demo, agenda, reagendamento",
            "offset_hours": 6,
        },
        {
            "contato_nome": "Roberto",
            "empresa": "Metal Norte",
            "canal_origem": InboxItem.CanalOrigem.EMAIL,
            "conteudo": "Preciso confirmar a fatura e a data de vencimento do boleto deste mes.",
            "categoria": InboxItem.Categoria.FINANCEIRO,
            "urgencia": InboxItem.Urgencia.MEDIA,
            "status": InboxItem.Status.AGUARDANDO_RESPOSTA,
            "tags": "demo, financeiro, boleto",
            "offset_hours": 10,
        },
        {
            "contato_nome": "Joana",
            "empresa": "Casa Flora",
            "canal_origem": InboxItem.CanalOrigem.MANUAL,
            "conteudo": "Tenho uma duvida sobre como funciona o onboarding e quais etapas preciso seguir.",
            "categoria": InboxItem.Categoria.DUVIDA,
            "urgencia": InboxItem.Urgencia.BAIXA,
            "status": InboxItem.Status.NOVO,
            "tags": "demo, duvida, onboarding",
            "offset_hours": 18,
        },
        {
            "contato_nome": "Marina",
            "empresa": "Orbita Consultoria",
            "canal_origem": InboxItem.CanalOrigem.WHATSAPP,
            "conteudo": "Obrigada pelo suporte. O acesso voltou e podemos encerrar esse atendimento.",
            "categoria": InboxItem.Categoria.SUPORTE,
            "urgencia": InboxItem.Urgencia.BAIXA,
            "status": InboxItem.Status.RESOLVIDO,
            "tags": "demo, suporte, resolvido",
            "offset_hours": 28,
        },
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Remove os InboxItems atuais antes de recriar os dados de demo.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted_count, _ = InboxItem.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Base de demo reiniciada. Registros removidos: {deleted_count}."
                )
            )

        suggestion_service = InboxSuggestionService()
        created_count = 0
        updated_count = 0
        now = timezone.now()

        for payload in self.DEMO_ITEMS:
            probe_item = InboxItem(
                contato_nome=payload["contato_nome"],
                empresa=payload["empresa"],
                canal_origem=payload["canal_origem"],
                conteudo=payload["conteudo"],
                tags=payload["tags"],
            )
            suggestions = suggestion_service.suggest(probe_item)

            defaults = {
                "canal_origem": payload["canal_origem"],
                "conteudo": payload["conteudo"],
                "categoria": payload["categoria"],
                "urgencia": payload["urgencia"],
                "status": payload["status"],
                "tags": payload["tags"],
                "sugestao_categoria": suggestions.categoria,
                "sugestao_urgencia": suggestions.urgencia,
                "sugestao_proxima_acao": suggestions.proxima_acao,
                "sugestao_resposta": suggestions.resposta_inicial,
            }

            inbox_item, created = InboxItem.objects.update_or_create(
                contato_nome=payload["contato_nome"],
                empresa=payload["empresa"],
                conteudo=payload["conteudo"],
                defaults=defaults,
            )

            timestamp = now - timedelta(hours=payload["offset_hours"])
            InboxItem.objects.filter(pk=inbox_item.pk).update(
                created_at=timestamp,
                updated_at=timestamp,
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        total = InboxItem.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed de demo concluido. Criados: {created_count}. Atualizados: {updated_count}. Total atual: {total}."
            )
        )
