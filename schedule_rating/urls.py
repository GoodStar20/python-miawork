from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:pk>/', views.CreateHeaderView, name= 'schedule-rating-create'),
    path('header/<int:pk>/', views.EditHeaderView, name= 'edit-header-view'),
    path('select-states/<int:pk>/', views.SelectStatesView, name= 'select-states-view'),
    path('states/<int:pk>/', views.StatesListView, name = 'states-list-view'),
    path('state-lines/<int:pk>/<str:state>/', views.StateView, name= 'work-comp-lines-view'),
    path('export/<int:pk>/', views.ExportView, name='exportsr'),
    path('delete/<int:pk>/', views.SRHeaderDelete.as_view(), name='delete-view'),
    path('success/<int:pk>/', views.success, name='sr-export-success'),
    path('download/<int:pk>/', views.download, name='schedule-rating-download'),
    path('upload/', views.upload_file, name = 'uploadsr'),
    path('list/', views.FormListView.as_view(), name= 'schedule-rating-list'),
    path('list-from-risk-eval/<int:pk>/', views.ListViewByRiskEval.as_view(), name= 'schedule-rating-list-by-risk-eval'),
    path('', views.schedule_rating_redirect, name = 'schedule-rating-redirect')
]