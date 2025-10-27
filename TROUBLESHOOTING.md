# Planty Troubleshooting Guide

## Issue: Dashboard Creation Failed

**Error**: `Failed to create My Plants dashboard: 'planty'`

### ✅ **Fixes Applied**

1. **Improved Dashboard Registration**
   - Added multiple fallback methods for dashboard creation
   - Uses frontend panel registration as primary method
   - Falls back to lovelace registration if needed
   - Added proper error handling to prevent integration failure

2. **Simplified Custom Cards**
   - Removed complex import statements that might cause issues
   - Updated card registration to be more robust
   - Better error handling in frontend resources

3. **Graceful Failure**
   - Integration now works even if dashboard creation fails
   - Creates notification when dashboard setup fails
   - Sensors and services still work normally

## 🚀 **Next Steps**

### **Step 1: Restart Home Assistant**
Restart HA completely to apply the fixes.

### **Step 2: Test Basic Functionality**
Add a test plant using Developer Tools → Services:

```yaml
service: planty.add_plant
data:
  plant_name: "My Test Plant"
  plant_type: "pothos"
  watering_mode: "manual"
  watering_interval: 7
```

### **Step 3: Check Results**
After adding a plant, check for:

1. **Sensors Created**: Go to Developer Tools → States
   - Look for: `sensor.planty_my_test_plant_water_status`
   - Look for: `sensor.planty_my_test_plant_days_until_water`
   - Look for: `button.planty_my_test_plant_water`

2. **Dashboard Appears**: Check sidebar for "My Plants"
   - If not visible, check Settings → Dashboards

3. **Services Available**: Developer Tools → Services
   - `planty.add_plant`
   - `planty.water_plant`
   - `planty.update_plant_settings`

### **Step 4: Manual Dashboard (If Needed)**
If automatic dashboard still doesn't work:

1. **Create Manual Dashboard**:
   - Settings → Dashboards → Add Dashboard
   - Title: "My Plants"
   - Icon: `mdi:leaf`
   - URL: `my-plants`

2. **Add Cards**: Once in the dashboard, add cards manually:
   - Click "Edit Dashboard"
   - Add Card → Custom: `planty-header-card`
   - Add Card → Custom: `planty-settings-card`
   - Add Card → Custom: `planty-card` (for each plant)

## 🔧 **Manual Card Configuration**

If you need to add cards manually, use these configurations:

### **Header Card**
```yaml
type: custom:planty-header-card
title: My Plants
subtitle: Plant care made simple
```

### **Settings Card**
```yaml
type: custom:planty-settings-card
```

### **Plant Card**
```yaml
type: custom:planty-card
entity: sensor.planty_[plant_id]_water_status
plant_id: [plant_id]
name: [Plant Name]
plant_type: [plant_type]
watering_mode: manual
```

## 📋 **Verification Checklist**

- ✅ Integration loads without errors
- ✅ Services are available in Developer Tools
- ✅ Adding plants creates sensors
- ✅ Watering plants updates sensors
- ✅ Dashboard appears in sidebar (automatic or manual)
- ✅ Custom cards load without JavaScript errors

## 🆘 **If Issues Persist**

Check logs for specific errors and ensure:

1. **All files are present** in `custom_components/planty/`
2. **www folder exists** with all JavaScript files
3. **No JavaScript errors** in browser console (F12)
4. **Home Assistant version** is 2023.1.0 or later

The integration should now work reliably even if the automatic dashboard creation fails!
