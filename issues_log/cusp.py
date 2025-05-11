
# ### API Endpoints

# 1. **Categories**
#    - GET `/api/categories/` - List all categories
#    - POST `/api/categories/` - Create new category
#    - GET/PUT/PATCH/DELETE `/api/categories/{id}/` - Retrieve/Update/Delete category

# 2. **Issues**
#    - GET `/api/issues/` - List all issues (with filters)
#      - Query params: `status`, `priority`, `category`, `search`, `overdue`
#    - POST `/api/issues/` - Create new issue
#    - GET/PUT/PATCH/DELETE `/api/issues/{id}/` - Retrieve/Update/Delete issue
#    - POST `/api/issues/{id}/add_comment/` - Add comment to issue
#    - PATCH `/api/issues/{id}/update_status/` - Update issue status
#    - GET `/api/issues/dashboard_stats/` - Get dashboard statistics

# 3. **Comments**
#    - GET `/api/issues/{issue_pk}/comments/` - List all comments for an issue
#    - POST `/api/issues/{issue_pk}/comments/` - Create new comment
#    - GET/PUT/PATCH/DELETE `/api/issues/{issue_pk}/comments/{id}/` - Retrieve/Update/Delete comment

# This implementation provides a complete backend API that matches the functionality shown in your React components, including:
# - Issue management with all fields
# - Category management
# - Comments system
# - Filtering and searching
# - Dashboard statistics
# - Pagination
# - Authentication (using token auth)

# You can now connect your React frontend to these endpoints to create a fully functional Issues Log application.