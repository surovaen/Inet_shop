from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.signing import BadSignature
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import RegisterUserForm, ChangeUserInfoForm
from .models import ShopUser
from .utilities import signer
from orders.models import OrderDB
from shopping.models import ReviewsDB


class RegisterUserView(CreateView):
    """
    Class for registration of new users
    """

    model = ShopUser
    template_name = 'registration/register.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('register_done')


class RegisterDoneView(TemplateView):
    """
    Class for notification of registered users
    """

    template_name = 'registration/register_done.html'


def user_activate(request, sign):
    """
    The function to determine the result of user activation
    and user status change
    """

    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'registration/bad_signature.html')

    user = get_object_or_404(ShopUser, username=username)

    if user.is_activated:
        template = 'registration/user_is_activated.html'
    else:
        template = 'registration/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class ShopPasswordResetView(PasswordResetView):
    """
    Class to reset user password
    """

    template_name = 'registration/pass_reset_form.html'
    subject_template_name = 'email/pass_reset_subject.txt'
    email_template_name = 'email/pass_reset_email.txt'
    success_url = reverse_lazy('password_reset_done')
    extra_email_context = {'domain': 'localhost:8000'}


class MyAccountView(LoginRequiredMixin, TemplateView):
    """
    Class to display user account
    """

    template_name = 'accounts/account.html'


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    """
    Class to update user personal data
    """

    model = ShopUser
    template_name = 'accounts/profile.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('profile')
    success_message = 'Ваши личные данные изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class OrderUserView(LoginRequiredMixin, ListView):
    """
    Class to display user's orders
    """

    model = OrderDB
    template_name = 'accounts/my_orders.html'
    context_object_name = 'orders'
    paginate_by = 6

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

    def get_queryset(self):
        queryset = OrderDB.objects.filter(for_user__pk=self.user_id)\
            .prefetch_related('items')
        return queryset


class ReviewUserView(LoginRequiredMixin, ListView):
    """
    Class to display user's reviews
    """

    model = ReviewsDB
    template_name = 'accounts/my_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 4

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

    def get_queryset(self):
        queryset = ReviewsDB.objects.filter(user_name__pk=self.user_id)\
            .select_related('user_name', 'good')
        return queryset


class DeleteUserView(LoginRequiredMixin, DeleteView):
    """
    Class to delete user
    """

    model = ShopUser
    template_name = 'accounts/delete_account.html'
    success_url = reverse_lazy('index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)
