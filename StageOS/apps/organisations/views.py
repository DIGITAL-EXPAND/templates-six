from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Organisation
from .serializers import OrganisationSerializer


class OrganisationListView(generics.ListAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.organisation_id:
            return Organisation.objects.none()
        return Organisation.objects.filter(id=self.request.user.organisation_id)
