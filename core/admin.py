from django.contrib import admin
from django.urls import path, reverse
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from .models import (
    Product,
    Instruction,
    News,
    Page,
    Slide,
    SupportThread,
    SupportMessage,
)


# ==============================
#  Product / Instruction / News / Page / Slide
# ==============================

class InstructionInline(admin.TabularInline):
    model = Instruction
    extra = 1
    fields = ("title", "pdf_file", "is_active")
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "model_code", "is_featured", "is_active", "created_at")
    list_filter = ("is_featured", "is_active", "created_at")
    list_editable = ("is_featured", "is_active")
    search_fields = (
        "name",
        "slug",
        "model_code",
        "compatible_models",
        "seo_title",
        "seo_description",
    )
    prepopulated_fields = {"slug": ("name",)}
    inlines = [InstructionInline]
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Basic info", {
            "fields": (
                "name",
                "slug",
                "model_code",
                "compatible_models",
                "short_description",
                "description",
                "image",
            )
        }),
        ("Amazon", {
            "fields": ("amazon_url",),
            "description": "Full URL to this product on Amazon (used by the Buy button).",
        }),
        ("Flags", {
            "fields": ("is_featured", "is_active"),
        }),
        ("SEO", {
            "fields": ("seo_title", "seo_description"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )


@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    list_display = ("title", "product", "is_active", "created_at")
    list_filter = ("is_active", "product")
    search_fields = (
        "title",
        "slug",
        "content",
        "product__name",
        "seo_title",
        "seo_description",
    )
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Basic info", {
            "fields": ("product", "title", "slug", "content", "pdf_file", "is_active")
        }),
        ("SEO", {
            "fields": ("seo_title", "seo_description"),
        }),
        ("Timestamps", {
            "fields": ("created_at",),
        }),
    )


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "published_at", "is_published")
    list_filter = ("is_published", "published_at")
    list_editable = ("is_published",)
    search_fields = (
        "title",
        "slug",
        "excerpt",
        "content",
        "seo_title",
        "seo_description",
    )
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    fieldsets = (
        ("Basic info", {
            "fields": ("title", "slug", "excerpt", "content", "published_at", "is_published")
        }),
        ("SEO", {
            "fields": ("seo_title", "seo_description"),
        }),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "key", "slug", "is_active")
    list_editable = ("is_active",)
    list_filter = ("key", "is_active")
    search_fields = ("title", "slug", "content", "seo_title", "seo_description")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Basic info", {
            "fields": ("key", "title", "slug", "content", "image", "is_active")
        }),
        ("SEO", {
            "fields": ("seo_title", "seo_description"),
        }),
    )


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active", "product", "news")
    list_editable = ("order", "is_active")
    list_filter = ("is_active", "product", "news")
    search_fields = ("title", "subtitle", "product__name", "news__title")
    fieldsets = (
        ("Basic info", {
            "fields": ("title", "subtitle", "badge_text", "bullet_1", "bullet_2", "bullet_3", "image")
        }),
        ("Links", {
            "fields": ("product", "news", "button_text", "button_url")
        }),
        ("Display", {
            "fields": ("is_active", "order"),
        }),
    )


# ==============================
#  Support chat admin (Inbox)
# ==============================

class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    fields = ("created_at", "author", "is_staff_reply", "text")
    readonly_fields = ("created_at",)
    ordering = ("created_at",)


@admin.register(SupportThread)
class SupportThreadAdmin(admin.ModelAdmin):
    """
    Вспомогательный admin для поиска/фильтрации.
    Основная работа идёт через кастомный Inbox.
    """
    list_display = ("id", "user", "subject", "status", "updated_at", "last_message_short")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "subject")
    readonly_fields = ("created_at", "updated_at")

    def last_message_short(self, obj):
        msg = obj.last_message
        if not msg:
            return "-"
        prefix = "Admin: " if msg.is_staff_reply else "User: "
        return prefix + (msg.text[:40] + ("…" if len(msg.text) > 40 else ""))
    last_message_short.short_description = "Last message"


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    """
    Скрываем реальный список сообщений, а пункт меню используем
    как ссылку на Inbox.
    """
    def has_view_permission(self, request, obj=None):
        # показываем пункт меню
        return request.user.is_staff

    def changelist_view(self, request, extra_context=None):
        # редиректим сразу в наш Inbox
        return HttpResponseRedirect(reverse("admin:support_inbox"))


# ------------------------------
#  Custom admin inbox view
# ------------------------------

def support_inbox_view(request, thread_id=None):
    """
    Кастомный admin-интерфейс для чатов:
    слева список тредов, справа переписка с выбранным пользователем.
    """
    threads = (
        SupportThread.objects.select_related("user")
        .order_by("-updated_at")
    )

    # выбор текущего треда
    current_thread = None
    if thread_id is not None:
        try:
            current_thread = threads.get(id=thread_id)
        except SupportThread.DoesNotExist:
            current_thread = None

    if current_thread is None:
        current_thread = threads.first()

    # обработка ответа админа
    if request.method == "POST" and current_thread is not None:
        text = request.POST.get("text", "").strip()
        if text:
            SupportMessage.objects.create(
                thread=current_thread,
                author=request.user if request.user.is_authenticated else None,
                is_staff_reply=True,
                text=text,
            )
            current_thread.save()  # обновит updated_at
        url = reverse("admin:support_inbox_thread", args=[current_thread.id])
        return redirect(url)

    messages_qs = None
    if current_thread is not None:
        messages_qs = current_thread.messages.select_related("author")

    context = {
        **admin.site.each_context(request),
        "title": "Support chats",
        "threads": threads,
        "current_thread": current_thread,
        "messages": messages_qs,
    }
    return TemplateResponse(request, "admin/support_inbox.html", context)


# Подключаем кастомный URL в admin namespace корректным способом
def support_admin_urls():
    urlpatterns = [
        path(
            "support/inbox/",
            admin.site.admin_view(support_inbox_view),
            name="support_inbox",
        ),
        path(
            "support/inbox/<int:thread_id>/",
            admin.site.admin_view(support_inbox_view),
            name="support_inbox_thread",
        ),
    ]
    return urlpatterns


# Оборачиваем существующий get_urls, добавляя наши
original_get_urls = admin.site.get_urls


def get_urls():
    return support_admin_urls() + original_get_urls()


admin.site.get_urls = get_urls
