# History Feature Documentation

## Overview

The History feature has been successfully implemented in the Refinify-AI project, providing users with a comprehensive activity tracking system for all their data processing activities. This feature allows users to view, filter, search, and download their previous reports and processed datasets.

## Features Implemented

### 1. Activity Tracking
- **Data Cleaning**: Tracks all data cleaning operations with configuration details
- **Report Generation**: Records report generation activities (PDF/HTML formats)
- **Data Encryption**: Logs encryption activities with method and column details
- **Typo Correction**: Tracks both single and batch typo correction operations

### 2. History Management
- **View History**: Browse all user activities with pagination
- **Filter by Activity Type**: Filter history by specific activity types
- **Search Functionality**: Search through file names and activity descriptions
- **Download Files**: Download previously generated reports and processed datasets
- **Delete History Items**: Remove unwanted history entries

### 3. User Interface
- **Modern Design**: Clean, responsive interface matching the existing project style
- **Activity Icons**: Visual indicators for different activity types
- **Status Badges**: Clear status indicators (completed, failed, processing)
- **Pagination**: Efficient browsing of large history lists
- **Mobile Responsive**: Works seamlessly on all device sizes

## Backend Implementation

### Database Schema

#### UserHistory Model
```python
class UserHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    file_name = db.Column(db.String(255))
    file_path = db.Column(db.String(1024))
    original_file_name = db.Column(db.String(255))
    activity_details = db.Column(db.JSON)
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### API Endpoints

#### 1. Get User History
```
GET /api/history
Parameters:
- page: Page number (default: 1)
- per_page: Items per page (default: 10)
- activity_type: Filter by activity type (optional)
```

#### 2. Download History File
```
GET /api/history/{history_id}/download
Downloads the file associated with a history item
```

#### 3. Delete History Item
```
DELETE /api/history/{history_id}
Deletes a history item and its associated file
```

### Activity Logging

The system automatically logs user activities in the following endpoints:

1. **Data Cleaning** (`/clean`): Logs cleaning configuration and results
2. **Report Generation** (`/report`): Logs report format and generation details
3. **Data Encryption** (`/encrypt-data`): Logs encryption method and columns
4. **Typo Correction** (`/api/typo/correct`, `/api/typo/batch`): Logs correction methods and statistics
5. **Data Download** (`/download_data`): Logs processed data downloads

## Frontend Implementation

### Components

#### History.jsx
- Main history page component
- Handles data fetching, filtering, and pagination
- Provides download and delete functionality
- Responsive design with modern UI

#### History.css
- Comprehensive styling matching project theme
- Responsive design for all screen sizes
- Activity-specific color coding
- Smooth animations and transitions

### Features

1. **Search and Filter**
   - Real-time search through file names and activities
   - Filter by activity type (Data Cleaning, Report Generation, etc.)
   - Pagination controls

2. **Activity Display**
   - Visual activity icons with color coding
   - Detailed activity information
   - Status indicators
   - File availability indicators

3. **File Management**
   - Download buttons for available files
   - Delete functionality with confirmation
   - File type detection and proper naming

## Installation and Setup

### Backend Setup
1. The database migration will automatically create the `user_history` table
2. No additional configuration required
3. Activity logging is automatically enabled

### Frontend Setup
1. The History component is already integrated into the routing
2. Accessible via the sidebar under "Main" section
3. No additional dependencies required

## Usage

### Accessing History
1. Navigate to the History page from the sidebar
2. View all your activity history with pagination
3. Use search and filters to find specific activities

### Downloading Files
1. Click the download button on any history item with available files
2. Files are automatically named with timestamps and activity types
3. Supported formats: CSV, PDF, HTML, JSON

### Managing History
1. Use the delete button to remove unwanted history items
2. Confirmation dialog prevents accidental deletions
3. Associated files are also deleted from the server

## Activity Types Supported

### 1. Data Cleaning (`data_cleaning`)
- Tracks cleaning configuration
- Records number of columns processed
- Stores cleaning logs and estimates
- Tracks generated plots count

### 2. Report Generation (`report_generation`)
- Records report format (PDF/HTML)
- Stores generation timestamp
- Tracks associated dataset information

### 3. Data Encryption (`data_encryption`)
- Logs encryption method used
- Records columns encrypted
- Tracks total columns and rows processed

### 4. Typo Correction (`typo_correction`)
- Records correction method used
- Tracks number of texts processed
- Stores correction statistics

## File Storage

### Storage Location
- Files are stored in the `uploads/` directory
- Organized with timestamp-based naming
- Automatic cleanup on history item deletion

### File Types
- **CSV**: Processed datasets and encrypted data
- **PDF**: Generated reports
- **HTML**: Generated reports
- **JSON**: Typo correction results

## Security Features

1. **Authentication Required**: All history endpoints require user authentication
2. **User Isolation**: Users can only access their own history
3. **File Access Control**: Files are only accessible to their owners
4. **Secure Deletion**: Files are properly removed when history items are deleted

## Performance Considerations

1. **Pagination**: Large history lists are paginated for performance
2. **File Cleanup**: Automatic cleanup prevents storage bloat
3. **Efficient Queries**: Database queries are optimized with proper indexing
4. **Lazy Loading**: File existence is checked on-demand

## Future Enhancements

### Potential Improvements
1. **Export History**: Bulk export of history data
2. **Activity Analytics**: Charts and statistics of user activities
3. **File Preview**: Preview files before downloading
4. **Activity Sharing**: Share specific activities with other users
5. **Advanced Filtering**: Date range filters and more complex queries

### Technical Improvements
1. **File Compression**: Compress stored files to save space
2. **Cloud Storage**: Move files to cloud storage for scalability
3. **Activity Notifications**: Real-time notifications for completed activities
4. **Batch Operations**: Bulk delete and download operations

## Troubleshooting

### Common Issues

1. **History Not Loading**
   - Check user authentication
   - Verify database connection
   - Check browser console for errors

2. **Files Not Downloading**
   - Verify file exists on server
   - Check file permissions
   - Ensure proper file path

3. **Activity Not Logged**
   - Check user authentication status
   - Verify database write permissions
   - Check server logs for errors

### Debug Information
- Check browser developer tools for API errors
- Review server logs for backend issues
- Verify database table structure
- Test API endpoints directly

## Testing

### Manual Testing
1. Perform various activities (data cleaning, report generation, etc.)
2. Check history page for logged activities
3. Test download functionality
4. Verify delete operations

### Automated Testing
- Use the provided `test_history.py` script
- Test API endpoints with different scenarios
- Verify authentication requirements
- Test error handling

## Conclusion

The History feature provides a comprehensive solution for tracking and managing user activities in the Refinify-AI project. It enhances user experience by providing easy access to previous work and maintains a complete audit trail of all data processing activities.

The implementation follows best practices for security, performance, and user experience, making it a valuable addition to the platform.
