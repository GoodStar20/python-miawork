from enum import unique
from django.forms.widgets import Select
from django.urls.base import clear_script_prefix
from .serializers import GeneralInfoSerializer
from rest_framework import viewsets
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from . import forms
from . import models
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView
from django.urls import reverse
from django.http import HttpResponseRedirect, FileResponse
from . import uw_notes_calculator as helper
import os
from django.core.mail import mail_admins
from excel import Export
from excel import handle_uploaded_file, Upload
import datetime as dt
from risk_eval.calculations import qbe, ReadCalculations
from . import utils
from datetime import datetime as dtt

def home(request, **kwargs):
    context = {'title': 'MIA Web Forms', 'home': True}
    return render(request, 'risk_eval/home.html', context)

def success(request, pk):
    """
    Export Success View
    """
    instance_export = models.Export.objects.get(pk=pk)
    generalinfo = models.GeneralInfo.objects.get(
        pk=instance_export.generalinfo_id)
    context = {'title': 'Export Successful',
               'generalinfo': generalinfo,
               'instance_export': instance_export}
    return render(request, 'risk_eval/success.html', context=context)

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
            # Once saved, you have a Upload object instance with an id
            upload_instance = form.save()
            upload_instance.created_by = request.user.id
            upload_instance.save()
            fname = handle_uploaded_file(request.FILES['file'])

            # Check form types to determine which module to use
            uploader = Upload(fname=fname, user_id=request.user.id,
                              upload_id=upload_instance.id, kind=request.POST['form_type'])
            request.session['fname'] = fname
            request.session['upload_instance_id'] = upload_instance.id
            request.session['form_type'] = request.POST['form_type']

            # In case there is an issue uploading the data
            # TO DO LIST:
            # There needs to be a way to determine what (if any) data was uploaded
            app = uploader.open_workbook()
            pid = app.pid
            form_type = upload_instance.form_type
            response, unique_number, general_infos = uploader.check_general_info_exists()
            request.session['unique_number'] = unique_number
            request.session['old_pid'] = pid
            if response == 'Create':
                try:
                    # run all for Risk Eval
                    uploader.risk_eval(response, unique_number, form_type, '')

                    # UW Specialty Notes
                    uploader.uw_specialty(response, unique_number, '')
                    uploader.exit()  # close and delete tmp workbook
                    pk = uploader.generalinfo.pk

                    # check to make sure the Excel workbook is closed
                    os.system("tskill {}".format(pid))
                    del request.session['unique_number']
                    del request.session['form_type']
                    del request.session['upload_instance_id']
                    del request.session['fname']
                    return redirect('EditSectionA', pk=pk)
                except:
                    uploader.logger.error(
                        "Upload was terminated.", exc_info=True)
                    uploader.exit()
                    # if for some reason the export becomes unresponsive
                    # kill the process
                    os.system("tskill {}".format(pid))
                    # then send an email alert
                    pk = upload_instance.id
                    with open("tmp/excel_upload_{}.log".format(pk)) as log:
                        data = log.readlines()
                        message = "".join(data)

                    mail_admins(
                        '[Django] Error Uploading Workbook'.format(pk), message)
                    messages.error(request, "Upload was not complete!")
                    del request.session['unique_number']
                    del request.session['form_type']
                    del request.session['upload_instance_id']
                    del request.session['fname']
                    return redirect('upload')
            else:
                response = 'Override'
                request.session['unique_number'] = unique_number
                context = {'unique_number': unique_number, 'general_infos': general_infos.order_by(
                    '-effective_date', '-quote_number')}
                return render(request, 'risk_eval/warn.html', context)
    else:
        form = forms.UploadFileForm(request.GET or None)
    return render(request, 'risk_eval/upload.html', {'form': form, 'title': title})

def create_new(request):
    if request.session.has_key('fname'):
        fname = request.session['fname']
    if request.session.has_key('upload_instance_id'):
        upload_instance_id = request.session['upload_instance_id']
    if request.session.has_key('form_type'):
        form_type = request.session['form_type']
    if request.session.has_key('unique_number'):
        unique_number = request.session['unique_number']
    if request.session.has_key('old_pid'):
        old_pid = request.session['old_pid']

    uploader = Upload(fname=fname, user_id=request.user.id,
                      upload_id=upload_instance_id, kind=form_type)
    app = uploader.open_workbook()
    pid = app.pid
    utils.kill_file(fname, old_pid)
    response = 'Create'
    try:
        # run all for Risk Eval
        uploader.risk_eval(response, unique_number, form_type, '')
        uploader.uw_specialty(response, unique_number,
                              '')  # UW Specialty Notes
        uploader.exit()  # close and delete tmp workbook
        pk = uploader.generalinfo.pk
        # check to make sure the Excel workbook is closed
        os.system("tskill {}".format(pid))
        del request.session['unique_number']
        del request.session['form_type']
        del request.session['upload_instance_id']
        del request.session['fname']
        return redirect('EditSectionA', pk=pk)
    except:
        uploader.logger.error("Upload was terminated.", exc_info=True)
        uploader.exit()
        # if for some reason the export becomes unresponsive
        # kill the process
        os.system("tskill {}".format(pid))
        # then send an email alert
        pk = upload_instance_id
        with open("tmp/excel_upload_{}.log".format(pk)) as log:
            data = log.readlines()
            message = "".join(data)

        mail_admins('[Django] Error Uploading Workbook'.format(pk), message)
        messages.error(request, "Upload was not complete!")
        del request.session['unique_number']
        del request.session['form_type']
        del request.session['upload_instance_id']
        del request.session['fname']
        return redirect('upload')

@login_required
def override_file_data(request, id):
    if request.session.has_key('fname'):
        fname = request.session['fname']
    if request.session.has_key('upload_instance_id'):
        upload_instance_id = request.session['upload_instance_id']
    if request.session.has_key('form_type'):
        form_type = request.session['form_type']
    if request.session.has_key('unique_number'):
        unique_number = request.session['unique_number']
    if request.session.has_key('old_pid'):
        old_pid = request.session['old_pid']

    uploader = Upload(fname=fname, user_id=request.user.id,
                      upload_id=upload_instance_id, kind=form_type)
    app = uploader.open_workbook()
    pid = app.pid
    utils.kill_file(fname, old_pid)
    try:
        generalinfo = models.GeneralInfo.objects.filter(id=id)
        if generalinfo.exists():
            # Don't beleive this works, want to double check
            generalinfo.first().delete()
        
        response = 'Create'

        # Run all for Risk Eval
        uploader.risk_eval(response, unique_number, form_type, id)

        # Run UW Specialty Notes
        uploader.uw_specialty(response, unique_number,
                              id) 

        # Close and delete tmp workbook
        uploader.exit()  
        pk = uploader.generalinfo.pk

        # Check to make sure the Excel workbook is closed
        os.system("tskill {}".format(pid))
        del request.session['unique_number']
        del request.session['form_type']
        del request.session['upload_instance_id']
        del request.session['fname']
        return redirect('EditSectionA', pk=pk)
    except:
        uploader.logger.error("Upload was terminated.", exc_info=True)
        uploader.exit()
        # if for some reason the export becomes unresponsive
        # kill the process
        os.system("tskill {}".format(pid))
        # then send an email alert
        pk = upload_instance_id
        with open("tmp/excel_upload_{}.log".format(pk)) as log:
            data = log.readlines()
            message = "".join(data)

        mail_admins('[Django] Error Uploading Workbook'.format(pk), message)
        messages.error(request, "Upload was not complete!")
        del request.session['unique_number']
        del request.session['form_type']
        del request.session['upload_instance_id']
        del request.session['fname']
        return redirect('upload')

@login_required
def export_view(request, pk):
    """
    Display model form to export risk eval
    """
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    form = forms.ExportForm()
    user_id = request.user.id
    if request.method == "POST":
        form = forms.ExportForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            form_type = instance_generalinfo.carrier
            export_to_webdocs = cleaned_data['export_to_webdocs']
            exporter = Export(
                user_id=user_id, pk=pk, form_type=form_type, export_to_webdocs=export_to_webdocs)
            app = exporter.open_workbook()
            pid = app.pid
            try:
                exporter.risk_eval()
                exporter.uw_specialty()
                exporter.save_and_exit()
                # save the export record
                instance = form.save(commit=False)
                instance.file_name = os.path.basename(exporter.outfile)
                instance.generalinfo_id = pk
                instance.form_type = form_type  # decided by GeneralInfo
                instance.save()

                if not exporter.exported_to_network_drive:
                    message = "Workbook was not exported to Webdocs"
                    messages.info(request, message=message)
                else:
                    message = "Workbook successfully exported to network drive"
                    messages.success(request, message=message)

                # check to make sure the Excel workbook is closed
                os.system("tskill {}".format(pid))
                return redirect("success", pk=instance.id)
            except:
                exporter.app.quit()
                exporter.close_logger()
                # if for some reason the export becomes unresponsive
                # kill the process
                os.system("tskill {}".format(pid))
                # then send an email alert

                with open("tmp/export-{}-{}.log".format('risk_eval', pk)) as log:
                    data = log.readlines()
                    message = "".join(data)

                mail_admins('[Django] Error Exporting {}'.format(pk), message)
                exporter.logger.error(
                    "Issue has occured. Admins were contacted.", exc_info=True)
                messages.error(
                    request, message="Issue has occured. Admins were contacted.")
                form = forms.ExportForm(request.POST)
            form.save()
        else:
            form = forms.ExportForm(request.POST)
    title = "Export Risk Eval"
    context = {'form': form, 'title': title}
    return render(request, template_name="risk_eval/export.html", context=context)

@method_decorator(login_required, name='dispatch')
class FormListView(ListView):
    model = models.GeneralInfo
    paginate_by = 5  # if pagination is desired
    template_name = 'risk_eval/listview.html'
    context_object_name = 'forms'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Form List View'
        context['filter_form'] = forms.FilterListView(self.request.GET or None)
        get_copy = self.request.GET.copy()
        if get_copy.get('page'):
            get_copy.pop('page')
        context['get_copy'] = get_copy
        return context

    def get_queryset(self):
        queryset = models.GeneralInfo.objects.all()
        form_id = self.request.GET.get('form_id')
        if form_id:
            return queryset.filter(pk=form_id)
        unique_number = self.request.GET.get('unique_number')
        if unique_number:
            return queryset.filter(unique_number=unique_number)
        uw = self.request.GET.get('uw')
        if uw:
            queryset = queryset.filter(uw=uw)
        order_by = self.request.GET.get('order_by')
        order = self.request.GET.get('order')
        if order_by:
            if order_by == 'account_number':
                queryset = queryset.exclude(account_number__isnull=True)
            order_by = order + order_by
        else:
            order_by = '-id'
        queryset = queryset.order_by(order_by)
        results_number = self.request.GET.get('results')

        if results_number:
            self.paginate_by = results_number
        return queryset

@login_required
def CreateRiskEval(request):
    # first create initial blank form
    form = forms.CreateRiskEvalForm()

    if request.method == "POST":
        form = forms.CreateRiskEvalForm(request.POST)

        if form.is_valid():

            # Set the  form
            instance = form.save(commit=False)

            # Set user that created risk eval
            instance.created_by = request.user.pk
            instance.last_modified_by = request.user.pk

            # Save the form
            instance.save()

            # Next, create the instances for account history because UWs
            # Want this to be created for them ahead of time

            # Set the insured dates and year
            effective_date = instance.effective_date
            expiration_date = instance.expiration_date
            year = instance.effective_date.year

            # Build account history
            for i in range(1, 6):
                # Create account history instance
                effective_date = dt.date(
                    effective_date.year - 1, effective_date.month, effective_date.day)
                expiration_date = dt.date(
                    expiration_date.year - 1, expiration_date.month, expiration_date.day)
                q = models.AccountHistory(generalinfo=instance, policy_period=i, effective_date=effective_date,
                                          expiration_date=expiration_date, last_modified_by=request.user.pk)
                q.save()

                # create loss instance
                models.LossRatingValuation(
                    generalinfo=instance, policy_period=i, last_modified_by=request.user.pk).save()

            for _ in range(6):
                # create exmod year
                exmod_instance = models.RiskExmod(
                    generalinfo=instance, year=year, last_modified_by=request.user.pk)
                exmod_instance.save()
                year -= 1

            return redirect("EditSectionA", pk=instance.pk)

        # Note by prior developer
        # If the forms have any issues, return them
        # Kinda double work, but it's the best I can do for now
        if not form.is_valid():
            # recreate form to pass along errors
            form = forms.CreateRiskEvalForm(request.POST)

    title = "Create Risk Eval"
    context = {'form': form,
               'title': title}
    return render(request, "risk_eval/create.html", context=context)

@login_required
def RenewRiskEval(request, pk):
    # first copy the risk eval header GeneralInfo
    generalinfo = models.GeneralInfo.objects.get(pk=pk)
    new_riskeval = generalinfo
    new_riskeval.pk = None
    # update the effective and expiration dates
    previous_eff_date = generalinfo.effective_date
    new_riskeval.effective_date = dt.date(
        previous_eff_date.year+1, previous_eff_date.month, previous_eff_date.day)
    previous_exp_date = generalinfo.expiration_date
    new_riskeval.expiration_date = dt.date(
        previous_exp_date.year+1, previous_exp_date.month, previous_exp_date.day)

    # Update last modified info
    new_riskeval.last_modified_by = request.user.pk

    # Save the record
    # Assure this is a new record, believe it is
    new_riskeval.save()

    # Recreate this instance as new_riskeval = generalinfo
    generalinfo = models.GeneralInfo.objects.get(
        pk=pk)  # Note from prior developer: only use this to pull data, never save (which makes sense)!

    # If they exist, copy the class codes and payroll lines
    qset = models.GeneralInfoPremium.objects.filter(generalinfo=generalinfo)

    if len(qset):
        for q in qset:

            # Set foreign key to new risk eval
            q.generalinfo = new_riskeval

            # Clear primary key to get a new one
            q.pk = None
          
            # Save new record
            q.save()

    # Next, if they exist copy the account and loss lines
    qset = models.AccountHistory.objects.filter(
        generalinfo=generalinfo).order_by('policy_period')

    # Create the first policy period
    q = models.AccountHistory(generalinfo=new_riskeval, policy_period=1,
                              effective_date=previous_eff_date, expiration_date=previous_exp_date, last_modified_by=request.user.pk)
    
    # Save the first record
    q.save()

    for i, q in enumerate(qset):

        # If past adding the 4th updated year, break out
        if i > 3:
            break

        # Update policy period by 1 year
        q.policy_period = q.policy_period + 1

        # Set foreign key to new risk eval
        q.generalinfo = new_riskeval

        # Clear primary key to get a new one
        q.pk = None

        # Save new record
        q.save()

    qset = models.LossRatingValuation.objects.filter(
        generalinfo=generalinfo).order_by('policy_period')

    # Could not remove default for prior_carrier: , prior_carrier = "" in q below, or error, Doorn, 2/27/2022
    """q = models.LossRatingValuation(generalinfo=new_riskeval, policy_period=1,
                                   valuation_date=dt.datetime.now().date(), prior_carrier=None, last_modified_by=request.user.pk)"""
    q = models.LossRatingValuation(generalinfo=new_riskeval, policy_period=1,
                                   prior_carrier=None, last_modified_by=request.user.pk)
    
    q.save()

    for i, q in enumerate(qset):

        # If past adding the 4th updated year, break out
        if i > 3:
            break

        # Update policy period by 1 year
        q.policy_period = q.policy_period + 1

        # Set foreign key to new risk eval
        q.generalinfo = new_riskeval

        # Clear primary key to get a new one
        q.pk = None

        # Save new record
        q.save()

    # Next, copy risk header and exmod
    qset = models.RiskHeader.objects.filter(generalinfo=generalinfo)
    if len(qset):

        # Get the first record (only record for prior risk eval)
        q = qset[0]

        # Set foreign key to new risk eval
        q.generalinfo = new_riskeval

        # Clear primary key to get a new one
        q.pk = None

        # Save new record
        q.save()

    qset = models.RiskExmod.objects.filter(
        generalinfo=generalinfo).order_by('-year')[:5]

    # Set first Exmod to new year
    year = new_riskeval.effective_date.year

    # Save first Exmod year
    q = models.RiskExmod(generalinfo=new_riskeval, year=year)

    q.save()

    # Loop and add prior Exmod's
    for q in qset:

        # Set the year to one prior for history
        year -= 1
        q.year = year

        # Set foreign key to new risk eval
        q.generalinfo = new_riskeval

        # Clear primary key to get a new one
        q.pk = None        

        # Save new record
        q.save()

    # Next, copy checklist
    qset = models.Checklist.objects.filter(generalinfo=generalinfo)

    if len(qset):

        # Get the first record (only record for prior risk eval)
        q = qset[0]

        # Set foreign key to new risk eval
        q.generalinfo = new_riskeval

        # Clear primary key to get a new one
        q.pk = None       

        # Save new record
        q.save()

    # Next, copy comments
    qset = models.Comments.objects.filter(generalinfo=generalinfo)
    if len(qset):

        # Get the first record (only record for prior risk eval)
        q = qset[0]

        # Set foreign key to new risk eval
        q.generalinfo = new_riskeval

        # Clear primary key to get a new one
        q.pk = None
        
        # Save new record
        q.save()


    # Next, copy claim details
    qset = models.Claims.objects.filter(generalinfo=generalinfo)
    for q in qset:
        q.generalinfo = new_riskeval
        q.pk = None
        q.save()

    # Next, copy underwriter details
    qset = models.EvalUnderwriter.objects.filter(generalinfo=generalinfo)
    if len(qset):
        q = qset[0]
        q.generalinfo = new_riskeval
        q.pk = None
        q.save()

    # Next, copy notes
    qset = models.Notes.objects.filter(generalinfo=generalinfo)
    if len(qset):
        q = qset[0]
        q.generalinfo = new_riskeval
        q.pk = None
        q.save()

    # Next, copy score
    qset = models.Score.objects.filter(generalinfo=generalinfo)
    if len(qset):
        q = qset[0]
        q.generalinfo = new_riskeval
        q.pk = None
        q.save()

    # Next, copy Logging
    qset = models.LoggingHeader.objects.filter(generalinfo=generalinfo)
    if len(qset):
        q = qset[0]
        q.generalinfo = new_riskeval
        q.pk = None
        q.save()

    qset = models.LoggingExposureCategories.objects.filter(
        generalinfo=generalinfo)
    if len(qset):
        q = qset[0]
        q.generalinfo = new_riskeval
        q.pk = None
        q.save()

    # Next, copy Mechanical
    qset = models.MechanicalHeader.objects.filter(generalinfo=generalinfo)
    if len(qset):
        q = qset[0]
        q.generalinfo = new_riskeval
        q.pk = None
        q.save()

    qset = models.MechanicalCategories.objects.filter(generalinfo=generalinfo)
    if len(qset):
        q = qset[0]
        q.generalinfo = new_riskeval
        q.pk = None
        q.save()

    # Next, copy Wood Manual
    qset = models.WoodManualHeader.objects.filter(generalinfo=generalinfo)
    if len(qset):
        q = qset[0]
        q.generalinfo = new_riskeval
        q.pk = None
        q.save()

    qset = models.WoodMechanicalCategories.objects.filter(
        generalinfo=generalinfo)
    if len(qset):
        q = qset[0]
        q.generalinfo = new_riskeval
        q.pk = None
        q.save()

    messages.success(request, "Renewal Form Created")
    return redirect("EditSectionA", pk=new_riskeval.pk)

@login_required
def EditGeneralInfo(request, pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    named_insured = instance_generalinfo.named_insured
    unique_number = instance_generalinfo.unique_number
    generalinfo_form = forms.EditFormGeneralInfo(
        instance=instance_generalinfo or None)
    premium_formset = forms.PremiumLineFormSet(
        instance=instance_generalinfo or None)

    if request.method == "POST":
        generalinfo_form = forms.EditFormGeneralInfo(request.POST,
                                                     instance=instance_generalinfo or None)

        premium_formset = forms.PremiumLineFormSet(request.POST,
                                                   instance=instance_generalinfo)

        # Forms only saved if both form and formset are valid
        if generalinfo_form.is_valid() and premium_formset.is_valid():
            formset_list = premium_formset.save()
            # update each saved record with the current user who edited the form
            for instance in formset_list:

                # Grab user
                instance.last_modified_by = request.user.pk

                # Save result
                instance.save()

            instance = generalinfo_form.save(commit=False)

            # Grab user
            instance.last_modified_by = request.user.pk

            manual_premium_qset = models.GeneralInfoPremium.objects.filter(
                generalinfo_id=instance.id)
            manual_premium = sum(
                [q.manual_premium or 0 for q in manual_premium_qset])
            instance.projected_base_premium = manual_premium
            instance.save()

            messages.success(request, 'General Info Saved')
            messages.success(request, 'Class Codes & Payroll Saved')
            return redirect('EditSectionA', pk=instance_generalinfo.id)
        # Show messages in correct order.
        if not generalinfo_form.is_valid():
            messages.error(request, "Fix General Info entry errors")
        if not premium_formset.is_valid():
            messages.error(request, "Fix Class Codes & Payroll entry errors")

    title = 'A. General Info'
    form_title1 = 'General Info'
    form_title2 = 'Class Codes & Payroll'
    context = {'title': title, 'form_title1': form_title1,
               'generalinfo': instance_generalinfo,
               'form_title2': form_title2,
               'generalinfo_form': generalinfo_form,
               'premiumlines': premium_formset,
               'named_insured': named_insured,
               'unique_number': unique_number
               }
    return render(request, "risk_eval/EditGeneralInfo.html", context=context)

@login_required
def AccountHistoryView(request, pk):
    today_date = dtt.today().strftime('%Y-%m-%d')
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    named_insured = instance_generalinfo.named_insured
    unique_number = instance_generalinfo.unique_number

    # Open account history and loss history data
    acchist_queryset = models.AccountHistory.objects.filter(
        generalinfo=instance_generalinfo).order_by('policy_period')
    loss_queryset = models.LossRatingValuation.objects.filter(
        generalinfo=instance_generalinfo).order_by('policy_period')

    # Added Order by here and removed call to run this same query again below, Doorn, 3/6/2022
    claims_queryset = models.Claims.objects.filter(
        generalinfo=instance_generalinfo).order_by('-incurred')

    # Open Ex Mod data
    risk_mode_queryset = models.RiskExmod.objects.filter(
        generalinfo=instance_generalinfo).order_by('-year')

    # Set dates and years for new record calcs below, Doorn, 3/6/2022
    effective_date = instance_generalinfo.effective_date
    expiration_date = instance_generalinfo.expiration_date
    year = instance_generalinfo.effective_date.year

    # If a new history record is to be generated
    if len(acchist_queryset) == 0 and len(loss_queryset) == 0:

        for i in range(1, 6):
            # create account history instance
            effective_date = dt.date(
                effective_date.year - 1, effective_date.month, effective_date.day)
            expiration_date = dt.date(
                expiration_date.year - 1, expiration_date.month, expiration_date.day)

            q = models.AccountHistory(generalinfo=instance_generalinfo, policy_period=i,
                                      effective_date=effective_date, expiration_date=expiration_date, last_modified_by=request.user.pk)
            q.save()

            # create loss instance
            models.LossRatingValuation(
                generalinfo=instance_generalinfo, policy_period=i, last_modified_by=request.user.pk).save()

        # Refill datasets following the save, 3/6/2022, Doorn
        loss_queryset = models.LossRatingValuation.objects.filter(
            generalinfo=instance_generalinfo).order_by('policy_period')
        acchist_queryset = models.AccountHistory.objects.filter(
            generalinfo=instance_generalinfo).order_by('policy_period')

    # If a new Ex Mod entry
    if len(risk_mode_queryset) == 0:

        # Updated to get 6 years vs. 5 (changed range from 6 to 7), Doorn, 3/6/2022
        for _ in range(7):
            # create exmod year
            exmod_instance = models.RiskExmod(
                generalinfo=instance_generalinfo, year=year)
            exmod_instance.last_modified_by = request.user.pk
            exmod_instance.save()
            year -= 1
        # Update this piece to have Ex Mod function similarly to Loss History (claims_queryset above), 3/6/2022, Doorn
        # We do this as this was a new save of data
        risk_mode_queryset = models.RiskExmod.objects.filter(
            generalinfo=instance_generalinfo).order_by('-year')

    # Updated to only use risk_mode_queryset and remove acchist_queryset, Doorn, 3/6/2022
    risk_mode_values = utils.Risk_Ex_Mod(risk_mode_queryset)

    # FORMS
    acchist_form = forms.AccountFormSet(
        queryset=acchist_queryset, prefix='acchist')
    loss_form = forms.LossFormSet(queryset=loss_queryset, prefix='loss')

    selected = 0

    # If a post, save the data posted
    if request.method == "POST":

        # This is data from the Account History tab
        if 'loss_history_save' in request.POST or 'save_next_tab_large_loss' in request.POST:

            if 'loss_history_save' in request.POST:
                selected = 0
            else:
                # Go to next tab
                selected = 1

            # Put the loss history in a format to be saved
            loss_history = utils.get_data_dictionaries_for_loss_history(
                request)

            # Loop the loss data for saving
            count = 0
            for history in loss_history:

                # Extra check for no history, if a checkbox value
                if history['no_history'] == 'on':
                    history['no_history'] = True

                if ',' in history['incurred_loss']:
                    history['incurred_loss'] = history['incurred_loss'].replace(
                        ',', '')

                if ',' in history['paid_loss']:
                    history['paid_loss'] = history['paid_loss'].replace(
                        ',', '')

                if ',' in history['total_claims']:
                    history['total_claims'] = history['total_claims'].replace(
                        ',', '')

                if ',' in history['total_indemnity_claims']:
                    history['total_indemnity_claims'] = history['total_indemnity_claims'].replace(
                        ',', '')

                if ',' in history['indemnity_claims']:
                    history['indemnity_claims'] = history['indemnity_claims'].replace(
                        ',', '')

                if ',' in history['open_claims']:
                    history['open_claims'] = history['open_claims'].replace(
                        ',', '')

                if history['incurred_loss'] == '':
                    history['incurred_loss'] = None
                else:
                    history['incurred_loss'] = int(history['incurred_loss'])

                if history['paid_loss'] == '':
                    history['paid_loss'] = None
                else:
                    history['paid_loss'] = int(history['paid_loss'])

                if history['total_claims'] == '':
                    history['total_claims'] = None
                else:
                    history['total_claims'] = int(history['total_claims'])

                if history['total_indemnity_claims'] == '':
                    history['total_indemnity_claims'] = None
                else:
                    history['total_indemnity_claims'] = int(
                        history['total_indemnity_claims'])

                if history['indemnity_claims'] == '':
                    history['indemnity_claims'] = None
                else:
                    history['indemnity_claims'] = int(
                        history['indemnity_claims'])

                if history['open_claims'] == '':
                    history['open_claims'] = None
                else:
                    history['open_claims'] = int(history['open_claims'])

                history['effective date'] = dt.datetime.strptime(
                    history['effective date'], "%Y-%m-%d").strftime("%Y-%m-%d")
                history['expiration_date'] = dt.datetime.strptime(
                    history['expiration_date'], "%Y-%m-%d").strftime("%Y-%m-%d")
                try:
                    history['valuation_date'] = dt.datetime.strptime(
                        history['valuation_date'], "%Y-%m-%d").strftime("%Y-%m-%d")
                except:
                    history['valuation_date'] = None

                # Get datasets for updates
                # Commented out as dup action, 3/6/2022, Doorn
                #account_queryset = models.AccountHistory.objects.filter(generalinfo = instance_generalinfo)

                # Grab row from Account History list based on the count in the loop through records
                account_queryset = acchist_queryset[count]
                account_history = models.AccountHistory.objects.filter(
                    id=account_queryset.id)

                # Don't think we need this, since we've already called above, Doorn, 3/6/2022
                #risk_mode_queryset = models.RiskExmod.objects.filter(generalinfo = instance_generalinfo)

                # Update the Account History data in the database based on the form entries
                account_history.update(
                    policy_period=history['policy period'],
                    effective_date=history['effective date'],
                    no_history=history['no_history'],
                    expiration_date=history['expiration_date'],
                    incurred_losses=history['incurred_loss'],
                    paid_losses=history['paid_loss'],
                    total_claims=history['total_claims'],
                    total_indemnity_claims=history['total_indemnity_claims'],
                    indemnity_claims=history['indemnity_claims'],
                    open_claims=history['open_claims'],
                    last_modified_by=request.user.pk
                )

                # Update the Loss Rating table with new values now entered on the Account History tab
                rating_queryset = models.LossRatingValuation.objects.filter(
                    generalinfo=instance_generalinfo)
                rating_queryset = rating_queryset[count]
                rating_queryset = models.LossRatingValuation.objects.filter(
                    id=rating_queryset.id)

                rating_queryset.update(
                    valuation_date=history['valuation_date'],
                    prior_carrier=history['prior_carier'],
                )

                # Check if any rows have no history and update related Policy Period's to no history available
                if history['no_history'] == 'True':

                    # Note below is not going to work for Ex Mode with the new setup
                    # May want to use count + 1, or just have that checked on it's own, not related to account history

                    # Removing below for extra Ex Mod year for now, 3/6/2022, Doorn
                    # Update Ex Mod
                    """"                
                    queryset = risk_mode_queryset[count]
                    queryset.exmod_val = None                    
                    queryset.no_history = 1
                    queryset.save()
                    """

                    # Update account history for written premium field
                    account_history.update(
                        written_premium=None,
                        last_modified_by=request.user.pk
                    )

                    # Update ratings table
                    rating_queryset.update(
                        payroll=None,

                        # Added 3/6/22 to capture no history in db table
                        no_history=1,

                        last_modified_by=request.user.pk
                    )
                else:
                    # Added to take care of switching if there is history, 3/6/22, Doorn
                    # Update Ex Mod
                    # Removing below for extra Ex Mod year for now, 3/6/2022, Doorn
                    """"
                    queryset = risk_mode_queryset[count]
                    queryset.no_history = 0
                    queryset.save()
                    """

                    # Update ratings table
                    rating_queryset.update(
                        no_history=0,
                        last_modified_by=request.user.pk
                    )

                count += 1
                # Removed the following conditio as we want to show the save regardless
                # of which Save button, 3/12/2022
                # if 'loss_history_save' in request.POST:
                if count == 1:
                    messages.success(request, 'Loss History Data Updated')
                # except Exception as e:
                #     count +=1
                #     messages.error(request,'Error: {} in line number {}'.format(e,count))

            acchist_queryset = models.AccountHistory.objects.filter(
                generalinfo=instance_generalinfo).order_by('policy_period')
            loss_queryset = models.LossRatingValuation.objects.filter(
                generalinfo=instance_generalinfo).order_by('policy_period')

        if 'large_loss' in request.POST or 'save_next_tab_payroll_premium' in request.POST:

            if 'large_loss' in request.POST:
                selected = 1
            else:
                # Go to next tab
                selected = 2

            list_of_delete_objects = request.POST.getlist('delete')

            for object_id in list_of_delete_objects:
                claim_object = models.Claims.objects.get(id=object_id)
                claim_object.delete()

            large_loss = utils.get_data_dictionaries_for_large_loss(request)

            for loss in large_loss:
                if ',' in loss['paid']:
                    loss['paid'] = loss['paid'].replace(',', '')

                if ',' in loss['incurred']:
                    loss['incurred'] = loss['incurred'].replace(',', '')
                try:
                    loss['doi'] = dt.datetime.strptime(
                        loss['doi'], "%Y-%m-%d").strftime("%Y-%m-%d")
                except:
                    # Updated to handle null values, Doorn, 2/27/2022
                    # pass
                    loss['doi'] = None

                # Changed to avoid zero being default on save, Doorn, 2/27/2022
                if loss['paid'] == '':
                    loss['paid'] = None

                if loss['incurred'] == '':
                    loss['incurred'] = None

                try:
                    claim_queryset = models.Claims.objects.filter(
                        generalinfo=instance_generalinfo).order_by('-incurred')
                    claim_queryset = claim_queryset.filter(id=loss['claim_id'])

                    if claim_queryset.exists():
                        claim_queryset = claim_queryset.first()
                        claim_queryset.doi = loss['doi']
                        # Updated below to avoid error on null values
                        #claim_queryset.paid = int(loss['paid'])
                        #claim_queryset.incurred = int(loss['incurred'])
                        claim_queryset.paid = loss['paid']
                        claim_queryset.incurred = loss['incurred']
                        # End change

                        claim_queryset.status = loss['status']
                        claim_queryset.claimant = loss['claimant']
                        claim_queryset.litigated = loss['litigated']
                        claim_queryset.injury_description = loss['injury_description']
                        claim_queryset.last_modified_by = request.user.pk
                        claim_queryset.save()
                except:
                    loss.pop('claim_id')
                    claim_queryset = models.Claims.objects.create(
                        generalinfo=instance_generalinfo, **loss)
                    claim_queryset.last_modified_by = request.user.pk
                    claim_queryset.save()

            # Removed the following conditio as we want to show the save regardless
                # of which Save button, 3/12/2022
            # if 'large_loss' in request.POST:
            messages.success(request, 'Large Loss Data Updated')

        if 'payrollpremium' in request.POST or 'save_next_tab_ex_mod' in request.POST:

            if 'payrollpremium' in request.POST:
                selected = 2
            else:
                # Go to next tab
                selected = 3

            payroll_premium_list = utils.get_data_dictionaries_for_payroll_premium(
                request)

            count = 0
            for payroll in payroll_premium_list:
                if payroll['no_history'] == '':
                    payroll['no_history'] = False

                if payroll['no_history'] == 'on':
                    payroll['no_history'] = True

                if ',' in payroll['payroll_payroll']:
                    payroll['payroll_payroll'] = payroll['payroll_payroll'].replace(
                        ',', '')

                if ',' in payroll['payroll_premium']:
                    payroll['payroll_premium'] = payroll['payroll_premium'].replace(
                        ',', '')

                if payroll['payroll_payroll'] == '':
                    payroll['payroll_payroll'] = None
                else:
                    payroll['payroll_payroll'] = float(
                        payroll['payroll_payroll'])

                if payroll['payroll_premium'] == '':
                    payroll['payroll_premium'] = None
                else:
                    payroll['payroll_premium'] = int(
                        payroll['payroll_premium'])

                # Commented out as dup action, 3/6/2022, Doorn
                #account_queryset = models.AccountHistory.objects.filter(generalinfo = instance_generalinfo)
                account_queryset = acchist_queryset[count]

                account_history = models.AccountHistory.objects.filter(
                    id=account_queryset.id)
                try:
                    account_history.update(
                        policy_period=payroll['policy_period'],
                        no_history=payroll['no_history'],
                        written_premium=payroll['payroll_premium'],
                        last_modified_by=request.user.pk
                    )

                    rating_queryset = models.LossRatingValuation.objects.filter(
                        generalinfo=instance_generalinfo)
                    rating_queryset = rating_queryset[count]
                    rating_queryset = models.LossRatingValuation.objects.filter(
                        id=rating_queryset.id)

                    rating_queryset.update(
                        payroll=payroll['payroll_payroll'],

                        # Added to handle saving no history info, 3/6/22, Doorn
                        no_history=payroll['no_history']
                    )
                    count += 1
                    # Removed the following conditio as we want to show the save regardless
                    # of which Save button, 3/12/2022
                    # if 'payrollpremium' in request.POST:
                    if count == 1:
                        messages.success(
                            request, 'Premium and Payroll Data Updated')
                except Exception as e:
                    count += 1
                    messages.error(
                        request, 'Error: {} in line number {}'.format(e, count))

            acchist_queryset = models.AccountHistory.objects.filter(
                generalinfo=instance_generalinfo).order_by('policy_period')
            loss_queryset = models.LossRatingValuation.objects.filter(
                generalinfo=instance_generalinfo).order_by('policy_period')

        if 'exmodevalue_save' in request.POST or 'save_next_tab_summary' in request.POST:

            if 'exmodevalue_save' in request.POST:
                selected = 3
            else:
                # Go to next tab
                selected = 4

            exmod_vlaues = request.POST.getlist('ex_mod_value')
            exmod_year = request.POST.getlist('exmod_year')
            # Added No History variable to save
            exmod_no_history = request.POST.getlist('exmod_no_history')

            count = 0
            for value, year, no_history in zip(exmod_vlaues, exmod_year, exmod_no_history):
                queryset = models.RiskExmod.objects.filter(
                    generalinfo=instance_generalinfo)
                queryset = risk_mode_queryset[count]

                # Added try/catch blocks for capturing non-numerics
                try:
                    queryset.exmod_val = float(value)
                except:
                    queryset.exmod_val = None

                try:
                   queryset.year = int(year)
                except:
                    queryset.year = None

                queryset.no_history = no_history

                # Add update user
                queryset.last_modified_by = request.user.pk

                # Save
                queryset.save()

                count += 1
                # Removed the following conditio as we want to show the save regardless
                # of which Save button, 3/12/2022
                # if 'exmodevalue_save' in request.POST:
                if count == 1:
                    messages.success(request, 'Ex Mod Data Updated')
            risk_mode_queryset = models.RiskExmod.objects.filter(
                generalinfo=instance_generalinfo)
            risk_mode_values = utils.Risk_Ex_Mod(risk_mode_queryset)

        acchist_queryset = models.AccountHistory.objects.filter(
            generalinfo=instance_generalinfo).order_by('policy_period')
        loss_queryset = models.LossRatingValuation.objects.filter(
            generalinfo=instance_generalinfo).order_by('policy_period')
        claims_queryset = models.Claims.objects.filter(
            generalinfo=instance_generalinfo).order_by('-incurred')
        risk_mode_values = utils.Risk_Ex_Mod(risk_mode_queryset)

    # Check Large Loss for those within two years and >=$100K ---
    effective_date = instance_generalinfo.effective_date

    # Set for showing alerts on screen or not
    hasCriteria = False

    # Only check for QBE, not BH
    if instance_generalinfo.carrier == 'QBE':
        for field in claims_queryset:
            if not effective_date == None and not field.doi == None:
                if(utils.compareDate(effective_date, field.doi) == True and field.incurred >= 100000 ):
                    field.isCriteria = True
                    hasCriteria = True
                else:
                    field.isCriteria = False
            else:
                field.isCriteria = False
    
    # Note, added hasCriteria to context below
    # End Large Loss Update ---

    title = "B. History & Ex Mod"
    context = {'acc_form': acchist_form, 'loss_form': loss_form, 'selected': selected,
               'title': title, 'generalinfo': instance_generalinfo, 'unique_number': unique_number,
               'carrier': instance_generalinfo.carrier, 'claims_queryset': claims_queryset, 'hasCriteria': hasCriteria,
               'risk_mode_values': risk_mode_values, 'acchist_queryset': acchist_queryset,
               'loss_queryset': loss_queryset, 'today_date': today_date, 'named_insured': named_insured
               }

    # Calculations: Loss Rating BH
    # only calculate if loss and account history data exist
    if len(loss_queryset) or len(acchist_queryset):
        request.session['instance_generalinfo'] = instance_generalinfo.id
        wb_reader = ReadCalculations(
            user_id=1, pk=pk, carrier=instance_generalinfo.carrier)
        app = wb_reader.open_workbook()
        pid = app.pid
        try:
            wb_reader.risk_eval(request)
            wb_reader.save_and_exit()
            os.system("tskill {}".format(pid))
            # os.remove(wb_reader.outfile)
        except:
            os.system("tskill {}".format(pid))
            wb_reader.logger.exception(
                "Reading and writting was not successful")
            wb_reader.logger.error("ERROR", exc_info=True)
            #wb_reader.logger.exception('Got exception on main handler')
            wb_reader.close_logger()
            messages.warning(
                request, message="Could not remove temporary files")
        
        # account history information
        if len(acchist_queryset):
            account_history = wb_reader.account_history_data
            context['acchist_total'] = account_history.pop('totals')
            context['acchist_avg'] = account_history.pop('average all years')
            context['acchist'] = account_history.values()

        # loss information
        if len(loss_queryset):
            loss_rating = wb_reader.loss_data
            if instance_generalinfo.carrier == "BH":
                loss_total = loss_rating.pop('totals')
                loss_analysis = loss_rating.pop('analysis')
                frequency_rating = loss_rating.pop('frequency_rating')
                minimum_premium = loss_rating.pop('minimum_premium')
                context['lossrating'] = loss_rating.values()
                context['loss_total'] = loss_total
                context['loss_analysis'] = loss_analysis
                context['frequency_rating'] = frequency_rating['frequency_rating']
                context['minimum_premium'] = minimum_premium['minimum_premium']
            else:
                loss_total = loss_rating.pop('totals')
                loss_avg_qbe = loss_rating.pop('avg_all_years')
                three_yr_avg = loss_rating.pop('avg_3_years')
                minimum_premium = loss_rating.pop('minimum_premium')
                context['lossrating'] = loss_rating.values()
                context['loss_total'] = loss_total
                context['loss_avg_qbe'] = loss_avg_qbe
                context['three_yr_avg'] = three_yr_avg
                context['minimum_premium'] = minimum_premium['minimum_premium']
        
        # Calculate Estimated Rate Change
        acchist = acchist_queryset.filter(policy_period=1)
        loss = loss_queryset.filter(policy_period=1)
        if len(loss) and len(acchist):
            acchist = acchist[0]
            loss = loss[0]
            try:
                payroll = float(loss.payroll)
            except:
                payroll = None
            try:
                premium = float(acchist.written_premium)
            except:
                premium = None
            projected_payroll = float(
                instance_generalinfo.projected_payroll or 0)
            projected_premium = float(
                instance_generalinfo.projected_net_premium or 0)
            try:
                rate_change = 100 * \
                    ((projected_premium / premium) /
                     (projected_payroll / payroll) - 1)
            except:
                rate_change = 0
                
            context['rate_change'] = {
                'rate_change': rate_change,
                'premium': premium, 
                'payroll': payroll,
                'projected_payroll': projected_payroll, 
                'projected_premium': projected_premium,
                'form_type': instance_generalinfo.carrier
            }

    del request.session['instance_generalinfo']
    return render(request, "risk_eval/EditAccountHistory.html", context=context)

def EditExmodView(request, pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    riskexmod_form = forms.RiskExmodFormSet(instance=instance_generalinfo)
    acchist_queryset = models.AccountHistory.objects.filter(
        generalinfo=instance_generalinfo).order_by('policy_period')
    loss_queryset = models.LossRatingValuation.objects.filter(
        generalinfo=instance_generalinfo).order_by('policy_period')
    named_insured = instance_generalinfo.named_insured
    unique_number = instance_generalinfo.unique_number
    # calculate Estimated Rate Change
    loss_rate_table = []
    for i in range(1, 6):
        acchist = acchist_queryset.filter(policy_period=i)
        loss = loss_queryset.filter(policy_period=i)
        if len(loss) and len(acchist):
            acchist = acchist[0]
            loss = loss[0]
            payroll = float(loss.payroll)
            incurred_losses = float(acchist.incurred_losses)
            try:
                rate = incurred_losses / payroll
            except:
                rate = 0
            data = {'policy_period': i, 'loss_rate': rate,
                    'payroll': payroll,
                    'incurred_losses': incurred_losses}
        else:
            data = {'policy_period': i, 'loss_rate': "",
                    'payroll': "",
                    'incurred_losses': ""}
        loss_rate_table.append(data)

    if request.method == "POST":
        riskexmod_form = forms.RiskExmodFormSet(
            request.POST, instance=instance_generalinfo)
        if riskexmod_form.is_valid():
            riskexmod_form.save()
            messages.success(request, "Saved Risk Exmod")
            return redirect('EditExmod', pk=pk)
        else:
            riskexmod_form = forms.RiskExmodFormSet(
                request.POST, instance=instance_generalinfo)

    title = "B. Exmod"
    context = {'title': title, 'generalinfo': instance_generalinfo,
               'carrier': instance_generalinfo.carrier,
               'form_title': title,
               'riskexmod_form': riskexmod_form,
               'loss_rate_table': loss_rate_table,
               'named_insured': named_insured,
               'unique_number': unique_number
               }
    return render(request, "risk_eval/EditExmod.html", context=context)

def EditRisk(request, pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    named_insured = instance_generalinfo.named_insured
    unique_number = instance_generalinfo.unique_number
    instance_risk = models.RiskHeader.objects.filter(
        generalinfo=instance_generalinfo)
    if len(instance_risk):
        instance_risk = instance_risk[0]
    risk_form = forms.RiskForm(instance=instance_risk or None)
    # if this a new risk eval form, a risk header instance will not exist so the query will be zero;
    # therefore, if it's empty, replace it with `None`
    # if it's not empty, then get the item out of the query

    if request.method == "POST":
        risk_form = forms.RiskForm(
            request.POST, instance=instance_risk or None)

        if risk_form.is_valid():
            instance = risk_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab last update by
            instance.last_modified_by = request.user.pk

            # Save data
            instance.save()
            messages.success(request, "Saved Risk Characteristics")
            return redirect("EditSectionC", pk=pk)

    title = "C. Risk Characteristics"
    form_title = "Risk Characteristics"
    context = {'risk_form': risk_form,
               'title': title, 'form_title': form_title,
               'generalinfo': instance_generalinfo,
               'named_insured': named_insured,
               'unique_number': unique_number
               }
    return render(request, "risk_eval/EditRisk.html", context=context)

def EditChecklist(request, pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    named_insured = instance_generalinfo.named_insured
    unique_number = instance_generalinfo.unique_number
    instance_checklist = models.Checklist.objects.filter(
        generalinfo=instance_generalinfo)
    # if this a new risk eval form, a checklist instance will not exist so the query will be zero;
    # therefore, if it's empty, replace it with `None`
    # if it's not empty, then get the item out of the query
    if len(instance_checklist):
        instance_checklist = instance_checklist[0]
    checklist_form = forms.ChecklistForm(instance=instance_checklist or None)

    if request.method == "POST":
        checklist_form = forms.ChecklistForm(
            request.POST, instance=instance_checklist or None)

        if checklist_form.is_valid():
            instance = checklist_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab last update by
            instance.last_modified_by = request.user.pk

            # Save the data
            instance.save()
            messages.success(request, "Saved checklist")
            return redirect("EditSectionD", pk=pk)
        else:
            checklist_form = forms.ChecklistForm(request.POST,
                                                 instance=instance_checklist or None)
    
    print(checklist_form)

    title = "D. Checklist"
    form_title = "Checklist"
    context = {'checklist_form': checklist_form,
               'title': title, 'form_title': form_title,
               'generalinfo': instance_generalinfo,
               'named_insured': named_insured,
               'unique_number': unique_number
               }
    return render(request, "risk_eval/EditChecklist.html", context=context)

"""
F. Underwriter's Analysis, Comments and Pricing Recommendations
"""

def EditComments(request, pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    named_insured = instance_generalinfo.named_insured
    unique_number = instance_generalinfo.unique_number
    instance_comments = models.Comments.objects.filter(
        generalinfo=instance_generalinfo)
    carrier = instance_generalinfo.carrier
    # if this a new risk eval form, a checklist instance will not exist so the query will be zero;
    # therefore, if it's empty, replace it with `None`
    # if it's not empty, then get the item out of the query
    if len(instance_comments):
        instance_comments = instance_comments[0]
        ee_drivers = instance_comments.ee_drivers
        owner_ops = instance_comments.owner_ops
    else:
        ee_drivers = None
        owner_ops = None

    comments_form = forms.CommentsForm(instance=instance_comments or None)
    # set the referral field's value and label
    comments_form.set_referral_field(carrier, ee_drivers, owner_ops)

    if request.method == "POST":
        comments_form = forms.CommentsForm(request.POST,
                                           instance=instance_comments or None)

        if comments_form.is_valid():
            instance = comments_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab last update by
            instance.last_modified_by = request.user.pk

            # Save the data
            instance.save()
            messages.success(request, "Comments Saved")
            return redirect("EditSectionF", pk=pk)
        else:
            comments_form = forms.CommentsForm(request.POST,
                                               instance=instance_comments or None)

    title = "F. Underwriter's Analysis"
    form_title = "Underwriter's Analysis, Comments & Pricing Recommendations"
    context = {'comments_form': comments_form, 'form_title': form_title,
               'title': title, 'generalinfo': instance_generalinfo,
               'company': 'REMOVE THIS',
               'named_insured': named_insured,
               'unique_number': unique_number
               }
    return render(request, "risk_eval/EditComments.html", context=context)

"""
G. Claim Details
"""

def EditClaimDetails(request, pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    named_insured = instance_generalinfo.named_insured
    unique_number = instance_generalinfo.unique_number
    if instance_generalinfo.carrier == 'QBE':
        is_qbe = True
    else:
        is_qbe = False

    instance_evalunderwriter = models.EvalUnderwriter.objects.filter(
        generalinfo=instance_generalinfo)
    # if this a new risk eval form, a risk header instance will not exist so the query will be zero;
    # therefore, if it's empty, replace it with `None`
    # if it's not empty, then get the item out of the query
    if len(instance_evalunderwriter):
        instance_evalunderwriter = instance_evalunderwriter[0]

    underwriter_form = forms.EvalUnderwriterForm(
        instance=instance_evalunderwriter or None)
    claims_form = forms.ClaimsFormSet(instance=instance_generalinfo)

    if request.method == "POST":
        underwriter_form = forms.EvalUnderwriterForm(
            request.POST, instance=instance_evalunderwriter or None)

       # Moved Claims to new Section B, Doorn, 2/27/2022
        """ claims_form = forms.ClaimsFormSet(
            request.POST, instance=instance_generalinfo) """

        if underwriter_form.is_valid():
            instance = underwriter_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab last update by
            instance.last_modified_by = request.user.pk

            # Save the data
            instance.save()
            messages.success(request, "Referral Details Saved")
        else:
            messages.error(request, "Fix Referral entry errors")

        # Moved Claims to new Section B, Doorn, 2/27/2022
        # if claims_form.is_valid():
        #     # after the form set saves, it returns a list of instances
        #     # from which you can add in the user info (and anything else)
        #     claims_list = claims_form.save()
        #     for instance in claims_list:
        #         instance.last_modified_by = request.user.pk
        #         instance.save()
        #     messages.success(request, "Saved claims")
        # else:
        #     messages.error(request, "Fix Large Loss entry errors")

        # Removed second part of below as not used here, moved to new Section B, Doorn, 2/27/2022
        # and claims_form.is_valid():
        if underwriter_form.is_valid():
            return redirect("EditSectionG", pk=pk)

    # Removed 'claims_form': claims_for, as not needed here anymore, Doorn, 2/27/2022
    title = "G. Referral Details"
    form_title1 = "Referral Details"
    form_title2 = "Large Loss Details"
    context = {'underwriter_form': underwriter_form,
               # 'claims_form': claims_form,
               'form_title1': form_title1, 'form_title2': form_title2,
               'title': title, 'generalinfo': instance_generalinfo,
               'company': 'REMOVE THIS', 'is_qbe': is_qbe,
               'named_insured': named_insured,
               'unique_number': unique_number}
    return render(request, "risk_eval/EditClaimDetails.html", context=context)

"""
H. MIA Notes
"""

def EditNotes(request, pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)

    named_insured = instance_generalinfo.named_insured
    unique_number = instance_generalinfo.unique_number

    # query the data for forms

    instance_notes = models.Notes.objects.filter(
        generalinfo=instance_generalinfo)
    instance_renewaltarget = models.RenewalTargetRateChange.objects.filter(
        generalinfo=instance_generalinfo)
    instance_actualrenewal = models.ActualRenewalRateChange.objects.filter(
        generalinfo=instance_generalinfo)

    # if this a new risk eval form, a checklist instance will not exist so the query will be zero;
    # therefore, if it's empty, replace it with `None`
    # if it's not empty, then get the item out of the query
    if len(instance_notes):
        instance_notes = instance_notes[0]

    if len(instance_renewaltarget):
        instance_renewaltarget = instance_renewaltarget[0]

    if len(instance_actualrenewal):
        instance_actualrenewal = instance_actualrenewal[0]

    # Set notes form
    notes_form = forms.NotesForm(instance=instance_notes or None)

    # Set renewal target form
    renewaltarget_form = forms.RenewalTargetForm(
        instance=instance_renewaltarget or None)
    
    # Calculate fields to show on form
    if instance_renewaltarget != None:
        renewal_rate_increase = qbe.renewal_target_rate_increase(
                instance_renewaltarget)
    else:
        renewal_rate_increase = None

    # Set actual renewal form
    actualrenewal_form = forms.ActualRenewalForm(
        instance=instance_actualrenewal or None)
 
    # Calculate fields to show on form
    if instance_actualrenewal != None:
        actual_renewal_rate_change, ren_adj_rate, exp_adj_rate = qbe.actual_renewal_rate_increase(
            instance_actualrenewal)
    else:
        actual_renewal_rate_change, ren_adj_rate, exp_adj_rate = None
    
    if request.method == "POST":
        notes_form = forms.NotesForm(request.POST,
                                     instance=instance_notes or None)

        renewaltarget_form = forms.RenewalTargetForm(request.POST,
                                                     instance=instance_renewaltarget or None)
        
        actualrenewal_form = forms.ActualRenewalForm(request.POST,
                                                     instance=instance_actualrenewal or None)

        if notes_form.is_valid():
            instance = notes_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab user that updated
            instance.last_modified_by = request.user.pk

            # Save the data
            instance.save()

            messages.success(request, "Notes Saved")
            instance_notes = models.Notes.objects.get(pk=instance.pk)
        else:
            notes_form = forms.NotesForm(request.POST,
                                         instance=instance_notes or None)
            messages.error(request, "Fix Notes entry errors")

        if renewaltarget_form.is_valid():
            instance = renewaltarget_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Calculate fields to show on form
            renewal_rate_increase = qbe.renewal_target_rate_increase(
                instance)

            # Grab user that updated
            instance.last_modified_by = request.user.pk

            instance.save()
            messages.success(request, "Renewal Target Rate Change Saved")
            instance_renewaltarget = models.RenewalTargetRateChange.objects.get(
                pk=instance.pk)
        else:
            renewaltarget_form = forms.RenewalTargetForm(request.POST,
                                                         instance=instance_renewaltarget or None)
            messages.error(request, "Fix Renewal Target entry errors")

        if actualrenewal_form.is_valid():
            instance = actualrenewal_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab user that updated
            instance.last_modified_by = request.user.pk

            # Calculate fields to show on form
            actual_renewal_rate_change, ren_adj_rate, exp_adj_rate = qbe.actual_renewal_rate_increase(
                instance)   

            instance.save()
            messages.success(request, "Actual Renewal Rate Change Saved")
            instance_actualrenewal = models.ActualRenewalRateChange.objects.get(
                pk=instance.pk)
        else:
            actualrenewal_form = forms.ActualRenewalForm(request.POST,
                                                         instance=instance_actualrenewal or None)
            messages.error(
                request, "Fix Actual Renewal Rate Change entry errors")

        if notes_form.is_valid() and renewaltarget_form.is_valid() and actualrenewal_form.is_valid():
            return redirect('EditSectionH', pk=instance_generalinfo.id)

    title = "H. MIA Notes"
    form_title = "Notes"

    context = {'notes_form': notes_form, 'title': title, 'form_title': form_title,
               'generalinfo': instance_generalinfo,
               'renewaltarget_form': renewaltarget_form,
               'actualrenewal_form': actualrenewal_form,
               'named_insured': named_insured,
               'unique_number': unique_number,
               'renewal_rate_increase': renewal_rate_increase,
               'actual_renewal_rate_change': actual_renewal_rate_change,
               'ren_adj_rate': ren_adj_rate,
               'exp_adj_rate': exp_adj_rate
               }
    return render(request, "risk_eval/EditNotes.html", context=context)

def ReviewRiskEval(request, pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    form = forms.ReviewRiskForm()
    context = {'title': 'Review Risk Eval', 'form': form}

    if request.GET:
        form = forms.ReviewRiskForm(request.GET)
        warnings = []
        # <QueryDict: {'section': ['GeneralInfo']}>
        model_name = request.GET['section']
        model = getattr(models, model_name)
        if model_name == 'GeneralInfo':
            instance = instance_generalinfo
        elif model_name in ('AccountHistory', 'Claims', 'LossRatingValuation'):
            qset = model.objects.filter(generalinfo=instance_generalinfo)
            if qset:
                for i, instance in enumerate(qset, 1):
                    data = instance.__dict__
                    for name, val in data.items():
                        if not val:
                            message = "({}) Field {} is empty".format(
                                i, instance)
                            warnings.append(message)
                            break
        else:
            qset = model.objects.filter(generalinfo=instance_generalinfo)
            if qset:
                instance = qset[0]
                data = instance.__dict__
                for name, val in data.items():
                    if not val:
                        message = "Field {} is empty".format(name)
                        warnings.append(message)
        context = {'title': 'Review -- {}'.format(model_name),
                   'form': form, 'warnings': warnings,
                   'company': 'REMOVE THIS'}
    return render(request, "risk_eval/ReviewRiskEval.html", context=context)

class RestView(viewsets.ModelViewSet):
    queryset = models.GeneralInfo.objects.all()
    serializer_class = GeneralInfoSerializer

"""
Underwriter Special Notes (Logging)
"""

def EditLoggingNotes(request, pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    named_insured = instance_generalinfo.named_insured
    unique_number = instance_generalinfo.unique_number
    instance_header = models.LoggingHeader.objects.filter(
        generalinfo=instance_generalinfo)
    instance_categories = models.LoggingExposureCategories.objects.filter(
        generalinfo=instance_generalinfo)
    avg_score = 0

    if len(instance_header):
        instance_header = instance_header[0]

    if len(instance_categories):
        instance_categories = instance_categories[0]
        avg_score = helper.calculate_score(
            instance_categories, reference=helper.logging_ref)

    if request.method == "POST":
        header_form = forms.LoggingHeaderForm(request.POST,
                                              instance=instance_header or None)
        categories_form = forms.LoggingExposureForm(request.POST,
                                                    instance=instance_categories or None)

        if header_form.is_valid():
            instance = header_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab user that updated
            instance.last_modified_by = request.user.pk

            instance.save()
            messages.success(request, "Logging Header Saved")

        if categories_form.is_valid():
            instance = categories_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab user that updated
            instance.last_modified_by = request.user.pk

            instance.save()
            messages.success(request, "Logging Categories Saved")

        return redirect("LoggingNotes", pk=pk)

    header_form = forms.LoggingHeaderForm(instance=instance_header or None)
    categories_form = forms.LoggingExposureForm(
        instance=instance_categories or None)
    title = "Logging"
    category_title = "Logging Exposure Categories"
    context = {'header_form': header_form, 'categories_form': categories_form,
               'title': title, 'category_title': category_title,
               'generalinfo': instance_generalinfo,
               'company': 'REMOVE THIS',
               'avg_score': avg_score,
               'previous_section': 'EditSectionH',
               'next_section': 'MechanicalNotes',
               'named_insured': named_insured,
               'unique_number': unique_number,
               'prev_section': 'Notes',
               'nxt_section': 'Wood Mechanical'
               }
    return render(request, "risk_eval/EditUnderwriterSpecialNotes.html", context=context)

"""
Underwriter Special Notes (Wood Mechanical)
"""

def EditMechanicalNotes(request, pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    named_insured = instance_generalinfo.named_insured
    unique_number = instance_generalinfo.unique_number
    instance_header = models.MechanicalHeader.objects.filter(
        generalinfo=instance_generalinfo)
    instance_categories = models.MechanicalCategories.objects.filter(
        generalinfo=instance_generalinfo)
    avg_score = 0

    if len(instance_header):
        instance_header = instance_header[0]

    if len(instance_categories):
        instance_categories = instance_categories[0]
        avg_score = helper.calculate_score(
            instance_categories, reference=helper.mechanical_ref)

    if request.method == "POST":
        header_form = forms.MechanicalHeaderForm(request.POST,
                                                 instance=instance_header or None)
        categories_form = forms.MechanicalCategoriesForm(request.POST,
                                                         instance=instance_categories or None)

        if header_form.is_valid():
            instance = header_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab user that updated
            instance.last_modified_by = request.user.pk

            instance.save()
            messages.success(request, "Mechanical Header Saved")

        if categories_form.is_valid():
            instance = categories_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab user that updated
            instance.last_modified_by = request.user.pk

            instance.save()
            messages.success(request, "Mechanical Categories Saved")

        return redirect("MechanicalNotes", pk=pk)

    header_form = forms.MechanicalHeaderForm(instance=instance_header or None)
    categories_form = forms.MechanicalCategoriesForm(
        instance=instance_categories or None)
    title = "Wood Mechanical"
    category_title = "Wood Mechanical Categories"
    context = {'header_form': header_form, 'categories_form': categories_form,
               'title': title, 'category_title': category_title,
               'generalinfo': instance_generalinfo,
               'company': 'REMOVE THIS',
               'avg_score': avg_score,
               'previous_section': 'LoggingNotes',
               'next_section': 'WoodManualNotes',
               'named_insured': named_insured,
               'unique_number': unique_number,
               'prev_section': 'Logging',
               'nxt_section': 'Wood Manual'
               }
    return render(request, "risk_eval/EditUnderwriterSpecialNotes.html", context=context)

"""
Underwriter Special Notes (Wood Manual)
"""

def EditWoodManualNotes(request, pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    named_insured = instance_generalinfo.named_insured
    unique_number = instance_generalinfo.unique_number
    instance_header = models.WoodManualHeader.objects.filter(
        generalinfo=instance_generalinfo)
    instance_categories = models.WoodMechanicalCategories.objects.filter(
        generalinfo=instance_generalinfo)
    avg_score = 0

    if len(instance_header):
        instance_header = instance_header[0]

    if len(instance_categories):
        instance_categories = instance_categories[0]
        avg_score = helper.calculate_score(
            instance_categories, reference=helper.wood_manual_ref)

    if request.method == "POST":
        header_form = forms.WoodManualHeaderForm(request.POST,
                                                 instance=instance_header or None)
        categories_form = forms.WoodMechanicalCategoriesForm(request.POST,
                                                             instance=instance_categories or None)

        if header_form.is_valid():
            instance = header_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab user that updated
            instance.last_modified_by = request.user.pk

            instance.save()
            messages.success(request, "Wood Manual Header Saved")

        if categories_form.is_valid():
            instance = categories_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab user that updated
            instance.last_modified_by = request.user.pk

            instance.save()
            messages.success(request, "Wood Mechanical Categories Saved")

        return redirect("WoodManualNotes", pk=pk)

    header_form = forms.WoodManualHeaderForm(instance=instance_header or None)
    categories_form = forms.WoodMechanicalCategoriesForm(
        instance=instance_categories or None)
    title = "Wood Manual"
    category_title = "Wood Mechanical Categories"
    context = {'header_form': header_form, 'categories_form': categories_form,
               'title': title, 'category_title': category_title,
               'generalinfo': instance_generalinfo,
               'company': 'REMOVE THIS',
               'avg_score': avg_score,
               'previous_section': 'MechanicalNotes',
               'named_insured': named_insured,
               'unique_number': unique_number,
               'prev_section': 'Wood Mechanical',
               }
    return render(request, "risk_eval/EditUnderwriterSpecialNotes.html", context=context)

def calc_final_score(query):
    """Calculate Final Score for Score tab"""
    class_fit = query.class_fit or 0
    class_fit_score = round(class_fit * 0.5, 2)

    wages = query.wages or 0
    wages_score = round(wages * 0.15, 2)

    safety_and_controls = query.safety_and_controls or 0
    safety_and_controls_score = round(safety_and_controls * 0.20, 2)

    management = query.management or 0
    management_score = round(management * 0.15, 2)

    final_score = round(class_fit_score + wages_score +
                        safety_and_controls_score + management_score, 2)
    score_results = {'class_fit_score': class_fit_score, 'wages_score': wages_score,
                     'safety_and_controls_score': safety_and_controls_score,
                     'management_score': management_score, 'final_score': final_score}
    return score_results

def EditScore(request, pk):
    instance_generalinfo = models.GeneralInfo.objects.get(pk=pk)
    named_insured = instance_generalinfo.named_insured
    unique_number = instance_generalinfo.unique_number
    instance_score = models.Score.objects.filter(
        generalinfo=instance_generalinfo)
    # if this a new risk eval form, a checklist instance will not exist so the query will be zero;
    # therefore, if it's empty, replace it with `None`
    # if it's not empty, then get the item out of the query
    if len(instance_score):
        instance_score = instance_score[0]
    comments_form = forms.ScoreForm(instance=instance_score or None)

    if request.method == "POST":
        score_form = forms.ScoreForm(request.POST,
                                     instance=instance_score or None)

        if score_form.is_valid():
            instance = score_form.save(commit=False)
            instance.generalinfo_id = instance_generalinfo.id

            # Grab last user info
            instance.last_modified_by = request.user.pk

            # Save the data
            instance.save()
            messages.success(request, "MIA Score Saved")
            return redirect("Score", pk=pk)
        else:
            comments_form = forms.ScoreForm(request.POST,
                                            instance=instance_score or None)
            messages.error(request, "Fix the entry errors")

    title = "MIA Score"
    context = {'score_form': comments_form,
               'title': title,
               'generalinfo': instance_generalinfo,
               'named_insured': named_insured,
               'unique_number': unique_number}
    if isinstance(instance_score, models.Score):
        context['instance'] = instance_score
        context['score_results'] = calc_final_score(instance_score)
    return render(request, "risk_eval/EditScore.html", context=context)

class DeleteRiskEval(DeleteView):
    model = models.GeneralInfo
    template_name = 'risk_eval/deleteview.html'
    success_url = '/risk_eval/list/'
    queryset = models.GeneralInfo.objects.all()

    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(models.GeneralInfo, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
