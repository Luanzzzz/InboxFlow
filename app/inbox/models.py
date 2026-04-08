from django.db import models


class InboxItem(models.Model):
    class CanalOrigem(models.TextChoices):
        WHATSAPP = "whatsapp", "WhatsApp"
        INSTAGRAM = "instagram", "Instagram"
        EMAIL = "email", "E-mail"
        MANUAL = "manual", "Manual"

    class Categoria(models.TextChoices):
        DUVIDA = "duvida", "Duvida"
        COMERCIAL = "comercial", "Comercial"
        SUPORTE = "suporte", "Suporte"
        FINANCEIRO = "financeiro", "Financeiro"
        AGENDAMENTO = "agendamento", "Agendamento"
        OUTRO = "outro", "Outro"

    class Urgencia(models.TextChoices):
        BAIXA = "baixa", "Baixa"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"

    class Status(models.TextChoices):
        NOVO = "novo", "Novo"
        TRIADO = "triado", "Triado"
        AGUARDANDO_RESPOSTA = "aguardando_resposta", "Aguardando resposta"
        RESOLVIDO = "resolvido", "Resolvido"

    contato_nome = models.CharField(max_length=150, blank=True, default="")
    empresa = models.CharField(max_length=150, blank=True, default="")
    canal_origem = models.CharField(
        max_length=20,
        choices=CanalOrigem.choices,
        default=CanalOrigem.MANUAL,
    )
    conteudo = models.TextField()
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        blank=True,
        default="",
    )
    urgencia = models.CharField(
        max_length=10,
        choices=Urgencia.choices,
        blank=True,
        default="",
    )
    sugestao_categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        blank=True,
        default="",
    )
    sugestao_urgencia = models.CharField(
        max_length=10,
        choices=Urgencia.choices,
        blank=True,
        default="",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.NOVO,
    )
    tags = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Lista simples de tags separadas por virgula.",
    )
    sugestao_proxima_acao = models.TextField(blank=True, default="")
    sugestao_resposta = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Inbox item"
        verbose_name_plural = "Inbox items"

    def __str__(self) -> str:
        principal = self.contato_nome or self.empresa or "Sem identificacao"
        prefixo = f"#{self.pk}" if self.pk else "novo"
        return f"{prefixo} | {self.get_canal_origem_display()} | {principal}"

    @property
    def tem_sugestoes(self) -> bool:
        return any(
            [
                self.sugestao_categoria,
                self.sugestao_urgencia,
                self.sugestao_proxima_acao,
                self.sugestao_resposta,
            ]
        )
