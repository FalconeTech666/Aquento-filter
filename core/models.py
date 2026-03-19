from django.db import models
from django.conf import settings


class Product(models.Model):
    """
    Основной продукт: фильтр.
    """
    name = models.CharField(max_length=200, help_text="Product name, e.g. Aquento ULTRA01")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL slug, e.g. aquento-ultra01")
    model_code = models.CharField(
        max_length=100,
        blank=True,
        help_text="Internal model code, e.g. AQ-ULTRA01"
    )
    compatible_models = models.TextField(
        blank=True,
        help_text="Comma-separated list of OEM compatible models (ULTRAWF, EPTWFU01, ...)."
    )
    short_description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short tagline shown in lists."
    )
    description = models.TextField(
        blank=True,
        help_text="Full description for the product detail page."
    )
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        help_text="Main product image."
    )
    # ссылка на карточку товара на Amazon
    amazon_url = models.URLField(
        "Amazon product URL",
        blank=True,
        help_text="Full URL to this product on Amazon."
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Show on the homepage as a featured product."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this product from the site."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # SEO
    seo_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom meta title for this product page."
    )
    seo_description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom meta description for this product page."
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Instruction(models.Model):
    """
    Инструкции по установке/эксплуатации, привязанные к продуктам.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="instructions",
        help_text="Product this instruction belongs to."
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField(
        blank=True,
        help_text="Instruction text (HTML or plain text)."
    )
    pdf_file = models.FileField(
        upload_to="instructions/",
        blank=True,
        null=True,
        help_text="Optional PDF file with instructions."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # SEO
    seo_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom meta title for this instruction page."
    )
    seo_description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom meta description for this instruction page."
    )

    class Meta:
        ordering = ["product", "title"]

    def __str__(self):
        return f"{self.product.name} – {self.title}"


class News(models.Model):
    """
    Новости/посты бренда Aquento.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    excerpt = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short summary for list views."
    )
    content = models.TextField()
    published_at = models.DateTimeField()
    is_published = models.BooleanField(default=True)

    # SEO
    seo_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom meta title for this news page."
    )
    seo_description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom meta description for this news page."
    )

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


class Page(models.Model):
    """
    Статические страницы: Production, Contacts, About, etc.
    """
    PAGE_CHOICES = [
        ("home", "Homepage extra content"),
        ("production", "Production"),
        ("contacts", "Contacts"),
        ("instructions", "Instructions landing"),
        ("custom", "Custom page"),
    ]

    key = models.CharField(
        max_length=50,
        choices=PAGE_CHOICES,
        default="custom",
        help_text="Logical key to refer to this page in views/templates."
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="URL slug for this page."
    )
    content = models.TextField(
        blank=True,
        help_text="Main page content (HTML or plain text)."
    )
    image = models.ImageField(
        upload_to="pages/",
        blank=True,
        null=True,
        help_text="Optional header/hero image for the page."
    )
    is_active = models.BooleanField(default=True)

    # SEO
    seo_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom meta title for this page."
    )
    seo_description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Custom meta description for this page."
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Slide(models.Model):
    """
    Слайды/баннеры для главной страницы.
    """
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    badge_text = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional badge text, e.g. NEW / AQ-ULTRA01",
    )
    bullet_1 = models.CharField(   # NEW
        max_length=120,
        blank=True,
        help_text="First bullet point",
    )
    bullet_2 = models.CharField(   # NEW
        max_length=120,
        blank=True,
        help_text="Second bullet point",
    )
    bullet_3 = models.CharField(   # NEW
        max_length=120,
        blank=True,
        help_text="Third bullet point",
    )
    image = models.ImageField(
        upload_to="slides/",
        blank=True,
        null=True,
        help_text="Background image for the slide."
    )
    # Слайд может быть связан с продуктом или новостью, но не обязательно
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="slides",
        help_text="Optional product to link to."
    )
    news = models.ForeignKey(
        News,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="slides",
        help_text="Optional news item to link to."
    )
    button_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Text for the call‑to‑action button."
    )
    button_url = models.URLField(
        blank=True,
        help_text="Absolute or relative URL for the button."
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ordering of slides on the homepage (lower appears first)."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title


class SupportThread(models.Model):
    """
    Чат с пользователем (как диалог в Amazon Seller Central).
    Один пользователь может иметь несколько тредов в истории,
    но только один активный (status='open') используется как основной чат.
    """
    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_threads",
    )
    subject = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        base = self.subject or "Support chat"
        return f"{self.user} – {base} ({self.get_status_display()})"

    @property
    def last_message(self):
        return self.messages.order_by("-created_at").first()

    @classmethod
    def get_or_create_active(cls, user):
        """
        Основной вход: получить активный чат пользователя.
        Если нет – создать новый пустой тред.
        """
        thread = (
            cls.objects.filter(user=user, status="open")
            .order_by("-updated_at")
            .first()
        )
        if thread:
            return thread

        return cls.objects.create(
            user=user,
            subject="Support chat",
            status="open",
        )


class SupportMessage(models.Model):
    """
    Сообщение внутри чата.
    """
    thread = models.ForeignKey(
        SupportThread,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="support_messages",
    )
    is_staff_reply = models.BooleanField(default=False)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        side = "Admin" if self.is_staff_reply else "User"
        return f"[{side}] {self.created_at:%Y-%m-%d %H:%M} – {self.text[:30]}"
