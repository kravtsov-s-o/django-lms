# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from school.models import Teacher, Student


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Создание или обновление связанных моделей Teacher или Student на основе роли school_role.
    """
    if hasattr(instance, 'is_from_user_form') and instance.is_from_user_form:
        if created:
            if instance.school_role == User.SchoolRole.TEACHER:
                Teacher.objects.create(user=instance)
            elif instance.school_role == User.SchoolRole.STUDENT:
                Student.objects.create(user=instance)
        else:
            if instance.school_role == User.SchoolRole.TEACHER:
                Student.objects.filter(user=instance).delete()
                Teacher.objects.get_or_create(user=instance)
            elif instance.school_role == User.SchoolRole.STUDENT:
                Teacher.objects.filter(user=instance).delete()
                Student.objects.get_or_create(user=instance)
            else:
                Student.objects.filter(user=instance).delete()
                Teacher.objects.filter(user=instance).delete()
