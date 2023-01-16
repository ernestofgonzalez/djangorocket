import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from {{ cookiecutter.project_slug }}.billing.forms import UpdateBillingInformationForm
from {{ cookiecutter.project_slug }}.model_loaders import get_stripe_customer_model


@never_cache
@require_http_methods(["GET", "POST"])
@login_required
def billing_settings_view(request):
    context = {
        "current_tab": "billing",
    }

    stripe.api_key = settings.STRIPE_SECRET_KEY
    subscription = stripe.Subscription.retrieve(
        request.user.stripe_customer.stripe_subscription_id
    )

    form = UpdateBillingInformationForm(
        request.POST or None,
        initial={
            "name": None,
            "address_line_1": None,
            "address_line_2": None,
            "city": None,
            "postal_code": None,
            "country": None,
        },
    )
    context["form"] = form

    if request.method == "POST":
        if form.is_valid():
            if form.has_changed():
                pass

            return redirect("{{ cookiecutter.project_slug }}-billing:billing-settings")

    return render(request, "billing/pages/billing_settings.html", context)


@csrf_exempt
@require_GET
@login_required
def create_subscribe_checkout_view(request):
    domain_url = request.build_absolute_uri("/")[:-1]
    success = request.GET.get("success", None)
    cancel = request.GET.get("cancel", None)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            success_url=domain_url + success + "?subcription_checkout_success=true",
            cancel_url=domain_url + cancel,
            client_reference_id=request.user.uuid,
            customer=request.user.stripe_customer.stripe_customer_id,
            customer_update={
                "address": "auto",
            },
            mode="setup",
        )

        return JsonResponse({"checkout_session_id": checkout_session["id"]})
    except Exception as e:
        return JsonResponse({"error": str(e)})


@require_POST
@login_required
def cancel_subscription_view(request):
    success = request.GET.get("success", None)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    stripe.Subscription.modify(
        request.user.stripe_customer.stripe_subscription_id,
        cancel_at_period_end=True,
    )

    return redirect(success + "?" + "subcription_cancel_success=true")


@require_POST
@login_required
def reactivate_subscription_view(request):
    """
    Reactivate canceled subscription which hasn't reached
    the end of the billing period.

    Note: If the cancellation has already been processed and the
    subscription is no longer active, a new subscription is
    needed for the customer. For this case, use the `create_subscribe_checkout_view`
    endpoint.
    """
    success = request.GET.get("success", None)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    stripe_customer = request.user.stripe_customer

    subscription = stripe.Subscription.retrieve(stripe_customer.stripe_subscription_id)

    if subscription.status.canceled:
        new_subscription = stripe.Subscription.create(
            customer=stripe_customer.stripe_customer_id,
            items=[{"price": settings.STRIPE_PRICE_ID}],
            automatic_tax={"enabled": True},
        )
        stripe_customer.stripe_subscription_id = new_subscription.id
        stripe_customer.save(update_fields=["stripe_subscription_id"])
    else:
        stripe.Subscription.modify(
            subscription.id,
            cancel_at_period_end=False,
            proration_behavior="create_prorations",
            items=[
                {
                    "id": subscription["items"]["data"][0].id,
                    "price": settings.STRIPE_PRICE_ID,
                }
            ],
        )

    return redirect(success + "?" + "subcription_reactivated_success=true")


@require_POST
@login_required
def remove_current_default_payment_method_view(request):
    pass


@csrf_exempt
def stripe_webhook_view(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Retrieve setup intent
        setup_intent = stripe.SetupIntent.retrieve(session["setup_intent"])

        # Set payment method as default
        stripe.Customer.modify(
            session["customer"],
            invoice_settings={"default_payment_method": setup_intent.payment_method},
        )

        StripeCustomer = get_stripe_customer_model()
        stripe_customer = StripeCustomer.objects.get(
            stripe_customer_id=session["customer"],
        )

        subscription = stripe.Subscription.retrieve(
            stripe_customer.stripe_subscription_id
        )

        # Check if subscription is still active
        # If subscription is active do nothing
        # If subscription is not active, create new subscription for same customer.

    return HttpResponse(status=200)
