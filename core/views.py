from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import SignUpForm
from .models import (
    Product,
    Instruction,
    News,
    Page,
    Slide,
    SupportThread,
    SupportMessage,
)


def home(request):
    slides = Slide.objects.filter(is_active=True).order_by("order", "-created_at")
    latest_news = News.objects.filter(is_published=True).order_by("-published_at")[:3]
    return render(
        request,
        "home.html",
        {
            "slides": slides,
            "latest_news": latest_news,
        },
    )


def product_list(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(model_code__icontains=query)
            | Q(compatible_models__icontains=query)
        )

    products = products.order_by("name")

    return render(
        request,
        "product_list.html",
        {
            "products": products,
            "query": query,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    compatible_models_list = []
    if product.compatible_models:
        compatible_models_list = [
            m.strip() for m in product.compatible_models.split(",") if m.strip()
        ]

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "compatible_models_list": compatible_models_list,
        },
    )


def page_by_key(key, default_slug=None):
    """
    Вспомогательная функция: сначала пробуем найти Page по key,
    если нет — по slug, если и этого нет — вернём None.
    """
    page = Page.objects.filter(key=key, is_active=True).first()
    if not page and default_slug:
        page = Page.objects.filter(slug=default_slug, is_active=True).first()
    return page


def production(request):
    page = page_by_key("production", default_slug="production")
    photos = []
    return render(
        request,
        "page_production.html",
        {
            "page": page,
            "photos": photos,
        },
    )


def contacts(request):
    page = page_by_key("contacts", default_slug="contacts")
    return render(
        request,
        "page_contacts.html",
        {
            "page": page,
        },
    )


def instructions_page(request):
    """
    Страница со списком инструкций + фильтр по продукту.
    """
    page = page_by_key("instructions", default_slug="instructions")
    products = Product.objects.filter(is_active=True).order_by("name")

    selected_product_id = request.GET.get("product", "")
    instructions = Instruction.objects.filter(is_active=True).select_related("product")

    if selected_product_id:
        instructions = instructions.filter(product_id=selected_product_id)

    instructions = instructions.order_by("product__name", "title")

    return render(
        request,
        "page_instructions.html",
        {
            "page": page,
            "products": products,
            "instructions": instructions,
            "selected_product_id": selected_product_id,
        },
    )


def news_list(request):
    news_list = News.objects.filter(is_published=True).order_by("-published_at")
    return render(
        request,
        "news_list.html",
        {
            "news_list": news_list,
        },
    )


def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug, is_published=True)
    return render(
        request,
        "news_detail.html",
        {
            "news": news,
        },
    )


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect("account_dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created.")
            return redirect("account_dashboard")
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})


@login_required
def account_dashboard(request):
    threads = SupportThread.objects.filter(user=request.user).order_by("-updated_at")

    thread_id = request.GET.get("thread")
    current_thread = None

    if thread_id:
        try:
            current_thread = threads.get(id=thread_id)
        except SupportThread.DoesNotExist:
            current_thread = None

    if not current_thread:
        current_thread = threads.first()

    current_messages = None
    if current_thread:
        current_messages = current_thread.messages.select_related("author")

    context = {
        "profile_user": request.user,
        "threads": threads,
        "current_thread": current_thread,
        "current_messages": current_messages,
    }
    return render(request, "account/dashboard.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def support_new_thread(request):
    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        text = request.POST.get("text", "").strip()
        if subject and text:
            thread = SupportThread.objects.create(
                user=request.user,
                subject=subject,
                status="open",
            )
            SupportMessage.objects.create(
                thread=thread,
                author=request.user,
                is_staff_reply=False,
                text=text,
            )
            return redirect("account_dashboard")  # сразу в кабинет
    return render(request, "support/new_thread.html", {})


@login_required
@require_http_methods(["GET", "POST"])
def support_thread_detail(request, thread_id):
    thread = get_object_or_404(SupportThread, id=thread_id)

    if thread.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        if text and thread.status == "open":
            SupportMessage.objects.create(
                thread=thread,
                author=request.user,
                is_staff_reply=request.user.is_staff,
                text=text,
            )
            thread.save()  # обновит updated_at
        # после отправки возвращаемся в кабинет на этот тред
        url = f"{reverse('account_dashboard')}?thread={thread.id}"
        return redirect(url)

    messages_qs = thread.messages.select_related("author")

    return render(
        request,
        "support/thread_detail.html",
        {
            "thread": thread,
            "messages": messages_qs,
        },
    )


@login_required
def support_thread_messages_json(request, thread_id):
    thread = get_object_or_404(SupportThread, id=thread_id)

    if thread.user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    messages_qs = thread.messages.select_related("author").order_by("created_at")
    data = [
        {
            "id": m.id,
            "author": "support" if m.is_staff_reply else "user",
            "text": m.text,
            "created_at": m.created_at.isoformat(timespec="seconds"),
        }
        for m in messages_qs
    ]
    return JsonResponse({"messages": data})
