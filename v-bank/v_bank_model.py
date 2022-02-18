"""
    this file is part of virtual bank application in django framework
    this is the models file which define the database tabels of application
    and is not workable standalone
    only for demonstration puposes
    
"""

from django.db import models
import random


class BasicUser(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    verification_code = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email}"


class RequestAccount(models.Model):
    pass


def get_random():
    return random.randrange(0, 99) * random.randrange(99, 9999)


# bank account
class BankAccount(models.Model):
    basic_user = models.OneToOneField(
        BasicUser,
        on_delete=models.CASCADE,
        primary_key=True,
        default=000
    )
    account_number = models.CharField(max_length=100, null=True)
    balance = models.FloatField(max_length=50, default=0.0)
    transfer_code = models.IntegerField(null=True)
    is_activated = models.BooleanField(default=False)


class Wallet(models.Model):
    basic_user = models.OneToOneField(
        BasicUser,
        on_delete=models.CASCADE,
        primary_key=True,
        default=000
    )
    private_key = models.CharField(max_length=256)
    public_key = models.CharField(max_length=256)
    addr = models.CharField(max_length=256)
    balance = models.FloatField(max_length=50, default=0.0)


# model for customer transactions
class Transactions(models.Model):
    is_transfer_amount = models.BooleanField(default=False)
    is_withdraw_amount = models.BooleanField(default=False)
    is_deposit_amount = models.BooleanField(default=False)
    is_transaction_approved = models.BooleanField(default=False)
    amount = models.FloatField(max_length=7, default=0)
    user = models.ForeignKey(BasicUser, on_delete=models.CASCADE)


# exchange rates model
class ExchangeRates(models.Model):
    basic_user = models.OneToOneField(
        BasicUser,
        on_delete=models.CASCADE,
        primary_key=True,
        default=000
    )
    usd_percent_rate = models.FloatField(max_length=5, default=0.15)


# class CurrencyRates(models.Model):
#     pass
