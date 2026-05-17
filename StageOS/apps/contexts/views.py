from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views import TenantScopedMixin
from .models import OperatingContext
from .serializers import OperatingContextSerializer, ChangeStatusSerializer
from .services import create_context, change_context_status


class OperatingContextViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = OperatingContext.objects.select_related(
        'site', 'venue', 'primary_space', 'owner', 'department', 'parent_context',
    )
    serializer_class = OperatingContextSerializer
    filterset_fields = ['context_type', 'status', 'priority', 'risk_level', 'site', 'venue', 'owner']
    search_fields = ['title', 'synopsis']
    ordering_fields = ['opening_date', 'created_at', 'readiness_score', 'title']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        context = create_context(
            organisation=self.request.user.organisation,
            user=self.request.user,
            data=serializer.validated_data,
        )
        serializer.instance = context

    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        context = self.get_object()
        input_serializer = ChangeStatusSerializer(data=request.data)
        if not input_serializer.is_valid():
            return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            updated = change_context_status(
                context=context,
                user=request.user,
                new_status=input_serializer.validated_data['status'],
                comment=input_serializer.validated_data.get('comment', ''),
            )
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            OperatingContextSerializer(updated, context={'request': request}).data
        )
