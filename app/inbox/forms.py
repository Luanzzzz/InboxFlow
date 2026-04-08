from django import forms

from .models import InboxItem


class InboxItemForm(forms.ModelForm):
    class Meta:
        model = InboxItem
        fields = [
            "contato_nome",
            "empresa",
            "canal_origem",
            "conteudo",
            "categoria",
            "urgencia",
            "tags",
        ]
        labels = {
            "contato_nome": "Contato",
            "empresa": "Empresa",
            "canal_origem": "Canal de origem",
            "conteudo": "Mensagem ou demanda",
            "categoria": "Categoria",
            "urgencia": "Urgencia",
            "tags": "Tags",
        }
        help_texts = {
            "tags": "Separe as tags por virgula.",
        }
        widgets = {
            "conteudo": forms.Textarea(attrs={"rows": 5}),
            "tags": forms.TextInput(
                attrs={"placeholder": "cliente vip, renovacao, financeiro"}
            ),
        }

    def clean_tags(self) -> str:
        tags = self.cleaned_data["tags"]
        if not tags:
            return ""

        partes = [parte.strip() for parte in tags.split(",") if parte.strip()]
        return ", ".join(dict.fromkeys(partes))


class InboxItemTriageForm(forms.ModelForm):
    class Meta:
        model = InboxItem
        fields = ["status", "categoria", "urgencia"]
        labels = {
            "status": "Status",
            "categoria": "Categoria",
            "urgencia": "Urgencia",
        }


class InboxItemFilterForm(forms.Form):
    EMPTY_CHOICE = "__empty__"

    status = forms.ChoiceField(
        required=False,
        label="Status",
        choices=[("", "Todos os status"), *InboxItem.Status.choices],
    )
    categoria = forms.ChoiceField(
        required=False,
        label="Categoria",
        choices=[
            ("", "Todas as categorias"),
            (EMPTY_CHOICE, "Sem categoria"),
            *InboxItem.Categoria.choices,
        ],
    )
    urgencia = forms.ChoiceField(
        required=False,
        label="Urgencia",
        choices=[
            ("", "Todas as urgencias"),
            (EMPTY_CHOICE, "Sem urgencia"),
            *InboxItem.Urgencia.choices,
        ],
    )
