from .models import SupportThread


def support_chat_context(request):
    """
    Глобальный контекст для чата поддержки.

    Для залогиненного пользователя подставляет:
    - global_support_thread: последний его тред (по updated_at)
    - global_support_messages: сообщения этого треда

    В account_dashboard мы всё равно можем переопределять current_thread,
    но виджет на всех страницах всегда будет иметь хоть какой-то тред.
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}

    thread = (
        SupportThread.objects.filter(user=user)
        .order_by("-updated_at")
        .first()
    )
    if not thread:
        return {
            "global_support_thread": None,
            "global_support_messages": None,
        }

    messages_qs = thread.messages.select_related("author").order_by("created_at")

    return {
        "global_support_thread": thread,
        "global_support_messages": messages_qs,
    }
