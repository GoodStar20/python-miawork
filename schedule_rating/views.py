from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from risk_eval.models import GeneralInfo
from schedule_rating import forms
from schedule_rating import models 
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
import os
from django.http import FileResponse
from django.core.mail import mail_admins

from excel import ExportSR
from excel import handle_uploaded_file_sr, uploadSR
from .state_form_helpers import workcomp_fieldlist, update_workcomplines, states_names, carrier_info

@login_required
def success(request, pk):
    """
    Export Success View
    """
    instance_export = models.Export.objects.get(pk=pk)
    header = models.SRHeader.objects.get(pk = instance_export.header_id)
    pk_for_sr = header.generalinfo.pk
    context = {'title': 'Export Successful', 
        'header': header, 
        'instance_export': instance_export,
        'schedule_rating': True,
        'pk_for_sr': pk_for_sr}
    return render(request, 'schedule_rating/success.html', context=context)

@login_required
def download(request, pk):
    """
    Downloadable content for the excel workbooks
    """
    instance_export = models.Export.objects.get(pk=pk)
    file_name = instance_export.file_name
    buffer = open("tmp/{}".format(file_name), 'rb')
    return FileResponse(buffer, as_attachment=True, filename=file_name)

@login_required
def upload_file(request):
    title = "Upload Form"
    if request.method == 'POST':
        form = forms.UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            upload_instance = form.save()  # once saved, you have a Upload object instance with an id
            upload_instance.created_by = request.user.id
            upload_instance.save()

            fname = handle_uploaded_file_sr(request.FILES['file'])
             # check form types to determine which module to use
            uploader = uploadSR(fname = fname, user_id = request.user.id, 
                upload_id = upload_instance.id)
            # in case there is an issue uploading the data
            uploader.open_workbook()
            try:
                uploader.run()
                pk = uploader.generalinfo.pk
                return redirect('edit-header-view', pk=pk)
            except:
                import xlwings as xl
                app = xl.apps.active
                app.quit()
                messages.error(request, "Could not read Schedule Rating form")
                return redirect('upload')
    else:
        form = forms.UploadFileForm(request.GET or None)
    context = {'form': form, 'title': title, 'schedule_rating': True}
    return render(request, 'schedule_rating/upload.html', context = context)

"""
Export Schedule Rating for QBE & BH
"""
@login_required
def ExportView(request, pk):
    """
    Display model form to export Schedule Rating 
    """
    #print(os.path.basename('C:\\Users\\jnavarrete\\Documents\\Midwestern Insurance Agency\\miaworkcomp\\export\\schedule_rating_3.xlsm'))
    header = models.SRHeader.objects.get(pk=pk)
    form = forms.ExportFormSR(initial={'form_type': header.form_type})
    user_id = request.user.id
    pk_for_sr = header.generalinfo.pk
    if request.method == 'POST':
        form = forms.ExportFormSR(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            #form_type = cleaned_data['form_type']
            export_to_webdocs = cleaned_data['export_to_webdocs']
            # export will be QBE for now since idk if we have a template for BH
            exporter = ExportSR(user_id=user_id, pk=pk, form_type=header.form_type, export_to_webdocs=export_to_webdocs)
            app = exporter.open_workbook()
            pid = app.pid
            try:
                exporter.run()
                # save the export record
                instance = form.save(commit=False)
                instance.file_name = os.path.basename(exporter.outfile)
                instance.header_id = pk
                instance.form_type = header.form_type

                # Grab user
                instance.created_by = request.user.pk

                instance.save()

                if not exporter.exported_to_network_drive:
                    message = "Workbook was not exported to Webdocs"  
                    messages.info(request, message=message)
                else:
                    message="Workbook successfully exported to network drive"
                    messages.success(request, message=message)

                # check to make sure the Excel workbook is closed
                os.system("tskill {}".format(pid))

                return redirect("sr-export-success", pk=instance.id)
            except:
                exporter.app.quit()
                exporter.close_logger()
                # if for some reason the export becomes unresponsive
                # kill the process
                os.system("tskill {}".format(pid))
                # then send an email alert
                
                with open("tmp/export-{}-{}.log".format('schedule_rating', pk)) as log:
                    data = log.readlines()
                    message = "".join(data)

                mail_admins('[Django] Error Exporting {}-{}'.format('schedule_rating',pk), message)
                exporter.logger.error("Issue has occured. Admins were contacted.", exc_info=True)
                messages.error(request, message="Issue has occured. Admins were contacted.")
                form = forms.ExportFormSR(request.POST)
            form.save()
        else:
            form = forms.ExportFormSR(request.POST)
    title = "Export Schedule Rating"
    context = {'form': form, 'title': title, 'schedule_rating': True, 'pk_for_sr': pk_for_sr}
    return render(request, template_name="schedule_rating/export.html", context=context)

"""
From Workbook we need to redirect to schedule rating
A. Schedule rating needs to be created
or 
B. Schedule rating exists and needs to be edited
"""

def schedule_rating_redirect(request):
    return redirect('schedule-rating-list')

"""
List View
    Basic landing page for Schedule Rating
"""
@method_decorator(login_required, name='dispatch')
class FormListView(ListView):
    model = models.SRHeader
    paginate_by = 5  # if pagination is desired
    template_name = 'schedule_rating/listview.html'
    context_object_name = 'posts'

    def get_context_data(self):
        context = super().get_context_data()
        context['title'] = 'Schedule Rating Forms'
        context['filter_form'] = forms.FilterListView(self.request.GET or None)
        context['schedule_rating'] = True
        get_copy = self.request.GET.copy()
        if get_copy.get('page'):
            get_copy.pop('page')
        context['get_copy'] = get_copy
        return context

    def get_queryset(self):
        queryset = models.SRHeader.objects.all()
        form_id = self.request.GET.get('form_id')
        if form_id:
            return queryset.filter(pk = form_id)
        unique_number = self.request.GET.get('unique_number')
        if unique_number:
            return queryset.filter(unique_number = unique_number)
        uw = self.request.GET.get('uw')
        if uw:
            queryset = queryset.filter(uw=uw)
        order_by = self.request.GET.get('order_by')
        order = self.request.GET.get('order')
        if order_by:
            order_by = order + order_by
        else:
            order_by = '-id'
        queryset = queryset.order_by(order_by)
        results_number = self.request.GET.get('results')
        if results_number:
            self.paginate_by = results_number
        return queryset

@method_decorator(login_required, name='dispatch')
class ListViewByRiskEval(ListView):
    model = models.SRHeader
    paginate_by = 5  # if pagination is desired
    template_name = 'schedule_rating/listview.html'
    context_object_name = 'posts'

    def get_context_data(self):
        context = super().get_context_data()
        context['title'] = 'Schedule Rating Forms by Risk Eval'
        context['schedule_rating'] = True
        context['pk_for_sr'] = self.kwargs['pk']
        return context

    def get_queryset(self):
        self.generalinfo = get_object_or_404(GeneralInfo, pk=self.kwargs['pk'])
        queryset = models.SRHeader.objects.filter(generalinfo = self.generalinfo)
        return queryset


"""
Entry Page 1
    First form to be created
    Acts as primary key for other forms
"""
@login_required
def CreateHeaderView(request, pk):
    # view recieves PK from GeneralInfo model
    generalinfo_instance = GeneralInfo.objects.get(pk=pk)
    data = generalinfo_instance.__dict__
    form = forms.CreateSRHeaderForm(initial=data)
    pk_for_sr = generalinfo_instance.pk
    if request.method =='POST':
        form = forms.CreateSRHeaderForm(request.POST)
        if form.is_valid():  
            instance=form.save(commit=False)
            instance.generalinfo_id = pk

            # Grab user
            instance.last_modified_by = request.user.pk

            if instance.form_type == "QBE":
                if instance.data_set:
                    info = carrier_info[instance.data_set]
                    instance.carrier = info['carrier']
                    instance.carrier_code = info['carrier_code']
                    instance.save()
                else:
                    messages.error(request, message='Data Set is missing in Risk Eval. Populate Data set for QBE Risk Evals before creating a Schedule Rating')
                    return redirect('EditSectionA', pk=pk)
            else:
                instance.save() # save the header form
            header_pk = instance.id
            messages.success(request, message='Schedule Rating Created')
            return redirect('select-states-view', pk = header_pk)
    context = {'form':form, 'title': 'Create Worksheet Prep', 
        'schedule_rating': True, 'pk_for_sr': pk_for_sr}
    return render(request, 'schedule_rating/header.html', context)

"""
Edit view for Page 1
"""
@login_required
def EditHeaderView(request, pk):
    instance_header = models.SRHeader.objects.get(pk=pk)
    form = forms.EditSRHeaderForm( instance= instance_header)
    if request.method =='POST':
        form = forms.EditSRHeaderForm(request.POST, instance= instance_header or None)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.header_id = instance_header.id

            # Grab user
            instance.last_modified_by = request.user.pk

            instance.save()
            messages.success(request,message='Worksheet Prep Updated')
            return redirect("edit-header-view",pk = pk)
    context = {'form':form, 'title': 'Worksheet Prep', 
        'header': instance_header, 'schedule_rating': True,
        'pk_for_sr': instance_header.generalinfo.pk}
    return render(request, 'schedule_rating/header.html', context)

"""
Page 2 Choose States for Schedule Rating Form
"""
@login_required
def SelectStatesView(request, pk):
    instance_header = models.SRHeader.objects.get(pk=pk)
    instance_states = models.SRStates.objects.filter(header= instance_header)
    previous_states = None
    pk_for_sr = instance_header.generalinfo.pk
    if len(instance_states):
        instance_states = instance_states[0]
        # get the list of states that was previously created; else it's None
        previous_states = instance_states.states 

    if request.method =='POST':
        # model: models.SRStates
        form = forms.SelectStatesForm(request.POST, instance=instance_states or None)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.header_id = instance_header.id

            # Grab user
            instance.last_modified_by = request.user.pk

            instance.save()
            update_workcomplines(instance_header, states=instance.states, 
                previous_states=previous_states, form_type = instance_header.form_type)
            messages.success(request,message='States Updated')
            return redirect('states-list-view',pk=pk)
                
    form = forms.SelectStatesForm(instance = instance_states or None)
    title = 'Select States' 
    checked_states = []
    if instance_states:
        checked_states = instance_states.states
    context = {'form':form, 'title': title, 'header': instance_header, 
        'schedule_rating': True, 'checked_states': checked_states, 'pk_for_sr': pk_for_sr}
    return render(request, 'schedule_rating/states.html', context)

"""
Page 3
    For each state selected, user has to populate Work Comp Lines information
"""
@login_required
def StateView(request, pk, state):
    if state == "AZ":
        header_form = forms.AZHeaderForm
        line_formset = forms.AZLineFormset
        state_header_model=models.AdaptedStateHeader
        state_line_model=models.AdaptedStateLines
    elif state == "CA":
        header_form = forms.CAHeaderForm
        line_formset = forms.CALineFormset
        state_header_model=models.CAHeader
        state_line_model=models.CALines
    elif state == "KS":
        header_form = forms.KSHeaderForm
        line_formset = forms.KSLineFormset
        state_header_model=models.AdaptedStateHeader
        state_line_model=models.AdaptedStateLines
    elif state == "NH":
        header_form = forms.NHHeaderForm
        line_formset = forms.NHLineFormset
        state_header_model=models.AdaptedStateHeader
        state_line_model=models.AdaptedStateLines
    elif state == "NM":
        header_form = forms.NMHeaderForm
        line_formset = forms.NMLineFormset
        state_header_model=models.AdaptedStateHeader
        state_line_model=models.AdaptedStateLines
    elif state in 'SD':
        header_form = forms.SDHeaderForm
        line_formset = forms.SDLineFormset
        state_header_model=models.AdaptedStateHeader
        state_line_model=models.AdaptedStateLines
    elif state == "OK":
        header_form = forms.OKHeaderForm
        line_formset = forms.OKLineFormset
        state_header_model=models.AdaptedStateHeader
        state_line_model=models.AdaptedStateLines
    elif state == 'VT':
        header_form = forms.VTHeaderForm
        line_formset = forms.VTLineFormset
        state_header_model=models.AdaptedStateHeader
        state_line_model=models.AdaptedStateLines
    else:
        header_form = forms.StateHeaderForm
        line_formset = forms.StateFormset
        state_header_model=models.StateHeader
        state_line_model=models.StateLines
    return StateFormView(request, pk, state, 
            state_header_model=state_header_model,
            state_line_model=state_line_model,
            header_form=header_form, line_formset=line_formset)

@login_required
def StateFormView(request, pk, state, state_header_model, state_line_model, header_form, line_formset):
    instance_header = models.SRHeader.objects.get(pk = pk)
    state_header = state_header_model.objects.filter(header=instance_header, state = state)
    state_header = state_header[0]
    queryset = state_line_model.objects.filter(header= state_header, state = state)
    pk_for_sr = instance_header.generalinfo.pk

    form_header = header_form(instance = state_header or None)
    formset = line_formset(queryset=queryset)

    if request.method =='POST':
        form_header = header_form(request.POST, 
            instance=state_header or None)
        formset = line_formset(request.POST, queryset=queryset)

        if form_header.is_valid():
            instance= form_header.save(commit=False)
            instance.header_id = instance_header.id

            # Grab user
            instance.last_modified_by = request.user.pk

            instance.save()

            messages.success(request,message='Header saved')
        else:
            messages.error(request, 'Fix Header entry errors')

        if formset.is_valid():
            #instance = formset.save(commit=False)
            formset.save()
            # Grab user
            #instance.last_modified_by = request.user.pk

            #instance.save()
            messages.success(request,message='State lines saved')
        else:
            messages.error(request,'Fix State Lines entry errors')

        if form_header.is_valid() and formset.is_valid():    
            return redirect('work-comp-lines-view', pk=pk, state=state)
        #else:
            # need to handle error messages in the future
            #print(formset.errors)
    
    title= "Schedule Rating Worksheet"
    form_title1 = "Risk Location"
    form_title2 = "Credits and Debits"
    context = {'formset':formset, 'form_header':form_header,
        'title': title, 'form_title1': form_title1, 
        'form_title2': form_title2, 'schedule_rating': True,
        'header': instance_header,
        'state_name': states_names[state], 'pk_for_sr': pk_for_sr}
    return render(request, 'schedule_rating/state-form-view.html', context)

@method_decorator(login_required, name='dispatch')
class SRHeaderDelete(DeleteView):
    model = models.SRHeader
    template_name = 'schedule_rating/deleteview.html'
    success_url = '/schedule_rating/list/'
    queryset = models.SRHeader.objects.all()

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(models.SRHeader, pk=pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['schedule_rating'] = True
        context['pk_for_sr'] = self.get_object().generalinfo.pk
        return context


"""
States Filter
    User is able to select a form and from the form edit each individual state
"""
@login_required
def StatesListView(request, pk):
    instance_header = models.SRHeader.objects.get(pk=pk)
    instance_states = models.SRStates.objects.filter(header= instance_header)
    pk_for_sr = instance_header.generalinfo.pk
    if len(instance_states):
        instance_states = instance_states[0]
    else:
        return redirect('select-states-view', pk=pk)
    title = 'Selected States'
    context = {'post':instance_states, 'title': title, 
        'pk':pk, 'schedule_rating': True,
        'header': instance_header, 'pk_for_sr': pk_for_sr}
    return render(request, 'schedule_rating/stateslistview.html', context)
  


    