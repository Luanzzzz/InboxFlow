from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from ai.services import InboxSuggestionService
from django.urls import reverse
from django.test import TestCase

from .models import InboxItem


class InboxItemModelTests(TestCase):
    def test_item_starts_with_expected_defaults(self) -> None:
        item = InboxItem.objects.create(conteudo="Cliente pediu atualizacao do pedido.")

        self.assertEqual(item.canal_origem, InboxItem.CanalOrigem.MANUAL)
        self.assertEqual(item.status, InboxItem.Status.NOVO)
        self.assertEqual(item.categoria, "")
        self.assertEqual(item.urgencia, "")
        self.assertEqual(item.sugestao_categoria, "")
        self.assertEqual(item.sugestao_urgencia, "")

    def test_string_representation_uses_primary_identifier(self) -> None:
        item = InboxItem.objects.create(
            contato_nome="Maria",
            canal_origem=InboxItem.CanalOrigem.EMAIL,
            conteudo="Preciso de ajuda com o faturamento.",
        )

        self.assertIn("Maria", str(item))
        self.assertIn("E-mail", str(item))


class InboxItemFlowTests(TestCase):
    def test_list_page_renders_empty_state(self) -> None:
        response = self.client.get(reverse("inbox:item_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nenhum item registrado ainda.")
        self.assertEqual(response.context["dashboard_metrics"]["total"], 0)
        self.assertContains(response, "Dashboard minimo")

    def test_post_creates_item_and_shows_it_in_queue(self) -> None:
        response = self.client.post(
            reverse("inbox:item_create"),
            data={
                "contato_nome": "Ana",
                "empresa": "Acme",
                "canal_origem": InboxItem.CanalOrigem.WHATSAPP,
                "conteudo": "Cliente pediu retorno sobre proposta comercial.",
                "categoria": InboxItem.Categoria.COMERCIAL,
                "urgencia": InboxItem.Urgencia.ALTA,
                "tags": "vip, proposta, vip",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(InboxItem.objects.count(), 1)

        item = InboxItem.objects.get()
        self.assertEqual(item.status, InboxItem.Status.NOVO)
        self.assertEqual(item.tags, "vip, proposta")
        self.assertContains(response, "Inbox item criado com sucesso.")
        self.assertContains(response, "Ana")
        self.assertContains(response, "Acme")

    def test_post_updates_manual_triage(self) -> None:
        item = InboxItem.objects.create(
            contato_nome="Bruno",
            canal_origem=InboxItem.CanalOrigem.MANUAL,
            conteudo="Cliente quer reagendar a visita tecnica.",
        )

        response = self.client.post(
            reverse("inbox:item_triage_update", args=[item.pk]),
            data={
                f"triage-{item.pk}-status": InboxItem.Status.TRIADO,
                f"triage-{item.pk}-categoria": InboxItem.Categoria.AGENDAMENTO,
                f"triage-{item.pk}-urgencia": InboxItem.Urgencia.MEDIA,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.status, InboxItem.Status.TRIADO)
        self.assertEqual(item.categoria, InboxItem.Categoria.AGENDAMENTO)
        self.assertEqual(item.urgencia, InboxItem.Urgencia.MEDIA)
        self.assertContains(response, "Triagem do item")

    def test_invalid_triage_post_returns_errors(self) -> None:
        item = InboxItem.objects.create(
            contato_nome="Carla",
            conteudo="Mensagem sem classificacao ainda.",
        )

        response = self.client.post(
            reverse("inbox:item_triage_update", args=[item.pk]),
            data={
                f"triage-{item.pk}-status": "invalido",
                f"triage-{item.pk}-categoria": InboxItem.Categoria.OUTRO,
                f"triage-{item.pk}-urgencia": InboxItem.Urgencia.BAIXA,
            },
        )

        self.assertEqual(response.status_code, 400)
        item.refresh_from_db()
        self.assertEqual(item.status, InboxItem.Status.NOVO)
        self.assertContains(
            response,
            "Nao foi possivel atualizar a triagem",
            status_code=400,
        )

    def test_post_generates_and_persists_suggestions(self) -> None:
        item = InboxItem.objects.create(
            contato_nome="Larissa",
            canal_origem=InboxItem.CanalOrigem.WHATSAPP,
            conteudo="Preciso de uma proposta urgente para o plano empresarial ainda hoje.",
        )

        response = self.client.post(
            reverse("inbox:item_generate_suggestions", args=[item.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.sugestao_categoria, InboxItem.Categoria.COMERCIAL)
        self.assertEqual(item.sugestao_urgencia, InboxItem.Urgencia.ALTA)
        self.assertIn("proximos passos comerciais", item.sugestao_proxima_acao)
        self.assertIn("prioridade", item.sugestao_resposta.lower())
        self.assertEqual(item.categoria, "")
        self.assertEqual(item.urgencia, "")
        self.assertContains(response, "Sugestoes geradas para o item")
        self.assertContains(response, "Categoria sugerida: Comercial")

    def test_post_applies_suggestions_to_manual_triage(self) -> None:
        item = InboxItem.objects.create(
            contato_nome="Helena",
            canal_origem=InboxItem.CanalOrigem.EMAIL,
            conteudo="Preciso de uma proposta urgente para renovar o contrato ainda hoje.",
            sugestao_categoria=InboxItem.Categoria.COMERCIAL,
            sugestao_urgencia=InboxItem.Urgencia.ALTA,
            status=InboxItem.Status.NOVO,
        )

        response = self.client.post(
            reverse("inbox:item_apply_suggestions", args=[item.pk]),
            data={"next_query": "status=novo"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.categoria, InboxItem.Categoria.COMERCIAL)
        self.assertEqual(item.urgencia, InboxItem.Urgencia.ALTA)
        self.assertEqual(item.status, InboxItem.Status.TRIADO)
        self.assertEqual(response.context["filtered_count"], 0)
        self.assertEqual(response.context["item_cards"], [])
        self.assertContains(response, "Sugestoes aplicadas na triagem do item")

    def test_post_apply_suggestions_requires_existing_suggestions(self) -> None:
        item = InboxItem.objects.create(
            contato_nome="Igor",
            conteudo="Mensagem sem sugestoes ainda.",
        )

        response = self.client.post(
            reverse("inbox:item_apply_suggestions", args=[item.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.categoria, "")
        self.assertEqual(item.urgencia, "")
        self.assertContains(response, "Nao ha sugestoes aplicaveis para o item")

    def test_post_apply_suggestions_preserves_non_novo_status(self) -> None:
        item = InboxItem.objects.create(
            contato_nome="Jade",
            conteudo="Atendimento ja esta aguardando retorno.",
            sugestao_categoria=InboxItem.Categoria.SUPORTE,
            sugestao_urgencia=InboxItem.Urgencia.MEDIA,
            status=InboxItem.Status.AGUARDANDO_RESPOSTA,
        )

        response = self.client.post(
            reverse("inbox:item_apply_suggestions", args=[item.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.categoria, InboxItem.Categoria.SUPORTE)
        self.assertEqual(item.urgencia, InboxItem.Urgencia.MEDIA)
        self.assertEqual(item.status, InboxItem.Status.AGUARDANDO_RESPOSTA)

    def test_list_filters_by_status_and_urgencia(self) -> None:
        InboxItem.objects.create(
            contato_nome="Ana",
            conteudo="Pedido novo e urgente.",
            status=InboxItem.Status.NOVO,
            urgencia=InboxItem.Urgencia.ALTA,
        )
        InboxItem.objects.create(
            contato_nome="Bruno",
            conteudo="Demanda resolvida.",
            status=InboxItem.Status.RESOLVIDO,
            urgencia=InboxItem.Urgencia.BAIXA,
        )

        response = self.client.get(
            reverse("inbox:item_list"),
            {
                "status": InboxItem.Status.NOVO,
                "urgencia": InboxItem.Urgencia.ALTA,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["filtered_count"], 1)
        filtered_names = [card["item"].contato_nome for card in response.context["item_cards"]]
        self.assertEqual(filtered_names, ["Ana"])
        self.assertContains(response, "1 de 2 item(ns)")

    def test_list_filters_uncategorized_items(self) -> None:
        InboxItem.objects.create(
            contato_nome="Carla",
            conteudo="Mensagem ainda sem triagem.",
            categoria="",
        )
        InboxItem.objects.create(
            contato_nome="Diego",
            conteudo="Solicitou proposta comercial.",
            categoria=InboxItem.Categoria.COMERCIAL,
        )

        response = self.client.get(
            reverse("inbox:item_list"),
            {
                "categoria": "__empty__",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["filtered_count"], 1)
        filtered_names = [card["item"].contato_nome for card in response.context["item_cards"]]
        self.assertEqual(filtered_names, ["Carla"])

    def test_triage_redirect_preserves_active_filters(self) -> None:
        item = InboxItem.objects.create(
            contato_nome="Erica",
            conteudo="Pedido aguardando triagem.",
            status=InboxItem.Status.NOVO,
        )

        response = self.client.post(
            reverse("inbox:item_triage_update", args=[item.pk]),
            data={
                "next_query": f"status={InboxItem.Status.NOVO}",
                f"triage-{item.pk}-status": InboxItem.Status.RESOLVIDO,
                f"triage-{item.pk}-categoria": "",
                f"triage-{item.pk}-urgencia": "",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["filtered_count"], 0)
        self.assertEqual(response.context["item_cards"], [])
        self.assertContains(response, "Nenhum item encontrado com os filtros atuais.")

    def test_dashboard_shows_operational_metrics_and_queues(self) -> None:
        InboxItem.objects.create(
            contato_nome="Alice",
            conteudo="Entrada nova.",
            status=InboxItem.Status.NOVO,
            urgencia=InboxItem.Urgencia.ALTA,
        )
        InboxItem.objects.create(
            contato_nome="Beto",
            conteudo="Aguardando retorno.",
            status=InboxItem.Status.AGUARDANDO_RESPOSTA,
            urgencia=InboxItem.Urgencia.MEDIA,
        )
        InboxItem.objects.create(
            contato_nome="Caio",
            conteudo="Resolvido ontem.",
            status=InboxItem.Status.RESOLVIDO,
            urgencia=InboxItem.Urgencia.BAIXA,
        )

        response = self.client.get(reverse("inbox:item_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["dashboard_metrics"],
            {
                "total": 3,
                "novos": 1,
                "urgentes": 1,
                "aguardando_resposta": 1,
                "resolvidos": 1,
            },
        )
        sections = {section["title"]: section for section in response.context["queue_sections"]}
        self.assertEqual(sections["Novos"]["count"], 1)
        self.assertEqual(sections["Urgentes"]["count"], 1)
        self.assertEqual(sections["Aguardando resposta"]["count"], 1)
        self.assertEqual(sections["Resolvidos"]["count"], 1)
        self.assertContains(response, "Abrir fila")


class InboxSuggestionServiceTests(TestCase):
    def test_service_uses_support_and_high_urgency_fallback(self) -> None:
        item = InboxItem(
            contato_nome="Marcos",
            canal_origem=InboxItem.CanalOrigem.EMAIL,
            conteudo="Sistema caiu e esta travado. Cliente sem acesso e precisa de ajuda urgente.",
        )

        suggestions = InboxSuggestionService().suggest(item)

        self.assertEqual(suggestions.categoria, InboxItem.Categoria.SUPORTE)
        self.assertEqual(suggestions.urgencia, InboxItem.Urgencia.ALTA)
        self.assertIn("acao tecnica", suggestions.proxima_acao)
        self.assertIn("prioridade", suggestions.resposta_inicial.lower())

    def test_service_falls_back_to_outro_and_baixa(self) -> None:
        item = InboxItem(
            contato_nome="Paula",
            canal_origem=InboxItem.CanalOrigem.MANUAL,
            conteudo="Quero registrar este contato para acompanhamento futuro.",
        )

        suggestions = InboxSuggestionService().suggest(item)

        self.assertEqual(suggestions.categoria, InboxItem.Categoria.OUTRO)
        self.assertEqual(suggestions.urgencia, InboxItem.Urgencia.BAIXA)
        self.assertTrue(suggestions.proxima_acao)
        self.assertTrue(suggestions.resposta_inicial)


class InboxDemoSeedCommandTests(TestCase):
    def test_seed_demo_command_creates_reusable_demo_data(self) -> None:
        stdout = StringIO()

        call_command("seed_demo_inbox", stdout=stdout)

        self.assertEqual(InboxItem.objects.count(), 6)
        self.assertTrue(InboxItem.objects.filter(tags__icontains="demo").exists())
        self.assertTrue(
            InboxItem.objects.filter(status=InboxItem.Status.AGUARDANDO_RESPOSTA).exists()
        )
        self.assertTrue(
            InboxItem.objects.filter(sugestao_proxima_acao__gt="").exists()
        )
        self.assertIn("Seed de demo concluido", stdout.getvalue())

        call_command("seed_demo_inbox", stdout=stdout)
        self.assertEqual(InboxItem.objects.count(), 6)

    def test_seed_demo_command_reset_replaces_existing_items(self) -> None:
        InboxItem.objects.create(
            contato_nome="Registro manual",
            conteudo="Item fora do seed.",
        )

        call_command("seed_demo_inbox", reset=True)

        self.assertEqual(InboxItem.objects.count(), 6)
        self.assertFalse(
            InboxItem.objects.filter(contato_nome="Registro manual").exists()
        )

    def test_seed_demo_supports_demo_smoke_flow(self) -> None:
        call_command("seed_demo_inbox", reset=True)

        response = self.client.get(reverse("inbox:item_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["dashboard_metrics"]["total"], 6)
        self.assertContains(response, "Fernanda")
        self.assertContains(response, "Dashboard minimo")
        self.assertContains(response, "Urgentes")
        self.assertContains(response, "Aplicar na triagem")


class DemoAdminCommandTests(TestCase):
    def test_create_demo_admin_creates_or_updates_superuser(self) -> None:
        stdout = StringIO()

        call_command("create_demo_admin", stdout=stdout)

        user_model = get_user_model()
        user = user_model.objects.get(username="teste")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("123@"))
        self.assertIn("teste / 123@", stdout.getvalue())

        user.is_staff = False
        user.is_superuser = False
        user.set_password("senha-antiga")
        user.save()

        call_command("create_demo_admin", stdout=stdout)

        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("123@"))
