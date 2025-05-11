from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Avg, F
from django.utils import timezone
from datetime import timedelta
from .models import Category, Issue, Comment, Notification
from .serializers import (
    CategorySerializer, 
    IssueSerializer, 
    IssueCreateSerializer,
    IssueStatusUpdateSerializer,
    CommentSerializer,
    NotificationSerializer
)

User = get_user_model()

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

class IssueViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Require authentication for issues
    
    def get_serializer_class(self):
        if self.action == 'create':
            return IssueCreateSerializer
        elif self.action == 'update_status':
            return IssueStatusUpdateSerializer
        return IssueSerializer

    def get_queryset(self):
        queryset = Issue.objects.select_related('category').prefetch_related('comments').all()
        
        # Filtering
        status_param = self.request.query_params.get('status', None)
        priority = self.request.query_params.get('priority', None)
        category = self.request.query_params.get('category', None)
        search = self.request.query_params.get('search', None)
        overdue = self.request.query_params.get('overdue', None)
        
        if status_param and status_param != 'All':
            queryset = queryset.filter(status=status_param)
        if priority and priority != 'All':
            queryset = queryset.filter(priority=priority)
        if category:
            queryset = queryset.filter(category__name=category)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(root_cause__icontains=search) |
                Q(corrective_action__icontains=search) |
                Q(remark__icontains=search) |
                Q(id__icontains=search)
            )
        if overdue:
            today = timezone.now().date()
            queryset = queryset.filter(
                target_close_out_date__lt=today,
                status__in=['Open', 'In Progress']
            )
        
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Generate issue ID
        last_issue = Issue.objects.order_by('-id').first()
        if last_issue:
            last_num = int(last_issue.id.split('-')[1])
            new_num = last_num + 1
        else:
            new_num = 1
        issue_id = f"ISSUE-{str(new_num).zfill(3)}"
        
        serializer.save(
            id=issue_id,
            reported_by=self.request.user.email,
            date_reported=timezone.now().date()
        )

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        issue = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(issue=issue, author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Comment serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        issue = self.get_object()
        serializer = self.get_serializer(issue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(IssueSerializer(issue).data)
        print("Status update serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        status_counts = Issue.objects.values('status').annotate(count=Count('status')).order_by('status')
        priority_counts = Issue.objects.values('priority').annotate(count=Count('priority')).order_by('priority')
        category_counts = Issue.objects.values('category__name').annotate(count=Count('category')).order_by('category__name')
        
        total_issues = Issue.objects.count()
        resolved_issues = Issue.objects.filter(status__in=['Resolved', 'Closed']).count()
        resolution_rate = (resolved_issues / total_issues * 100) if total_issues > 0 else 0
        
        resolved_with_dates = Issue.objects.filter(
            status__in=['Resolved', 'Closed'],
            date_reported__isnull=False,
            date_resolved__isnull=False
        )
        avg_resolution_days = resolved_with_dates.aggregate(
            avg_days=Avg(F('date_resolved') - F('date_reported'))
        )['avg_days'] or 0
        
        today = timezone.now().date()
        overdue_issues = Issue.objects.filter(
            target_close_out_date__lt=today,
            status__in=['Open', 'In Progress']
        ).count()
        
        weeks = []
        resolution_trend = []
        for i in range(4):
            week_start = today - timedelta(days=(3-i)*7)
            week_end = week_start + timedelta(days=6)
            weeks.append(week_start.strftime('%Y-%m-%d'))
            resolved_count = Issue.objects.filter(
                status__in=['Resolved', 'Closed'],
                date_resolved__range=[week_start, week_end]
            ).count()
            resolution_trend.append(resolved_count)
        
        return Response({
            'status_counts': status_counts,
            'priority_counts': priority_counts,
            'category_counts': category_counts,
            'resolution_rate': round(resolution_rate, 1),
            'average_resolution_days': avg_resolution_days.days if avg_resolution_days else 0,
            'overdue_issues': overdue_issues,
            'resolution_trend': {
                'weeks': weeks,
                'counts': resolution_trend
            }
        })

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]  # Require authentication

    def get_queryset(self):
        return Comment.objects.filter(issue_id=self.kwargs['issue_pk'])

    def create(self, request, *args, **kwargs):
        # print("Received request headers:", request.headers)
        # print("Request user:", request.user)
        # print("Request data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)   
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required to add a comment."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        issue = Issue.objects.get(pk=self.kwargs['issue_pk'])
        serializer.save(
            issue=issue,
            author=self.request.user
        )

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]  # Require authentication

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)
