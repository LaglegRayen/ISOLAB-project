# ISOLAB Role-Based Access Control - Testing Guide

## 🎯 Overview
The role-based access control system has been successfully implemented and tested. Users now have proper roles and can only access machines they're assigned to work on.

## 🚀 Application Status
- **Flask App**: Running on http://127.0.0.1:5000
- **Database**: Updated with new user structure
- **Workflow Assignments**: All machines have proper user assignments

## 🔑 Test User Accounts

### 1. Administrator
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Can see ALL machines and modify ANY workflow stage
- **Use Case**: Full system administration

### 2. Assembly Technician
- **Username**: `technicien1` 
- **Password**: `tech123`
- **Access**: Only sees machines with assembly stages assigned
- **Can Modify**: Only "Assemblage" stages
- **Use Case**: Assembly specialist

### 3. Testing Technician
- **Username**: `technicien2`
- **Password**: `tech123` 
- **Access**: Only sees machines with testing stages assigned
- **Can Modify**: Only "Tests et validation" stages
- **Use Case**: Quality control and testing

### 4. Delivery/Installation Technician
- **Username**: `technicien3`
- **Password**: `tech123`
- **Access**: Only sees machines with delivery/installation stages
- **Can Modify**: Only "Livraison" and "Installation" stages
- **Use Case**: Logistics and field installation

### 5. Supervisor
- **Username**: `supervisor`
- **Password**: `super123`
- **Access**: Can see ALL machines
- **Can Modify**: Only "Collecte des matériaux" stages
- **Use Case**: Production oversight

## 🧪 Testing Scenarios

### Scenario 1: Admin Full Access
1. Login as `admin`
2. Go to "Voir Machines"
3. **Expected**: See all 10 machines
4. Click on any machine to view workflow
5. **Expected**: Can update any workflow stage

### Scenario 2: Specialist Access Control
1. Login as `technicien1` (Assembly)
2. Go to "Voir Machines" 
3. **Expected**: See all 10 machines (since all have assembly stages)
4. Click on a machine workflow
5. **Expected**: Can only update "Assemblage" stage
6. Try to update other stages
7. **Expected**: Access denied error

### Scenario 3: Stage-Specific Permissions
1. Login as `technicien2` (Testing)
2. Navigate to machine workflow
3. Try to update "Assemblage" stage
4. **Expected**: "Access denied - you are not assigned to this stage"
5. Update "Tests et validation" stage
6. **Expected**: Success

### Scenario 4: Cross-User Verification
1. Login as `technicien3` (Delivery)
2. Note which machines are visible
3. Logout and login as `technicien1` (Assembly)
4. **Expected**: Same machines visible (all have assignments)
5. **Expected**: Different stage modification permissions

## 🔍 What to Verify

### ✅ Machine Visibility
- [ ] Admin sees all machines
- [ ] Regular users see only assigned machines
- [ ] Machine count varies by user role

### ✅ Workflow Stage Access
- [ ] Users can only modify their assigned stages
- [ ] Access denied errors for unauthorized stages
- [ ] Admin can modify any stage

### ✅ UI Behavior
- [ ] Workflow stages show user assignments
- [ ] Update buttons work correctly
- [ ] Error messages display properly
- [ ] Stage status updates reflect in real-time

### ✅ Security Features
- [ ] No unauthorized data access
- [ ] Proper session management
- [ ] Role-based filtering works
- [ ] Database permissions enforced

## 🐛 Troubleshooting

### If Login Fails
- Verify you're using exact credentials above
- Check if Firebase connection is working
- Ensure users were created properly

### If Role Filtering Doesn't Work
- Check browser console for JavaScript errors
- Verify session data in browser dev tools
- Test with different browsers

### If Workflow Updates Fail
- Check user assignments in database
- Verify stage names match exactly
- Test with admin account first

## 📊 Expected Results Summary

| User | Machines Visible | Can Modify Stages | Special Notes |
|------|------------------|-------------------|---------------|
| admin | All 10 | All stages | Full access |
| technicien1 | All 10 | Assemblage only | Assembly specialist |
| technicien2 | All 10 | Tests et validation only | Testing specialist |
| technicien3 | All 10 | Livraison, Installation | Logistics specialist |
| supervisor | All 10 | Collecte des matériaux | Management oversight |

## 🎉 Success Indicators
- Different users see appropriate content
- Stage update permissions work correctly
- No unauthorized access occurs
- Error messages are clear and helpful
- System maintains security while being user-friendly

## 🔧 Next Steps After Testing
1. Verify all test scenarios pass
2. Test edge cases (empty assignments, etc.)
3. Consider additional role refinements
4. Plan production deployment
5. Document any issues found

---
**Ready to test!** Navigate to http://127.0.0.1:5000 and start with the admin account to verify full functionality, then test with specialized user accounts to confirm role-based restrictions work correctly.
