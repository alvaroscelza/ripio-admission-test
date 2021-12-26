from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=30)


class Currency(models.Model):
    name = models.CharField(max_length=30)


class AmountOfCurrency(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    owner = models.ForeignKey(Person, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)

    class Meta:
        unique_together = ('currency', 'owner')


class LogLine(models.Model):
    actor = models.ForeignKey(Person, on_delete=models.CASCADE)
    date = models.DateTimeField()
    text = models.CharField(max_length=200)
