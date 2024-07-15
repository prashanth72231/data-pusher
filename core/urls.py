from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import Account_Get, Accounts_Crud, AccountViewSet, Destination_Crud, DestinationViewSet, IncomingDataView

router = DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'destinations', DestinationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('server/incoming_data/', IncomingDataView.as_view(), name='incoming-data'),

    path('accounts-crud/', Accounts_Crud.as_view(), name='accounts-crud'),
    path('accounts-crud/<id>/', Accounts_Crud.as_view(), name='accounts-crud'),
    path('account-get/<token>/', Account_Get.as_view(), name='account-get'),

    path('destination-crud/', Destination_Crud.as_view(), name='destination-crud'),
    path('destination-crud/<id>/', Destination_Crud.as_view(), name='destination-crud'),

]

