from django.shortcuts import render
from .push_on_rbmq import publish_to_exchange
from .tasks import *
import json
# Create your views here.

def ItemList(request):
    print("rishbahaaaaa")
    result = generate_report_task()
    publish_to_exchange(json.dumps({'a':"rishabh"}))

    print(result)

