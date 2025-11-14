from django.shortcuts import get_object_or_404
from pgweb.util.contexts import render_pgweb

from .models import ContributorType, Contributor, ContributorBadgeAward


def completelist(request):
    contributortypes = list(ContributorType.objects.all())
    return render_pgweb(request, 'community', 'contributors/list.html', {
        'contributortypes': contributortypes,
    })


def profile(request, contributor_id):
    contributor = get_object_or_404(Contributor, pk=contributor_id)

    # Get all active badge awards for this contributor
    badge_awards = ContributorBadgeAward.objects.filter(
        contributor=contributor,
        active=True
    ).select_related('badge', 'badge__org').order_by('-awarded_date')

    return render_pgweb(request, 'community', 'contributors/profile.html', {
        'contributor': contributor,
        'badge_awards': badge_awards,
    })
