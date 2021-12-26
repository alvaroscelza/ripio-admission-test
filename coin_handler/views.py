from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.utils.datetime_safe import date

from coin_handler.models import AmountOfCurrency, Person, LogLine, Currency


def index(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    person_currencies = AmountOfCurrency.objects.filter(owner=person_id)
    context = {
        'person': person,
        'person_currencies': person_currencies,
    }
    return render(request, 'coin_handler/index.html', context)


def log(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    user_log_lines = LogLine.objects.filter(actor=person_id)
    context = {
        'person': person,
        'user_log_lines': user_log_lines,
    }
    return render(request, 'coin_handler/log.html', context)


def send_cash(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    person_currencies = AmountOfCurrency.objects.filter(owner=person_id)
    possible_addresses = Person.objects.exclude(id=person_id)
    context = {
        'person': person,
        'person_currencies': person_currencies,
        'possible_addresses': possible_addresses,
    }
    return render(request, 'coin_handler/send_cash.html', context)


def process_cash_sending(request, person_id):
    person = get_object_or_404(Person, pk=person_id)
    person_currencies = AmountOfCurrency.objects.filter(owner=person_id)
    possible_addresses = Person.objects.exclude(id=person_id)
    addressee_id = request.POST.get('addressee', False)
    currency_id = request.POST.get('currency', False)
    amount = request.POST.get('amount', False)
    currency = get_object_or_404(Currency, pk=currency_id)
    addressee = get_object_or_404(Person, pk=addressee_id)

    error_message = False
    if not amount:
        error_message = "Please, set an amount to send."
    if not currency_id:
        error_message = "Currency not set. Again... good try :)"
    if not addressee_id:
        error_message = "Addressee not set. Good try though :)"
    if error_message:
        context = {
            'person': person,
            'person_currencies': person_currencies,
            'result_message': error_message,
            'possible_addresses': possible_addresses,
        }
        return render(request, 'coin_handler/send_cash.html', context)

    amount = int(amount)

    with transaction.atomic():
        try:
            addressee_currency_to_augment = AmountOfCurrency.objects.select_for_update()\
                .get(currency=currency_id, owner=addressee_id)
            addressee_currency_to_augment.amount += amount
        except AmountOfCurrency.DoesNotExist:
            addressee_currency_to_augment = AmountOfCurrency.objects.create(currency=currency, owner=addressee,
                                                                            amount=amount)

        sender_currency_to_diminish = get_object_or_404(AmountOfCurrency.objects.select_for_update(),
                                                        currency=currency_id, owner=person_id)
        sender_currency_to_diminish.amount -= amount
        if sender_currency_to_diminish.amount < 0:
            context = {
                'person': person,
                'person_currencies': person_currencies,
                'result_message': "You've not enough of that currency.",
                'possible_addresses': possible_addresses,
            }
            return render(request, 'coin_handler/send_cash.html', context)

        addressee_currency_to_augment.save()
        sender_currency_to_diminish.save()

    text = 'Sent %s %s to %s.' % (amount, currency.name, addressee.name)
    LogLine.objects.create(actor=person, date=date.today(), text=text)
    text = 'Received %s %s from %s.' % (amount, currency.name, person.name)
    LogLine.objects.create(actor=addressee, date=date.today(), text=text)

    context = {
        'person': person,
        'person_currencies': person_currencies,
        'result_message': "Success!",
        'possible_addresses': possible_addresses,
    }
    return render(request, 'coin_handler/send_cash.html', context)


def login(request):
    people = Person.objects.all()
    context = {'people': people, }
    return render(request, 'coin_handler/login.html', context)


def process_login(request):
    person_id = request.POST.get('person', False)
    if not person_id:
        people = Person.objects.all()
        context = {'people': people,
                   'result_message': 'You must select a person', }
        return render(request, 'coin_handler/login.html', context)
    return index(request, person_id)
