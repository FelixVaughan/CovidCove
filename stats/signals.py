from django.db.models.signals import post_save, post_init
from django.dispatch import receiver
from stats.models import Last_update
import sys 

@receiver(post_save, sender=Last_update)
def check_time_table(sender, **kwargs): #checks to make sure that exactly one element is present in db
    if(len(sender.objects.all()) > 1):
        user_input = input("There appears to be more than one entry in 'Last_update' db. delete all but pk=1 (y/n)? ")
        if(user_input.lower() == "y"):
            problem_elements = sender.objects.filter(pk__gt=1)
            problem_elements.delete()
        else:
            print("Okie dokie. Trust you'll resolve the issue yourself :)")
            

    