import json
import pytz
from django.http import  HttpResponse
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User, Expense
from .forms import QarzForm, QarzOldimForm
from .serializers import ExpenseSerializer
from django.shortcuts import render
from datetime import date, datetime, timedelta
from collections import defaultdict
from django.utils.timezone import localtime
from django.http import JsonResponse
from django import forms
from django.shortcuts import get_object_or_404, redirect
from .utils import generate_pdf
from django.http import FileResponse
from .models import QarzBerdim, QarzOldim
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.utils import timezone


@api_view(['POST'])
def add_expense(request):
    data = json.loads(request.body)

    tg_id = data.get("telegram_id")
    name = data.get("name", "Foydalanuvchi")
    text = data.get("text")
    category = data.get("category", "Xarajat")
    borrower_name = data.get("borrower_name", None)


    user, _ = User.objects.get_or_create(telegram_id=tg_id, defaults={"name": name})

    try:
        amount = int(text)
    except ValueError:
        return JsonResponse({"status": "error", "message": "Xato son"}, status=400)

    # 👇 Mahalliy vaqtga o‘tkazamiz
    now = localtime()
    today = now.date()

    if category == "Balance":
        old_expense = Expense.objects.filter(
            user=user, category="Balance", date__date=today
        ).first()

        if old_expense:
            old_expense.amount += amount
            old_expense.text = str(old_expense.amount)
            old_expense.date = now
            old_expense.save()
        else:
            Expense.objects.create(user=user, text=str(amount), amount=amount, category="Balance", date=timezone.now())
    else:
        Expense.objects.create(user=user, text=str(amount), amount=amount, category=category, date=timezone.now())

    return JsonResponse({"status": "success"})





@api_view(['POST'])
def check_existing_expense(request):
    data = request.data
    telegram_id = data.get("telegram_id")
    category = data.get("category", "Xarajat")
    today = date.today()

    try:
        user = User.objects.get(telegram_id=telegram_id)
        expenses = Expense.objects.filter(user=user, category=category, date__date=today)
        if expenses.exists():
            total = sum(int(e.text) for e in expenses)
            return Response({
                "exists": True,
                "text": total
            })
        else:
            return Response({"exists": False})
    except User.DoesNotExist:
        return Response({"exists": False})


@api_view(['PUT'])
def update_expense(request):
    data = json.loads(request.body)

    tg_id = data.get("telegram_id")
    category = data.get("category")
    text = data.get("text")

    try:
        amount = int(text)
    except ValueError:
        return JsonResponse({"status": "error", "message": "Noto‘g‘ri qiymat"}, status=400)

    user = User.objects.filter(telegram_id=tg_id).first()
    if not user:
        return JsonResponse({"status": "error", "message": "Foydalanuvchi topilmadi"}, status=404)

    if category == "Balance":
        today = timezone.now().date()
        expense = Expense.objects.filter(user=user, category="Balance", date__date=today).first()

        if expense:
            expense.amount += amount
            expense.text = str(expense.amount)
            expense.save()
        else:
            Expense.objects.create(user=user, category="Balance", amount=amount, text=str(amount), date=timezone.now())
    else:
        Expense.objects.create(user=user, category=category, amount=amount, text=str(amount), date=timezone.now())

    return JsonResponse({"status": "updated"})
@api_view(['GET'])
def get_today_expenses(request, tg_id):
    today = date.today()
    user = User.objects.get(telegram_id=tg_id)
    expenses = Expense.objects.filter(user=user, date=today)
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data)

def parse_int(text):
    import re
    try:
        return int(re.sub(r"[^\d]", "", text))
    except:
        return 0

def statistika(request, telegram_id):
    global balance, balance_sum, qarz_berganlar, qarz_olganlar, real_balance
    try:
        user = User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return render(request, "qarzlar.html", {"kunlik_malumotlar": []})

    expenses = Expense.objects.filter(user=user)


    kunlar = defaultdict(list)
    for e in expenses:
        sana = localtime(e.date).date()
        kunlar[sana].append(e)

    tartiblangan = []
    for sana, es in sorted(kunlar.items(), key=lambda x: x[0], reverse=False):
        xarajatlar = [e for e in es if e.category == "Xarajat"]
        qarzlar = [e for e in es if e.category == "Qarz"]
        balans = sum(parse_int(e.text) for e in es if e.category in ["Balance"])
        jami = sum(parse_int(e.text) for e in es if e.category in ["Xarajat", "Qarz"])
        balanslar = balans - jami
        tartiblangan.append({
            "sana": sana,
            "xarajatlar": xarajatlar,
            "qarzlar": qarzlar,
            "jami": jami,
            "balance": balanslar
        })


        qarz_berganlar = QarzBerdim.objects.filter(user=user, is_deleted=False).order_by('-date')
        qarz_olganlar = QarzOldim.objects.filter(user=user, is_deleted=False).order_by('-id')

        balance_expenses = Expense.objects.filter(user=user, category="Balance")
        xarajatlar = Expense.objects.filter(user=user).exclude(category="Balance")


        balance_sum = sum(e.amount for e in balance_expenses)
        expenses_sum = sum(e.amount for e in xarajatlar)
        qarz_olgan_sum = sum(q.amount for q in qarz_olganlar)
        qarz_bergan_sum = sum(q.amount for q in qarz_berganlar)

        real_balance = balance_sum + qarz_olgan_sum - qarz_bergan_sum - expenses_sum

    return render(request, "qarzlar.html", {
        "kunlik_malumotlar": tartiblangan,
        "telegram_id": telegram_id,
        "balance": real_balance if real_balance > 0 else 0,
        "qarz_berganlar": qarz_berganlar,
        "qarz_olganlar": qarz_olganlar,

    })

def grafikli_statistika(request, telegram_id):
    user = User.objects.get(telegram_id=telegram_id)


    return render(request, "grafik.html", {
        "telegram_id": telegram_id,
    })

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['text', 'category']


def balance_view(request, telegram_id):
    user = get_object_or_404(User, telegram_id=telegram_id)

    balance_expenses = Expense.objects.filter(user=user, category="Balance").order_by('-date')

    balance_sum =sum(e.amount for e in balance_expenses)

    context = {
        'user': user,
        'balance':balance_sum if balance_sum else 0,
        'telegram_id': telegram_id,
    }
    return render(request, 'balance.html', context)



@api_view(['POST'])
def register_user(request):
    data = request.data
    telegram_id = data.get('telegram_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if not telegram_id or not first_name or not last_name:
        return Response({'error': 'Barcha maydonlar to‘ldirilishi kerak.'}, status=400)

    user, created = User.objects.update_or_create(
        telegram_id=telegram_id,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
        }
    )

    return Response({'status': 'success', 'created': created})

def profile_view(request, telegram_id):
    user = User.objects.get(telegram_id=telegram_id)
    return render(request, 'profil.html',{
        'user': user,
        'telegram_id': telegram_id,
    })

def edit_user(request, telegram_id):
    user = get_object_or_404(User, telegram_id=telegram_id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        return redirect('edit_user', telegram_id=telegram_id)

    return render(request, 'edit_user.html', {
        'user': user,
        'telegram_id': telegram_id,
    })


def weekly_expense_pdf(request, telegram_id):
    user = get_object_or_404(User, telegram_id=telegram_id)
    today = datetime.today().date()
    start_date = today - timedelta(days=6)

    expenses = Expense.objects.filter(
        user=user,
        date__date__range=[start_date, today]
    ).order_by("date")

    xarajatlar = expenses.filter(category="Xarajat")
    qarz_berdim = QarzBerdim.objects.filter(user=user, is_deleted=False).order_by('-date')
    qarz_oldim = QarzOldim.objects.filter(user=user, is_deleted=False).order_by('-id')
    jami_xarajat = expenses.aggregate(Sum("amount"))["amount__sum"] or 0
    jami_oldim = qarz_oldim.aggregate(Sum("amount"))["amount__sum"] or 0
    jami_berdim = qarz_berdim.aggregate(Sum("amount"))["amount__sum"] or 0
    context = {
        "user": user,
        "start_date": start_date,
        "end_date": today,
        "xarajatlar": xarajatlar,
        "qarz_oldim": qarz_oldim,
        "qarz_berdim": qarz_berdim,
        "jami_xarajat": jami_xarajat,
        "jami_oldim": jami_oldim,
        "jami_berdim": jami_berdim,
    }

    pdf_buffer = generate_pdf("weekly_expense_pdf.html", context)
    if pdf_buffer:
        return FileResponse(pdf_buffer, as_attachment=True, filename="haftalik_hisobot.pdf")
    else:
        return HttpResponse("❌ PDF yaratishda xatolik yuz berdi.", status=500)

def daily_report(request, telegram_id):
    user = User.objects.get(telegram_id=telegram_id)
    today = date.today()
    uzbekistan = pytz.timezone("Asia/Tashkent")

    expenses = Expense.objects.filter(user=user, date__date=today).order_by('date')

    qarz_olganlar = QarzOldim.objects.filter(user=user, date__date=today).order_by('date')

    qarz_berganlar = QarzBerdim.objects.filter(user=user, date__date=today).order_by('date')

    report = f"📊 <b>{today.strftime('%d-%m-%Y')}</b> kunlik hisobot:\n\n"

    if expenses.exists():
        report += "💸 <b>Xarajatlar:</b>\n"
        for i, exp in enumerate(expenses, 1):
            t = localtime(exp.date, uzbekistan).strftime('%H:%M')
            report += f"{i}. 📁 {exp.category} — {exp.text } {exp.amount} so'm ({t})\n"
        jami_xarajat = expenses.aggregate(Sum("amount"))["amount__sum"] or 0
        report += f"\n🔻 Jami: {jami_xarajat} so‘m\n\n"
    else:
        report += "💸 Xarajatlar yo‘q.\n\n"

    if qarz_olganlar.exists():
        report += "📥 <b>Qarz oldim:</b>\n"
        for i, q in enumerate(qarz_olganlar, 1):
            t = localtime(q.date, uzbekistan).strftime('%H:%M')
            report += f"{i}. {q.person_name} — {q.amount} so‘m ({t})\n"
        jami_oldim = qarz_olganlar.aggregate(Sum("amount"))["amount__sum"] or 0
        report += f"\n🔻 Jami qarz olingan: {jami_oldim} so‘m\n\n"
    else:
        report += "📥 Qarz olinganlar yo‘q.\n\n"

    if qarz_berganlar.exists():
        report += "📤 <b>Qarz berdim:</b>\n"
        for i, q in enumerate(qarz_berganlar, 1):
            t = localtime(q.date, uzbekistan).strftime('%H:%M')
            report += f"{i}. {q.person_name} — {q.amount} so‘m ({t})\n"
        jami_berdim = qarz_berganlar.aggregate(Sum("amount"))["amount__sum"] or 0
        report += f"\n🔺 Jami qarz berilgan: {jami_berdim} so‘m\n\n"
    else:
        report += "📤 Qarz berilganlar yo‘q.\n\n"

    balance = user.balance if hasattr(user, "balance") else "❔ Belgilanmagan"
    report += f"💰 <b>Balance:</b> {balance} so‘m\n"

    return JsonResponse({"message": report})

def check_user(request, telegram_id):
    exists = User.objects.filter(telegram_id=telegram_id).exists()
    return JsonResponse({"exists": exists})

@csrf_exempt
def add_qarz(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        telegram_id = data.get("telegram_id")
        person_name = data.get("person_name")
        category = data.get("category")
        amount_str = data.get("amount")
        date_text = data.get("date_text")

        if not all([telegram_id, person_name, category, amount_str]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            amount = float(amount_str)
        except ValueError:
            return JsonResponse({"error": "Invalid amount"}, status=400)

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        if category == "berdim":
            QarzBerdim.objects.create(
                user=user,
                person_name=person_name,
                amount=amount,
                date_text=date_text
            )
        elif category == "oldim":
            QarzOldim.objects.create(
                user=user,
                person_name=person_name,
                amount=amount,
                date_text=date_text
            )
        else:
            return JsonResponse({"error": "Invalid category"}, status=400)

        return JsonResponse({"status": "success"})

    return JsonResponse({"error": "Invalid HTTP method"}, status=405)


@api_view(["GET"])
def qarz_names(request, telegram_id):
    try:
        user = User.objects.get(telegram_id=telegram_id)
        ismlar = QarzBerdim.objects.filter(user=user).values_list("person_name", flat=True).distinct()
        return Response({"names": list(ismlar)})
    except User.DoesNotExist:
        return Response({"names": []})

@api_view(["GET"])
def qarz_olganlar(request, telegram_id):
    try:
        user = User.objects.get(telegram_id=telegram_id)
        ismlar = QarzOldim.objects.filter(user=user).values_list("person_name", flat=True).distinct()
        return Response({"names": list(ismlar)})
    except User.DoesNotExist:
        return Response({"names": []})


def edit_qarz(request, qarz_id):
    qarz = get_object_or_404(QarzBerdim, id=qarz_id)
    form = QarzForm(request.POST or None, instance=qarz)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('statistika', telegram_id=qarz.user.telegram_id)

    return render(request, 'edit_expense.html', {
        'form': form,
        'telegram_id': qarz.user.telegram_id,
    })


@require_POST
def delete_qarz(request, qarz_id):
    qarz = get_object_or_404(QarzBerdim, id=qarz_id)
    telegram_id = qarz.user.telegram_id
    qarz.is_deleted = True
    qarz.save()
    return redirect('qarzlar', telegram_id=telegram_id)

def edit_qarz_oldim(request, qarz_id):
    qarz = get_object_or_404(QarzOldim, id=qarz_id)
    telegram_id = qarz.user.telegram_id
    form = QarzOldimForm(request.POST or None, instance=qarz)

    if form.is_valid():
        form.save()
        return redirect('qarzlar', telegram_id=telegram_id)

    return render(request, "edit_qarz_oldim.html", {
        "form": form,
        "telegram_id": telegram_id
    })

@require_POST
def delete_qarz_oldim(request, qarz_id):
    qarz = get_object_or_404(QarzOldim, id=qarz_id)
    telegram_id = qarz.user.telegram_id
    qarz.is_deleted = True
    qarz.save()
    return redirect('qarzlar', telegram_id=telegram_id)

def keyingi_sahifa(request, telegram_id):
    user = User.objects.get(telegram_id=telegram_id)
    return render(request, 'base.html',{
        "telegram_id": telegram_id,
    })
@csrf_exempt
def add_xarajat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            telegram_id = data.get("telegram_id")
            text = data.get("text")  # Masalan: "Nonushta", "Avtobus"
            amount = data.get("amount")

            user = User.objects.get(telegram_id=telegram_id)

            Expense.objects.create(
                user=user,
                text=text,
                category="Xarajat",
                amount=amount,
                date=timezone.now()
            )

            return JsonResponse({"message": "✅ Xarajat muvaffaqiyatli saqlandi."})

        except User.DoesNotExist:
            return JsonResponse({"error": "Foydalanuvchi topilmadi."}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Faqat POST so'rovi qabul qilinadi."}, status=400)

def daily_expense_report(request, telegram_id):
    user = User.objects.get(telegram_id=telegram_id)
    expenses = Expense.objects.filter(user=user, category="Xarajat" ).order_by('date')

    grouped = defaultdict(list)
    for exp in expenses:
        date_key = localtime(exp.date).date()
        grouped[date_key].append(exp)

    qarz_berganlar = QarzBerdim.objects.filter(user=user, is_deleted=False).order_by('-date')
    qarz_olganlar = QarzOldim.objects.filter(user=user, is_deleted=False).order_by('-id')

    balance_expenses = Expense.objects.filter(user=user, category="Balance")
    xarajatlar = Expense.objects.filter(user=user).exclude(category="Balance")

    balance_sum = sum(e.amount for e in balance_expenses)
    expenses_sum = sum(e.amount for e in xarajatlar)
    qarz_olgan_sum = sum(q.amount for q in qarz_olganlar)
    qarz_bergan_sum = sum(q.amount for q in qarz_berganlar)

    real_balance = balance_sum + qarz_olgan_sum - qarz_bergan_sum - expenses_sum

    return render(request, "harajatlar.html", {
        "grouped_expenses": sorted(grouped.items()),
        "telegram_id": telegram_id,
        "balance": real_balance if real_balance > 0 else 0,
    })


@api_view(["GET"])
def get_balance(request, telegram_id):
    user = get_object_or_404(User, telegram_id=telegram_id)
    total_balance = Expense.objects.filter(user=user, category="Balance").aggregate(total=Sum("amount"))["total"] or 0
    return JsonResponse({"balance": total_balance})



def qarzlar_list(request, user_id, tur):
    try:
        user = User.objects.get(telegram_id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    if tur == "berdim":
        queryset = QarzBerdim.objects.filter(user=user, is_deleted=False)
    elif tur == "oldim":
        queryset = QarzOldim.objects.filter(user=user, is_deleted=False)
    else:
        return JsonResponse({"error": "Noto‘g‘ri tur"}, status=400)

    data = [
        {"id": q.id, "person_name": q.person_name, "amount": float(q.amount)}
        for q in queryset
    ]
    return JsonResponse(data, safe=False)


@csrf_exempt
def delete_qarz_api(request, qarz_id):
    try:
        # Ikkala modelni tekshirib chiqamiz
        try:
            obj = QarzBerdim.objects.get(id=qarz_id)
        except QarzBerdim.DoesNotExist:
            obj = QarzOldim.objects.get(id=qarz_id)

        obj.is_deleted = True
        obj.save()
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


