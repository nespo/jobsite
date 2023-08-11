from django.views.generic import TemplateView
from company.models import PricingPlan, CompanyInfo
from pages.views import UserInfo
from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
import random
from django.db.models import Q
import requests
import json

class About(TemplateView):
    template_name = "company/about.html"
class Services(TemplateView):
    template_name = "company/services.html"
class Team(TemplateView):
    template_name = "company/team.html"

class Pricing(TemplateView):
    template_name = "company/pricing.html"

    def get_context_data(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            if request.user.is_company:
                pricing_plan = PricingPlan.objects.filter(Q(for_company=1) & ~Q(price=0)).all()
                context["profile_info"] = CompanyInfo.objects.get(user_id=request.user.id)
            else:
                pricing_plan = PricingPlan.objects.filter(Q(for_company=0) & ~Q(price=0)).all()
                context["profile_info"] = UserInfo.objects.get(user_id=request.user.id)
        except:
            pricing_plan = PricingPlan.objects.filter(~Q(price=0)).all()

        context['pricing_plan'] = pricing_plan

        return context
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request)
        return render(request, self.template_name, context)

class CancelPlan(TemplateView):
    template_name = "company/pricing.html"

    def get_context_data(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        if request.user.is_company:
            pricing_plan = PricingPlan.objects.filter(Q(for_company=1) & ~Q(price=0)).all()
            company = CompanyInfo.objects.get(user_id=request.user.id)
            company.purchased_package_id = PricingPlan.objects.get(id=4)
            company.job_post_count = 50
            company.save()
            context["profile_info"] = CompanyInfo.objects.get(user_id=request.user.id)
        else:
            pricing_plan = PricingPlan.objects.filter(Q(for_company=0) & ~Q(price=0)).all()
            user = UserInfo.objects.get(user_id=request.user.id)
            user.purchased_package_id = PricingPlan.objects.get(id=5)
            user.job_apply_count = 50
            user.save()
            context["profile_info"] = UserInfo.objects.get(user_id=request.user.id)
        context['pricing_plan'] = pricing_plan

        return context
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request)

        return render(request, self.template_name, context)

class PricingOrders(TemplateView):
    template_name = "company/pricing.html"
    def post(self, request, *args, **kwargs):
        given = request.POST.get("provided_money")
        url = "https://api.sandbox.paypal.com/v1/oauth2/token"
        payload='grant_type=client_credentials'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'EHBTNxY7_0ADEwBUMjx_S-vGcDbUWOQP1vCMYKIO5XB1kLJwmULvqB1RdQKb9e-NwetYUDjaCrowkExa'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        abc = response.json()



        url = "https://api-m.sandbox.paypal.com/v1/payments/payouts"
        payload = json.dumps({
        "sender_batch_header": {},
        "items": [
            {
            "recipient_type": "EMAIL",
            "amount": {
                "value": given,
                "currency": "USD"
            },
            "note": "Thanks for your patience!",
            "receiver": "signalsysten@gmail.com"
            }
        ]
        })

        headers = {
        'Content-Type': 'application/json',
        'PayPal-Request-Id': 'a32871ad-76d2-4236-a50d-472e48816ad4',
        'Authorization': f"Bearer {abc['access_token']}"
        }

        response = requests.request("POST", url, headers=headers, data=payload)




class PaypalFormView(FormView):
    template_name = 'company/process_payment.html'

    def post(self, request, *args, **kwargs):
        amount = request.POST.get("amount")
        item_name = request.POST.get("item_name")
        request.session["pricing_plan"] = PricingPlan.objects.get(id=request.POST.get("pricing_plan")).id
        print(amount, item_name)
        invoice_no = random.randint(9999999, 999999999)
        host = request.get_host()
        paypal_dict = {
            "cmd": "_xclick-subscriptions",
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "a3": float("%.2f"%float(amount)),                      # monthly price
            "p3": 1,                           # duration of each unit (depends on unit)
            "t3": "M",                         # duration unit ("M for Month")
            "src": "1",                        # make payments recur
            "sra": "1",                        # reattempt payment on payment error
            "no_note": "1",                    # remove extra notes (optional)
            "item_name": item_name,
            'currency_code': 'USD',
            "invoice_no": invoice_no,
            'notify_url': 'http://{}{}'.format(host,
                                               reverse('paypal-ipn')),
            'return_url': 'http://{}{}'.format(host,
                                               reverse('payment_done')),
            'cancel_return': 'http://{}{}'.format(host,
                                                  reverse('payment_cancelled')),

        }

        form = PayPalPaymentsForm(initial=paypal_dict, button_type="subscribe")
        return JsonResponse({'form': form.render()})


def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    print(sender)
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        print("completed")
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:

            return

        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.

        # Undertake some action depending upon `ipn_obj`.
        if ipn_obj.item_name == "premium_plan":
            price = ""
        else:
            price = ""

        if ipn_obj.mc_gross == price and ipn_obj.currency == 'USD':
            pass
    else:
        #...
        print("pass")
        pass



@csrf_exempt
def payment_done(request):
    if request.user.is_company:
        company = CompanyInfo.objects.get(user_id=request.user.id)
        company.purchased_package_id = PricingPlan.objects.get(id=request.session["pricing_plan"])
        company.job_post_count = PricingPlan.objects.get(id=request.session["pricing_plan"]).jobs_count
        company.save()
        del request.session["pricing_plan"]
    else:
        user = UserInfo.objects.get(user_id=request.user.id)
        user.purchased_package_id = PricingPlan.objects.get(id=request.session["pricing_plan"])
        user.job_apply_count = PricingPlan.objects.get(id=request.session["pricing_plan"]).jobs_count
        user.save()
        del request.session["pricing_plan"]
    valid_ipn_received.connect(show_me_the_money)
    return redirect('pricing')


@csrf_exempt
def payment_canceled(request):
    return render(request, 'company/payment_cancelled.html')


class PrivacyPolicy(TemplateView):
    template_name = "company/privacy-policy.html"
class FAQs(TemplateView):
    template_name = "company/faqs.html"



@csrf_exempt
def update_count(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        pplan = PricingPlan.objects.get(id = id)
        user = request.user
        ci_ = CompanyInfo.objects.get(user=user)
        ci_.job_post_count += pplan.jobs_count
        ci_.purchased_package = pplan
        ci_.save()        
        response_data = {'message': 'Data received and processed successfully.'}
        return JsonResponse(response_data)


