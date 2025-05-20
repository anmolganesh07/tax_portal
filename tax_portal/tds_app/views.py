from django.shortcuts import render

# Create your views here.
# tds_app/views.py
import csv
from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView
from .forms import TDSForm
from .utils import get_tds_due_dates

TDS_RATES = {
    '194C': 2.0,
    '194J': 10.0,
    '194H': 5.0,
    
}

class TDSCalculatorView(View):
    """
    TDS Calculator form
    """
    def get(self, request):
        form = TDSForm()
        # due_dates = get_tds_due_dates(fin_year_start=2024)
        return render(request, 'tds_app/calculator.html', {
            'form': form,
            'result': None,
            # 'due_dates': due_dates,
        })

    def post(self, request):
        form = TDSForm(request.POST)
        # due_dates = get_tds_due_dates(fin_year_start=2024)

        result = None
        if form.is_valid():
            section = form.cleaned_data['section']
            amount = form.cleaned_data['amount']
            pan_available = form.cleaned_data['pan_available']

            rate = Decimal('20.0') if pan_available == 'no' else Decimal((TDS_RATES.get(section, 0)))
            tds_amount = round(amount * (rate / Decimal('100')), 2)
            net_payable = round(amount - tds_amount, 2)

            result = {
                'rate': rate,
                'tds_amount': tds_amount,
                'net_payable': net_payable,
            }

        return render(request, 'tds_app/calculator.html', {
            'form': form,
            'result': result,
            # 'due_dates': due_dates,
        })

class DownloadReportView(View):
    """
    View To Download Report
    """
    def get(self, request):
        section = request.GET.get('section')
        amount = request.GET.get('amount')
        pan = request.GET.get('pan')
        rate = request.GET.get('rate')
        tds = request.GET.get('tds')
        net = request.GET.get('net')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tds_report.csv"'

        writer = csv.writer(response)
        writer.writerow(['TDS Section', 'Amount Paid', 'PAN Available', 'TDS Rate (%)', 'TDS Amount', 'Net Payable'])
        writer.writerow([section, amount, pan, rate, tds, net])

        return response

class DueDateTrackerView(TemplateView):
    template_name = 'tds_app/due_dates.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['due_dates'] = get_tds_due_dates(fin_year_start=2024)
        return context
