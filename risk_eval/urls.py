from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('risk_eval', views.RestView)

urlpatterns = [
    path('list/', views.FormListView.as_view(), name = 'listview'),
    path('renew/<int:pk>/', views.RenewRiskEval, name = 'renew'),
    path('create/', views.CreateRiskEval, name = 'create'),
    path('delete/<int:pk>/', views.DeleteRiskEval.as_view(), name = 'delete-risk-eval'),
    path('edit/SectionA/<int:pk>/', views.EditGeneralInfo, name = 'EditSectionA'),
    path('edit/SectionB/<int:pk>/', views.AccountHistoryView, name = 'EditSectionB'),
    path('edit/Exmod/<int:pk>/', views.EditExmodView, name = 'EditExmod'),
    path('edit/SectionC/<int:pk>/', views.EditRisk, name = 'EditSectionC'),
    path('edit/SectionD/<int:pk>/', views.EditChecklist, name = 'EditSectionD'),
    path('edit/SectionF/<int:pk>/', views.EditComments, name = 'EditSectionF'),
    path('edit/SectionG/<int:pk>/', views.EditClaimDetails, name = 'EditSectionG'),
    path('edit/SectionH/<int:pk>/', views.EditNotes, name = 'EditSectionH'),
    path('edit/LoggingNotes/<int:pk>/', views.EditLoggingNotes, name = 'LoggingNotes'),
    path('edit/MechanicalNotes/<int:pk>/', views.EditMechanicalNotes, name = 'MechanicalNotes'),
    path('edit/WoodManualNotes/<int:pk>/', views.EditWoodManualNotes, name = 'WoodManualNotes'),
    path('edit/Score/<int:pk>/', views.EditScore, name = 'Score'),
    path('review/<int:pk>/', views.ReviewRiskEval, name = 'ReviewRiskEval'),
    path('export/<int:pk>/', views.export_view, name='export'),
    path('success/<int:pk>/', views.success, name='success'),
    path('download/<int:pk>/', views.download, name='risk-eval-download'),
    path('upload/', views.upload_file, name = 'upload'),
    path('override_file_data/<int:id>/', views.override_file_data, name = 'override_file_data'),
    path('create_new/',views.create_new, name='create_new'),
    path('api/', include(router.urls), name='api'), ## test is the url
]