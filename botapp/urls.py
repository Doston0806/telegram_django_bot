from django.urls import path
from . import views
from .views import check_existing_expense

urlpatterns = [
    path('add_expense/', views.add_expense),
    path('today_expenses/<int:telegram_id>/', views.get_today_expenses),
    path('statistika/<int:telegram_id>/', views.keyingi_sahifa , name='statistika'),
    path('check_expense/', check_existing_expense),
    path('grafik/<int:telegram_id>/', views.grafikli_statistika, name='grafik'),
    # path('edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    # path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('customer/<int:telegram_id>/balance/', views.balance_view, name='balance'),
    path('register_user/', views.register_user, name='profil'),
    path('profil/<int:telegram_id>/', views.profile_view, name='profil'),
    path("weekly-pdf/<int:telegram_id>/", views.weekly_expense_pdf, name="weekly_expense_pdf"),
    path('daily_report/<int:telegram_id>/', views.daily_report, name='daily_report'),
    path("check_user/<int:telegram_id>/", views.check_user),
    path('update_expense/', views.update_expense, name='update_expense'),
    path('edit_user/<int:telegram_id>/', views.edit_user, name='edit_user'),
    path("add_qarz/", views.add_qarz),
    path("qarz_names/<int:telegram_id>/", views.qarz_names),
    path("qarz_olganlar/<int:telegram_id>/", views.qarz_olganlar),
    path('qarz_delete/<int:qarz_id>/', views.delete_qarz, name='delete_qarz'),
    path('edit_qarz/<int:qarz_id>/', views.edit_qarz, name='edit_expense'),
    path('edit_qarz_oldim/<int:qarz_id>/', views.edit_qarz_oldim, name='edit_qarz_oldim'),
    path('delete_qarz_oldim/<int:qarz_id>/', views.delete_qarz_oldim, name='delete_qarz_oldim'),
    path('qarzlar/<int:telegram_id>/', views.statistika, name='qarzlar'),
    path("add_xarajat/", views.add_xarajat, name="add_xarajat"),
    path('harajatlar/<int:telegram_id>/', views.daily_expense_report, name='harajatlar'),
    path("get_balance/<int:telegram_id>/", views.get_balance),
    path('qarzlar_list/<int:user_id>/<str:tur>/', views.qarzlar_list, name='qarzlar_list'),
    path("delete_qarz/<int:qarz_id>/", views.delete_qarz_api, name="delete_qarz_api"),

]

