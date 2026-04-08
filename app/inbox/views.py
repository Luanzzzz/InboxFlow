from django.contrib import messages
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from ai.services import InboxSuggestionService

from .forms import InboxItemFilterForm, InboxItemForm, InboxItemTriageForm
from .models import InboxItem


def _build_triage_forms(items, bound_forms: dict[int, InboxItemTriageForm] | None = None):
    bound_forms = bound_forms or {}
    return [
        {
            "item": item,
            "triage_form": bound_forms.get(
                item.pk,
                InboxItemTriageForm(instance=item, prefix=f"triage-{item.pk}"),
            ),
        }
        for item in items
    ]


def _apply_filters(items, filter_form: InboxItemFilterForm):
    if not filter_form.is_valid():
        return items

    status = filter_form.cleaned_data["status"]
    categoria = filter_form.cleaned_data["categoria"]
    urgencia = filter_form.cleaned_data["urgencia"]

    if status:
        items = items.filter(status=status)

    if categoria == InboxItemFilterForm.EMPTY_CHOICE:
        items = items.filter(categoria="")
    elif categoria:
        items = items.filter(categoria=categoria)

    if urgencia == InboxItemFilterForm.EMPTY_CHOICE:
        items = items.filter(urgencia="")
    elif urgencia:
        items = items.filter(urgencia=urgencia)

    return items


def _has_active_filters(filter_form: InboxItemFilterForm) -> bool:
    return filter_form.is_valid() and any(filter_form.cleaned_data.values())


def _build_dashboard_context(items):
    novos = items.filter(status=InboxItem.Status.NOVO)
    urgentes = items.filter(urgencia=InboxItem.Urgencia.ALTA)
    aguardando_resposta = items.filter(status=InboxItem.Status.AGUARDANDO_RESPOSTA)
    resolvidos = items.filter(status=InboxItem.Status.RESOLVIDO)

    return {
        "dashboard_metrics": {
            "total": items.count(),
            "novos": novos.count(),
            "urgentes": urgentes.count(),
            "aguardando_resposta": aguardando_resposta.count(),
            "resolvidos": resolvidos.count(),
        },
        "queue_sections": [
            {
                "title": "Novos",
                "description": "Entradas recentes que ainda nao passaram por triagem.",
                "count": novos.count(),
                "items": list(novos[:4]),
                "query": "status=novo",
                "empty_message": "Nenhum item novo agora.",
            },
            {
                "title": "Urgentes",
                "description": "Itens com urgencia alta que pedem atencao imediata.",
                "count": urgentes.count(),
                "items": list(urgentes[:4]),
                "query": "urgencia=alta",
                "empty_message": "Nenhum item urgente agora.",
            },
            {
                "title": "Aguardando resposta",
                "description": "Demandas ja triadas que dependem de retorno operacional.",
                "count": aguardando_resposta.count(),
                "items": list(aguardando_resposta[:4]),
                "query": "status=aguardando_resposta",
                "empty_message": "Nenhum item aguardando resposta agora.",
            },
            {
                "title": "Resolvidos",
                "description": "Itens concluidos e mantidos no historico recente.",
                "count": resolvidos.count(),
                "items": list(resolvidos[:4]),
                "query": "status=resolvido",
                "empty_message": "Nenhum item resolvido ainda.",
            },
        ],
    }


def _build_list_context(
    *,
    create_form: InboxItemForm,
    filter_data=None,
    bound_forms: dict[int, InboxItemTriageForm] | None = None,
):
    filter_form = InboxItemFilterForm(filter_data or None)
    all_items = InboxItem.objects.all()
    total_items = all_items.count()
    filtered_items = _apply_filters(all_items, filter_form)
    dashboard_context = _build_dashboard_context(all_items)

    return {
        "create_form": create_form,
        "filter_form": filter_form,
        "item_cards": _build_triage_forms(filtered_items, bound_forms=bound_forms),
        "total_items": total_items,
        "filtered_count": filtered_items.count(),
        "has_active_filters": _has_active_filters(filter_form),
        "active_query": filter_form.data.urlencode() if filter_form.is_bound else "",
        **dashboard_context,
    }


def _redirect_to_item_list(next_query: str):
    if next_query:
        return redirect(f"{reverse('inbox:item_list')}?{next_query}")
    return redirect("inbox:item_list")


def _querydict_from_string(query_string: str):
    return QueryDict(query_string) if query_string else None


@require_GET
def inbox_item_list_create(request):
    return render(
        request,
        "inbox/item_list.html",
        _build_list_context(create_form=InboxItemForm(), filter_data=request.GET),
    )


@require_POST
def inbox_item_create(request):
    form = InboxItemForm(request.POST)
    next_query = request.POST.get("next_query", "").strip()

    if form.is_valid():
        form.save()
        messages.success(request, "Inbox item criado com sucesso.")
        return _redirect_to_item_list(next_query)

    return render(
        request,
        "inbox/item_list.html",
        _build_list_context(
            create_form=form,
            filter_data=_querydict_from_string(next_query),
        ),
        status=400,
    )


@require_POST
def inbox_item_triage_update(request, pk: int):
    item = get_object_or_404(InboxItem, pk=pk)
    next_query = request.POST.get("next_query", "").strip()
    form = InboxItemTriageForm(request.POST, instance=item, prefix=f"triage-{item.pk}")

    if form.is_valid():
        form.save()
        messages.success(request, f"Triagem do item #{item.pk} atualizada.")
        return _redirect_to_item_list(next_query)

    messages.error(request, f"Nao foi possivel atualizar a triagem do item #{item.pk}.")
    return render(
        request,
        "inbox/item_list.html",
        _build_list_context(
            create_form=InboxItemForm(),
            filter_data=_querydict_from_string(next_query),
            bound_forms={item.pk: form},
        ),
        status=400,
    )


@require_POST
def inbox_item_generate_suggestions(request, pk: int):
    item = get_object_or_404(InboxItem, pk=pk)
    next_query = request.POST.get("next_query", "").strip()
    suggestions = InboxSuggestionService().suggest(item)

    item.sugestao_categoria = suggestions.categoria
    item.sugestao_urgencia = suggestions.urgencia
    item.sugestao_proxima_acao = suggestions.proxima_acao
    item.sugestao_resposta = suggestions.resposta_inicial
    item.save(
        update_fields=[
            "sugestao_categoria",
            "sugestao_urgencia",
            "sugestao_proxima_acao",
            "sugestao_resposta",
            "updated_at",
        ]
    )

    messages.success(request, f"Sugestoes geradas para o item #{item.pk}.")
    return _redirect_to_item_list(next_query)


@require_POST
def inbox_item_apply_suggestions(request, pk: int):
    item = get_object_or_404(InboxItem, pk=pk)
    next_query = request.POST.get("next_query", "").strip()

    if not item.sugestao_categoria and not item.sugestao_urgencia:
        messages.error(
            request,
            f"Nao ha sugestoes aplicaveis para o item #{item.pk}. Gere as sugestoes antes de aplicar.",
        )
        return _redirect_to_item_list(next_query)

    updated_fields = ["updated_at"]
    if item.sugestao_categoria:
        item.categoria = item.sugestao_categoria
        updated_fields.append("categoria")
    if item.sugestao_urgencia:
        item.urgencia = item.sugestao_urgencia
        updated_fields.append("urgencia")
    if item.status == InboxItem.Status.NOVO:
        item.status = InboxItem.Status.TRIADO
        updated_fields.append("status")

    item.save(update_fields=updated_fields)
    messages.success(
        request,
        f"Sugestoes aplicadas na triagem do item #{item.pk}.",
    )
    return _redirect_to_item_list(next_query)
