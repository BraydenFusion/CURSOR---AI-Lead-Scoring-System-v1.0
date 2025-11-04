# 🚗 Dealership Lead Management System

## Overview

This system is designed for **dealerships** to integrate AI-powered lead scoring into their existing sales process. It allows sales reps to upload leads (individually or via CSV), automatically scores them with AI, and provides role-based dashboards for tracking and managing leads.

## 🎯 Key Features

### For Sales Reps
- **Upload Leads**: CSV bulk upload or individual lead entry
- **Automatic AI Scoring**: All uploaded leads are instantly scored using GPT-4
- **Personal Dashboard**: View only their own leads in a sortable table
- **Statistics**: See total leads, hot/warm/cold breakdown, average score
- **Lead Management**: Track leads they've uploaded

### For Managers
- **Team Overview**: See all sales reps and their performance
- **Team Statistics**: Total leads across all reps, team averages
- **Rep Performance**: Compare sales reps side-by-side
- **Access Control**: View all leads but can't modify sales rep data

### For Owners/Admins
- **Full System Overview**: Complete analytics across entire dealership
- **Top Performers**: See which sales reps are performing best
- **Source Analytics**: Track where leads are coming from
- **System Statistics**: Total users, leads, conversion rates
- **Recent Activity**: Monitor all recent lead uploads
- **Full Control**: Complete system access and management

## 📊 System Architecture

### Role-Based Access Control

```
Sales Rep (sales_rep)
├── Can upload leads (CSV or individual)
├── Can view only their own leads
├── Can see their own statistics
└── Dashboard: /dashboard/sales-rep

Manager (manager)
├── Can view all sales reps' leads
├── Can see team performance
├── Can view all sales reps' statistics
└── Dashboard: /dashboard/manager

Owner/Admin (admin)
├── Can view everything
├── Can see all analytics
├── Can see top performers
├── Can view system-wide statistics
└── Dashboard: /dashboard/owner
```

## 🔄 Workflow

1. **Sales Rep Uploads Leads**
   - CSV upload: Bulk import from spreadsheet
   - Individual upload: Manual entry form
   - Leads automatically tagged with `created_by` field

2. **AI Scoring**
   - Every uploaded lead is immediately scored with OpenAI GPT-4
   - Scores include:
     - Overall score (0-100)
     - Engagement score
     - Buying signal score
     - Demographic score
     - Priority tier (HOT/WARM/COLD)
     - Confidence level
     - AI-generated insights

3. **Lead Management**
   - Sales reps see their leads in a table
   - Managers see all reps' leads
   - Owners see everything with analytics

## 📤 CSV Upload Format

CSV file should have these columns:

```csv
name,email,phone,source,location
John Doe,john@example.com,555-0101,website,New York,NY
Jane Smith,jane@example.com,555-0102,referral,Los Angeles,CA
```

**Required Fields:**
- `name` - Customer name
- `email` - Customer email (must be unique)

**Optional Fields:**
- `phone` - Customer phone number
- `source` - Lead source (defaults to "csv_upload")
- `location` - Customer location

## 🛣️ API Endpoints

### Upload Endpoints
- `POST /api/upload/csv` - Upload CSV file with leads
- `POST /api/upload/individual` - Upload single lead

### Dashboard Endpoints
- `GET /api/dashboard/sales-rep` - Sales rep dashboard data
- `GET /api/dashboard/sales-rep/leads` - Sales rep's leads table
- `GET /api/dashboard/manager` - Manager dashboard data
- `GET /api/dashboard/owner` - Owner dashboard data

### Lead Endpoints (Role-Filtered)
- `GET /api/leads` - List leads (filtered by role)
  - Sales reps: Only their leads
  - Managers/Owners: All leads
- `POST /api/leads` - Create lead (now tracks creator)

## 🗄️ Database Changes

### New Field: `created_by`
- Added to `leads` table
- Tracks which user (sales rep) created the lead
- Foreign key to `users.id`
- Nullable (for existing leads)
- Used for role-based filtering

### Migration
- `003_add_lead_ownership.py` - Adds `created_by` field

## 🚀 Setup Instructions

### 1. Run Migration

After Railway redeploys, the migration will run automatically. Or manually:

```bash
cd backend
alembic upgrade head
```

This will add the `created_by` field to the `leads` table.

### 2. Create Users

Create users with appropriate roles:

```bash
# Sales Rep
curl -X POST https://your-backend/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "salesrep1",
    "email": "rep1@dealership.com",
    "full_name": "Sales Rep 1",
    "password": "SecurePass123!@",
    "role": "sales_rep"
  }'

# Manager
curl -X POST https://your-backend/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "manager1",
    "email": "manager@dealership.com",
    "full_name": "Sales Manager",
    "password": "SecurePass123!@",
    "role": "manager"
  }'

# Owner/Admin
curl -X POST https://your-backend/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "owner",
    "email": "owner@dealership.com",
    "full_name": "Dealership Owner",
    "password": "SecurePass123!@",
    "role": "admin"
  }'
```

### 3. Upload Leads

**As Sales Rep:**

1. Login to the system
2. You'll be redirected to `/dashboard/sales-rep`
3. Click "Upload Leads"
4. Choose CSV upload or Individual
5. Upload your leads
6. Leads are automatically AI-scored
7. View your leads in the table

## 📋 CSV Upload Example

Create a CSV file (`leads.csv`):

```csv
name,email,phone,source,location
John Smith,john.smith@email.com,555-0101,website,New York
Mary Johnson,mary.j@email.com,555-0102,referral,Los Angeles
Bob Williams,bob.w@email.com,555-0103,walk-in,Chicago
```

Upload via:
- Sales Rep Dashboard → Upload Leads → CSV Upload → Select file → Upload

## 🎨 Dashboard Features

### Sales Rep Dashboard
- **Upload Section**: CSV or individual lead upload
- **Statistics Cards**: Total, Hot, Warm, Cold leads, Average score
- **Leads Table**: Sortable table with all their leads
- **AI Scoring**: All leads show AI-generated scores and classifications

### Manager Dashboard
- **Team Statistics**: Overall team performance
- **Sales Rep Table**: Performance comparison for all reps
- **Quick Overview**: See which reps are performing best

### Owner Dashboard
- **System Statistics**: Complete system overview
- **Top Performers**: Ranked sales reps by performance
- **Source Breakdown**: See where leads are coming from
- **Recent Activity**: Monitor all recent uploads
- **Full Analytics**: Complete system insights

## 🔐 Security

- **Role-Based Access**: Users can only see data they're authorized for
- **Lead Ownership**: Sales reps can only see their own leads
- **Manager Access**: Managers see all leads but can't modify ownership
- **Owner Access**: Full system access for admins

## 💡 Usage Tips

1. **CSV Upload**: Best for bulk imports from CRM exports
2. **Individual Upload**: Quick entry for single leads
3. **AI Scoring**: Happens automatically - no action needed
4. **Dashboard**: Refreshes automatically after upload
5. **Filtering**: Use the table to sort and filter leads

## 🔄 Next Steps

After Railway redeploys:
1. ✅ Migration will run automatically
2. ✅ Backend endpoints will be available
3. ✅ Frontend dashboards will be accessible
4. ✅ Users can start uploading leads

**Test the System:**
1. Create a sales rep user
2. Login as sales rep
3. Upload a CSV file with test leads
4. View the AI-scored leads in the table
5. Login as manager to see team overview
6. Login as owner to see full analytics

---

**Status**: ✅ Complete and Ready  
**Version**: 3.0.0 - Dealership Integration  
**Next**: Test with real dealership data

