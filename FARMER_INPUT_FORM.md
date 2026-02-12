# 🌾 Farmer Input Form - User Guide

## 📱 Access the Application

1. **Home Page**: http://127.0.0.1:8000/
2. **Farmer Input Form**: http://127.0.0.1:8000/farmer-input/

## ✨ Features Implemented

### 1. **Language Toggle (English/Telugu)**
- Click the translate button (🌐) in the top-right corner
- Switches between English and Telugu (తెలుగు)
- All labels, placeholders, and buttons update dynamically

### 2. **Mandal Selection**
- Dropdown with 3 mandals:
  - Machilipatnam
  - Gudivada
  - Vuyyur

### 3. **Village Selection**
- Auto-updates based on selected mandal
- 4 villages per mandal:
  - **Machilipatnam**: Chilakalapudi, Avanigadda, Koduru, Nagayalanka
  - **Gudivada**: Gudivada Urban, Gudivada Rural, Mudinepalli, Pedapalem
  - **Vuyyur**: Vuyyuru Urban, Vuyyuru Rural, Jaggaiahpeta, Nandivada

### 4. **Crop Selection**
- 10 major crops dropdown:
  - Paddy
  - Cotton
  - Chillies
  - Turmeric
  - Maize
  - Sugarcane
  - Banana
  - Groundnut
  - Sunflower
  - Tobacco

### 5. **Acres Input**
- Number input with decimal support
- Minimum: 0.1 acres
- Step: 0.1 (allows precise land area)

### 6. **Sowing Date Picker**
- Date input with calendar popup
- Maximum date: Today (prevents future dates)

### 7. **Image Upload with Preview**
- Accepts all image formats
- Live preview after selection
- Shows uploaded crop/leaf/fruit image
- Optional field

### 8. **Cold Storage Toggle**
- Beautiful toggle switch (❄️)
- ON/OFF indicator
- Turns purple when enabled

### 9. **Urgent Cash Toggle**
- Toggle switch (💰)
- Indicates cash requirement urgency
- Visual feedback on toggle

### 10. **Responsive Design**
- Works on mobile, tablet, and desktop
- Bootstrap 5.3 for clean UI
- Gradient background and rounded corners
- Smooth animations and transitions

## 📂 Files Created/Modified

### New Files:
1. **forecast/templates/forecast/home.html** - Landing page with hero section
2. **forecast/templates/forecast/farmer_input.html** - Main input form with language toggle

### Modified Files:
1. **forecast/views.py** - Added `farmer_input()` view with form handling
2. **forecast/urls.py** - Added route: `/farmer-input/`

## 🎨 UI Design

### Color Scheme:
- Primary: Purple gradient (#667eea → #764ba2)
- Background: Light gradient (#f5f7fa → #c3cfe2)
- Accents: Bootstrap icons and badges

### Form Layout:
- Centered card with shadow
- Icon labels for each field
- Toggle switches for yes/no options
- Image preview with border
- Large submit button with icon

## 🔧 How It Works

### 1. Form Submission Flow:
```
User fills form → Submits → Django saves to database
                           → Creates Farmer record
                           → Creates DiseaseRecord (if image uploaded)
                           → Shows success message
                           → Redirects back to form
```

### 2. Data Storage:
- **Farmer table**: Stores farmer details, crop info, preferences
- **DiseaseRecord table**: Stores uploaded image with detection date

### 3. Language Toggle:
- JavaScript function `toggleLanguage()`
- Swaps text using `data-en` and `data-te` attributes
- Updates placeholders dynamically
- No page reload required

### 4. Village Auto-Update:
- JavaScript function `updateVillages()`
- Reads mandal selection
- Populates village dropdown from JSON data
- Clears previous selection

### 5. Image Preview:
- JavaScript function `previewImage()`
- Uses FileReader API
- Shows image immediately after selection
- Displays below file input

## 🧪 Testing the Form

### Test Data Example:
```
Farmer Name: Ramesh Kumar
Mandal: Machilipatnam
Village: Chilakalapudi
Crop: Paddy
Acres: 5.5
Sowing Date: 2026-01-15
Image: [Upload any crop image]
Cold Storage: ON
Urgent Cash: OFF
```

### Expected Behavior:
1. ✅ All fields validate on submit
2. ✅ Village dropdown updates when mandal changes
3. ✅ Image preview appears after upload
4. ✅ Success message shows after submission
5. ✅ Data saved to database (check Django admin)
6. ✅ Language toggle works without page reload

## 📊 Database Records

After submission, check:
```bash
python manage.py shell
```

```python
from forecast.models import Farmer, DiseaseRecord

# View all farmers
Farmer.objects.all()

# Latest farmer
latest = Farmer.objects.latest('id')
print(f"Name: {latest.name}")
print(f"Mandal: {latest.mandal}")
print(f"Crop: {latest.crop_type}")
print(f"Acres: {latest.total_acres}")

# Check disease records with images
DiseaseRecord.objects.all()
```

## 🌐 URLs Available

| URL | Description |
|-----|-------------|
| `/` | Home page with welcome screen |
| `/farmer-input/` | Farmer input form |
| `/admin/` | Django admin (to view submitted data) |

## 🎯 Next Steps (Step 5)

After this form is complete, the next phase will be:
- ML-based disease detection from uploaded images
- Yield prediction based on historical data
- Market price analysis
- STORE/SELL recommendation
- Results display page

## 💡 Form Validation

### Required Fields:
- ✅ Farmer Name
- ✅ Mandal
- ✅ Village
- ✅ Crop Type
- ✅ Total Acres
- ✅ Sowing Date

### Optional Fields:
- Image Upload
- Cold Storage (defaults to OFF)
- Urgent Cash (defaults to OFF)

## 📱 Mobile Responsive

The form automatically adapts to:
- 📱 **Mobile** (< 768px): Single column, full-width inputs
- 💻 **Tablet** (768-992px): Wider container, better spacing
- 🖥️ **Desktop** (> 992px): Centered card, max 800px width

## 🎨 Language Support

### English Text:
- Farmer Input Form
- Enter your farming details
- Select Mandal, Village, Crop
- Submit & Get Forecast

### Telugu Text (తెలుగు):
- రైతు ఇన్‌పుట్ ఫారమ్
- మీ వ్యవసాయ వివరాలను నమోదు చేయండి
- మండలం, గ్రామం, పంట ఎంచుకోండి
- సమర్పించండి & అంచనా పొందండి

---

**Note**: Server must be running at http://127.0.0.1:8000/ to access the form.
