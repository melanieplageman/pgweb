from django.db import models
from django.contrib.auth.models import User

from pgweb.core.models import Organisation


class ContributorType(models.Model):
    typename = models.CharField(max_length=32, null=False, blank=False)
    sortorder = models.IntegerField(null=False, default=100)
    extrainfo = models.TextField(null=True, blank=True)
    detailed = models.BooleanField(null=False, default=True)
    showemail = models.BooleanField(null=False, default=True)

    purge_urls = ('/community/contributors/', )

    def __str__(self):
        return self.typename

    class Meta:
        ordering = ('sortorder',)


class Contributor(models.Model):
    ctype = models.ForeignKey(ContributorType, on_delete=models.CASCADE, verbose_name='Contributor Type')
    lastname = models.CharField(max_length=100, null=False, blank=False)
    firstname = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(null=False, blank=True)
    company = models.CharField(max_length=100, null=True, blank=True)
    companyurl = models.URLField(max_length=100, null=True, blank=True, verbose_name='Company URL')
    location = models.CharField(max_length=100, null=True, blank=True)
    contribution = models.TextField(null=True, blank=True,
                                    help_text='This description is currently used for major contributors only')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    send_notification = True
    purge_urls = ('/community/contributors/', )

    def __str__(self):
        return "%s %s" % (self.firstname, self.lastname)

    class Meta:
        ordering = ('lastname', 'firstname',)


class ContributorBadge(models.Model):
    org = models.ForeignKey(Organisation, null=False, blank=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)

    purge_urls = ('/community/contributors/', )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('org', 'name',)
        unique_together = (
            ('org', 'name',),
        )


class ContributorBadgeAward(models.Model):
    contributor = models.ForeignKey(Contributor, null=False, blank=False, on_delete=models.CASCADE)
    badge = models.ForeignKey(ContributorBadge, null=False, blank=False, on_delete=models.CASCADE)
    awarded_date = models.DateField(null=False, blank=False, auto_now_add=True)
    active = models.BooleanField(null=False, blank=False, default=True)

    purge_urls = ('/community/contributors/', )

    def __str__(self):
        return "%s - %s" % (self.contributor, self.badge)

    class Meta:
        ordering = ('contributor', 'awarded_date',)
        unique_together = (
            ('contributor', 'badge',),
        )
        verbose_name = 'Contributor Badge Award'
        verbose_name_plural = 'Contributor Badge Awards'


class ContributorBadgeRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    contributor = models.ForeignKey(Contributor, null=True, blank=True, on_delete=models.CASCADE,
                                    help_text='If you have a contributor profile, select it here')
    badge = models.ForeignKey(ContributorBadge, null=False, blank=False, on_delete=models.CASCADE)
    justification = models.TextField(null=False, blank=False,
                                     help_text='Explain why you should receive this badge')
    status = models.CharField(max_length=20, null=False, blank=False,
                             default=STATUS_PENDING, choices=STATUS_CHOICES)
    requested_date = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    reviewed_date = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='badge_requests_reviewed')
    review_notes = models.TextField(null=True, blank=True)

    purge_urls = ('/community/contributors/', )

    def __str__(self):
        return "%s - %s (%s)" % (self.user.username, self.badge.name, self.status)

    class Meta:
        ordering = ('-requested_date',)
        verbose_name = 'Badge Request'
        verbose_name_plural = 'Badge Requests'
