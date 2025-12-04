from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from pgweb.util.contexts import render_pgweb

from .models import ContributorType, Contributor, ContributorBadgeAward, ContributorBadge, ContributorBadgeRequest


def completelist(request):
    contributortypes = list(ContributorType.objects.all())
    return render_pgweb(request, 'community', 'contributors/list.html', {
        'contributortypes': contributortypes,
    })


def profile(request, contributor_id):
    contributor = get_object_or_404(Contributor, pk=contributor_id)

    # Get all active badge awards for this contributor
    active_badge_awards = ContributorBadgeAward.objects.filter(
        contributor=contributor,
        active=True
    ).select_related('badge', 'badge__org').order_by('-awarded_date')

    # Get inactive badge awards (only visible to the contributor's own user)
    inactive_badge_awards = []
    if request.user.is_authenticated and contributor.user == request.user:
        inactive_badge_awards = ContributorBadgeAward.objects.filter(
            contributor=contributor,
            active=False
        ).select_related('badge', 'badge__org').order_by('-awarded_date')

    return render_pgweb(request, 'community', 'contributors/profile.html', {
        'contributor': contributor,
        'badge_awards': active_badge_awards,
        'inactive_badge_awards': inactive_badge_awards,
    })


class BadgeRequestForm(forms.ModelForm):
    class Meta:
        model = ContributorBadgeRequest
        fields = ['badge', 'contributor', 'justification']
        widgets = {
            'justification': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Filter contributors to those linked to this user
        if user:
            self.fields['contributor'].queryset = Contributor.objects.filter(user=user)
            if not self.fields['contributor'].queryset.exists():
                self.fields['contributor'].help_text = 'You do not have a contributor profile. One will need to be created for you.'

        # Add CSS classes
        self.fields['badge'].widget.attrs['class'] = 'form-control'
        self.fields['contributor'].widget.attrs['class'] = 'form-control'
        self.fields['contributor'].required = False


@login_required
def request_badge(request):
    if request.method == 'POST':
        form = BadgeRequestForm(request.POST, user=request.user)
        if form.is_valid():
            badge_request = form.save(commit=False)
            badge_request.user = request.user
            badge_request.status = ContributorBadgeRequest.STATUS_APPROVED  # Auto-approve
            badge_request.save()

            # Automatically create inactive badge award
            contributor = badge_request.contributor
            if not contributor:
                # Try to find contributor by user
                try:
                    contributor = Contributor.objects.get(user=request.user)
                except Contributor.DoesNotExist:
                    messages.error(request, 'You need a contributor profile to request a badge. Please contact an administrator.')
                    return redirect('badge_requests')

            # Create inactive badge award if it doesn't already exist
            award, created = ContributorBadgeAward.objects.get_or_create(
                contributor=contributor,
                badge=badge_request.badge,
                defaults={'active': False}
            )

            if created:
                messages.success(request, 'Your badge has been added to your profile (inactive). The organization will review and activate it.')
            else:
                messages.info(request, 'You already have this badge on your profile.')

            return redirect('badge_requests')
    else:
        form = BadgeRequestForm(user=request.user)

    return render_pgweb(request, 'community', 'contributors/request_badge.html', {
        'form': form,
    })


@login_required
def badge_requests(request):
    # Get user's badge requests
    requests_list = ContributorBadgeRequest.objects.filter(
        user=request.user
    ).select_related('badge', 'badge__org', 'contributor').order_by('-requested_date')

    # Attach badge award status to each request
    for req in requests_list:
        if req.contributor:
            try:
                award = ContributorBadgeAward.objects.get(
                    contributor=req.contributor,
                    badge=req.badge
                )
                req.award_active = award.active
            except ContributorBadgeAward.DoesNotExist:
                req.award_active = None
        else:
            req.award_active = None

    return render_pgweb(request, 'community', 'contributors/badge_requests.html', {
        'badge_requests': requests_list,
    })
