# MCP Integration Test Workflow

## Test: Copy Task from Dart AI to NocoDB "Notion Imports" Table

### Prerequisites
- ✅ Dart AI MCP configured and connected
- ✅ NocoDB MCP configured and connected  
- ✅ "Notion Imports" table created (ID: m2qn2emzlgcjzun)

### Test Steps

1. **Create a test task in Dart AI**
   - Use Dart AI MCP to create a sample task
   - Note the task details (title, description, due date, etc.)

2. **Copy task data to NocoDB**
   - Use NocoDB MCP to create a record in "Notion Imports" table
   - Map Dart AI fields to NocoDB columns

3. **Verify the data**
   - Query NocoDB to confirm the record was created
   - Check that all fields were properly transferred

### Sample Data Flow
```
Dart AI Task → MCP Bridge → NocoDB "Notion Imports" Table
```

### NocoDB Table IDs Reference
- Project: pce7ccvwdlz09bx (Base)
- Table: m2qn2emzlgcjzun (Notion Imports)

### Example Commands

#### Create record in NocoDB
```javascript
nocodb_create_record({
  project_id: "pce7ccvwdlz09bx",
  table_id: "m2qn2emzlgcjzun", 
  record_data: {
    "Title": "Task from Dart AI",
    "Description": "Task description",
    "Status": "To Do",
    "CreatedAt": new Date().toISOString()
  }
})
```

### Success Criteria
- Data flows seamlessly between MCP servers
- No formatting or encoding issues
- All fields map correctly
- Timestamps are preserved
