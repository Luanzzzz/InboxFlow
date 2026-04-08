from django.contrib import admin

from .models import InboxItem


@admin.register(InboxItem)
class InboxItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "contato_nome",
        "empresa",
        "canal_origem",
        "categoria",
        "urgencia",
        "sugestao_categoria",
        "sugestao_urgencia",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("canal_origem", "categoria", "urgencia", "status")
    search_fields = ("contato_nome", "empresa", "conteudo", "tags")
    ordering = ("-created_at",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "sugestao_categoria",
        "sugestao_urgencia",
        "sugestao_proxima_acao",
        "sugestao_resposta",
    )
    fieldsets = (
        (
            "Dados principais",
            {
                "fields": (
                    "contato_nome",
                    "empresa",
                    "canal_origem",
                    "conteudo",
                    "tags",
                )
            },
        ),
        (
            "Triagem",
            {"fields": ("status", "categoria", "urgencia")},
        ),
        (
            "Sugestoes do MVP",
            {
                "fields": (
                    "sugestao_categoria",
                    "sugestao_urgencia",
                    "sugestao_proxima_acao",
                    "sugestao_resposta",
                )
            },
        ),
        (
            "Auditoria",
            {"fields": ("created_at", "updated_at")},
        ),
    )
