# Add these action methods to TimetableViewSet in views.py

    @action(detail=True, methods=['post'])
    def share_with_groups(self, request, pk=None):
        """Share timetable with additional class groups"""
        class_group_ids = request.data.get('class_group_ids', [])
        
        if not class_group_ids:
            return error_response(message="Class group IDs are required")
        
        try:
            timetable = TimetableManagementService.share_timetable_with_groups(
                pk, class_group_ids
            )
            return success_response(
                data=TimetableSerializer(timetable).data,
                message="Timetable shared successfully"
            )
        except ValueError as e:
            return error_response(message=str(e))
        except Exception as e:
            return error_response(message="Error sharing timetable", errors=str(e))

    @action(detail=True, methods=['post'])
    def remove_shared_group(self, request, pk=None):
        """Remove a class group from shared timetable"""
        class_group_id = request.data.get('class_group_id')
        
        if not class_group_id:
            return error_response(message="Class group ID is required")
        
        try:
            timetable = TimetableManagementService.remove_shared_group(
                pk, class_group_id
            )
            return success_response(
                data=TimetableSerializer(timetable).data,
                message="Class group removed from timetable"
            )
        except Exception as e:
            return error_response(message="Error removing group", errors=str(e))

    @action(detail=True, methods=['get'])
    def shared_groups(self, request, pk=None):
        """Get all groups sharing this timetable"""
        try:
            from services.core_service.academic_module.class_app.serializers import ClassGroupSerializer
            
            groups = TimetableManagementService.get_all_groups_in_timetable(pk)
            serializer = ClassGroupSerializer(groups, many=True)
            
            return success_response(
                data=serializer.data,
                message="Shared groups retrieved successfully"
            )
        except Exception as e:
            return error_response(message="Error retrieving groups", errors=str(e))
