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
            # Если пользователь создан, создаём соответствующую связанную модель
            if instance.school_role == 'teacher':
                Teacher.objects.create(user=instance)
            elif instance.school_role == 'student':
                Student.objects.create(user=instance)
        else:
            # Если пользователь обновляется, проверяем изменения
            if instance.school_role == 'teacher':
                # Удаляем Student, если был, и создаём Teacher
                Student.objects.filter(user=instance).delete()
                Teacher.objects.get_or_create(user=instance)
            elif instance.school_role == 'student':
                # Удаляем Teacher, если был, и создаём Student
                Teacher.objects.filter(user=instance).delete()
                Student.objects.get_or_create(user=instance)
            else:
                # Если роль None, удаляем все связанные модели
                Student.objects.filter(user=instance).delete()
                Teacher.objects.filter(user=instance).delete()
