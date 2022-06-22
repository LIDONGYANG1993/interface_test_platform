from django.db import models
from django.db.models import QuerySet


class SoftDeleteQuerySet(QuerySet):
    def delete(self):
        return super(SoftDeleteQuerySet, self).update(is_deleted=True)

    def hard_delete(self):
        return super(SoftDeleteQuerySet, self).delete()


class Manager(models.Manager):
    """支持软删除"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model).filter(is_deleted=False)

    def get_queryset_in_deleted(self):
        return SoftDeleteQuerySet(self.model).filter()


class PropertyManager(Manager):
    pass
