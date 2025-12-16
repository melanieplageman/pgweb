from django.shortcuts import get_object_or_404
from pgweb.util.contexts import render_pgweb

from .models import ContributorType, Contributor


def completelist(request):
    contributortypes = list(ContributorType.objects.all())
    return render_pgweb(request, 'community', 'contributors/list.html', {
        'contributortypes': contributortypes,
    })


def contributor_profile(request, username):
    # Only show profiles that are not hidden
    contributor = get_object_or_404(
        Contributor,
        user__username=username,
        hidden=False
    )
    return render_pgweb(request, 'community', 'contributors/profile.html', {
        'contributor': contributor,
    })
