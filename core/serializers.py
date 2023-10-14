from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class DealerSerializer(ModelSerializer):
    """Serializer which will return the dealer details with computed fields.
    - name: dealer name
    - username: dealer phone
    - total_orders: total orders placed by the dealer
    - total_amount: total amount of all orders placed by the dealer
    """

    class Meta:
        model = User
        fields = (
            "username",
            "name",
            "total_orders",
            "total_amount",
        )
