from django.db import models
from django.utils import timezone

class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100)
    balance = models.IntegerField(default=0)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)


    def __str__(self):
        return self.name


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("Xarajat", "Xarajat"),
        ("Qarz", "Qarz"),
        ("Balance", "Balance"),
        ("oldim", "oldim"),
        ("berdim", "berdim"),
        ("Qarzim qaytdi", "Qarzim qaytdi"),
        ("Qarz qaytardim", "Qarz qaytardim"),

    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    date = models.DateTimeField(default=timezone.now)
    amount = models.IntegerField(default=0)
    borrower_name = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)




    def __str__(self):
        return f"{self.user.name} - {self.text} so'm ({self.category})"

class QarzBerdim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    person_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    date_text = models.CharField(max_length=100, blank=True, null=True)  # Sana matni
    is_deleted = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.person_name} - {self.amount}"

    class Meta:
        verbose_name = "Qarz Berdim"
        verbose_name_plural = "Qarz Berdimlar"


class QarzOldim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    person_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateTimeField(default=timezone.now)
    date_text = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.person_name} ({self.amount})"

    class Meta:
        verbose_name = "Qarz Oldim"
        verbose_name_plural = "Qarz Oldimlar"

