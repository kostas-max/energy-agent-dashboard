# Energy Agent Dashboard - Frontend

Σύγχρονο, επαγγελματικό web interface για το Energy Agent Dashboard API.

## Χαρακτηριστικά

### 🎨 Design
- Modern, clean UI με Tailwind-inspired styling
- Dark mode sidebar με accent colors
- Responsive design (mobile-friendly)
- Smooth animations και transitions
- Font Awesome icons

### 📊 Dashboard
- Real-time statistics
  - Σύνολο νέων άρθρων
  - Σημαντικά άρθρα
  - Ενεργές πηγές
  - Κατηγορίες
- Προβολή πρόσφατων άρθρων

### 📰 Νέα
- Εμφάνιση όλων των άρθρων
- **Search**: Αναζήτηση στους τίτλους
- **Filtering**: Φιλτράρισμα ανά κατηγορία (topic)
- Hover effects
- Metadata display (ημερομηνία, κατηγορία, saved status)
- AI summaries

### ⭐ Σημαντικά
- Προβολή saved άρθρων
- Ίδια λειτουργικότητα με τα Νέα (search, filter)
- Empty state messages

### 🤖 Agent Prompt
- Textarea για εντολές
- Real-time response display
- Λίστα διαθέσιμων εντολών
- Error handling

### 🌐 Πηγές
- Προσθήκη νέων πηγών
- Λίστα υπαρχόντων πηγών
- Delete functionality με confirmation
- Type detection (RSS, HTML, API)

### 🧠 AI Usage Tracker
- Real-time progress bar
- Λεπτά χρήσης / Σύνολο
- Auto-refresh κάθε 30 δευτερόλεπτα
- Sidebar widget

## Τεχνολογίες

- **HTML5** - Semantic markup
- **CSS3** - Custom properties, Flexbox, Grid
- **Vanilla JavaScript** - ES6+, async/await
- **Font Awesome 6.4.0** - Icons
- **Fetch API** - HTTP requests

## Εγκατάσταση

Το frontend είναι ένα **single-page HTML file** - δεν χρειάζεται build process ή dependencies!

### Βήμα 1: Εκκίνηση Backend

```bash
cd backend
python main.py
```

Το API θα τρέχει στο `http://localhost:8000`

### Βήμα 2: Άνοιγμα Frontend

Απλά ανοίξτε το `index.html` σε browser:

**Επιλογή Α: Double-click**
```
frontend/index.html
```

**Επιλογή Β: Live Server (προτείνεται)**

Αν έχετε VS Code με Live Server extension:
- Right-click στο `index.html`
- "Open with Live Server"

**Επιλογή Γ: Python HTTP Server**
```bash
cd frontend
python -m http.server 8080
```

Μετά ανοίξτε: `http://localhost:8080`

## Χρήση

### Πλοήγηση

Χρησιμοποιήστε το sidebar για να μετακινηθείτε μεταξύ:
- **Dashboard**: Επισκόπηση
- **Νέα**: Όλα τα άρθρα
- **Σημαντικά**: Saved άρθρα
- **Agent Prompt**: Εντολές
- **Πηγές**: Διαχείριση πηγών

### Search & Filter

Στα **Νέα** και **Σημαντικά**:
1. Χρησιμοποιήστε το search box για αναζήτηση
2. Κλικ στα filter buttons για κατηγορίες
3. Combine search + filter για ακριβή αποτελέσματα

### Agent Commands

Στο **Agent Prompt** tab:
```
ψάξε φωτοβολταϊκά
πρόσθεσε πηγή https://ypen.gov.gr/feed/
δείξε τις πηγές
φτιάξε φάκελο Αντλίες
βάλε στο ημερολόγιο 15/11/2025
σημαντικό https://example.com/article
βοήθεια
```

## Customization

### Χρώματα

Επεξεργαστείτε τις CSS variables στο `<style>`:

```css
:root {
  --primary: #10b981;        /* Πράσινο - primary color */
  --primary-dark: #059669;   /* Σκούρο πράσινο */
  --bg-dark: #111827;        /* Sidebar background */
  --bg-gray: #1f2937;        /* Secondary dark */
  --bg-light: #f3f4f6;       /* Body background */
}
```

### API Base URL

Αν το backend τρέχει σε άλλο port:

```javascript
const API_BASE = 'http://localhost:8000';  // Line 566
```

### Icons

Αλλάξτε τα Font Awesome icons:
```html
<i class="fas fa-home"></i>        <!-- Solid -->
<i class="far fa-clock"></i>       <!-- Regular -->
<i class="fab fa-github"></i>      <!-- Brands -->
```

## Troubleshooting

### CORS Errors

Αν δείτε CORS errors στο console:
1. Βεβαιωθείτε ότι το backend τρέχει
2. Το backend έχει ήδη CORS enabled για `*`
3. Ανοίξτε το frontend μέσω HTTP server (όχι file://)

### Δεν φορτώνει δεδομένα

1. Έλεγχος backend: `http://localhost:8000/news`
2. Έλεγχος console για errors (F12)
3. Verify API_BASE URL

### Icons δεν φαίνονται

Το CDN link μπορεί να είναι blocked. Κατεβάστε Font Awesome locally:
```html
<link rel="stylesheet" href="path/to/fontawesome/css/all.min.css">
```

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Performance

- Single HTML file (~30KB)
- Font Awesome CDN (~70KB cached)
- No frameworks or build tools
- Fast load times
- Minimal HTTP requests

## Security

- No authentication (localhost only)
- XSS protection via textContent
- HTTPS ready
- No inline event handlers (addEventListener)

## Features Summary

| Feature | Status |
|---------|--------|
| Dashboard Overview | ✅ |
| News List | ✅ |
| Saved Articles | ✅ |
| Search | ✅ |
| Category Filters | ✅ |
| Agent Prompt | ✅ |
| Sources Management | ✅ |
| AI Usage Tracker | ✅ |
| Responsive Design | ✅ |
| Dark Mode Sidebar | ✅ |
| Empty States | ✅ |
| Loading States | ✅ |
| Error Handling | ✅ |

## Future Enhancements

Πιθανές μελλοντικές βελτιώσεις:
- [ ] Dark mode για ολόκληρη την εφαρμογή
- [ ] Export data (CSV, JSON)
- [ ] Notifications
- [ ] User preferences
- [ ] Keyboard shortcuts
- [ ] Multi-language support
- [ ] Offline mode (Service Worker)
- [ ] Charts & graphs
- [ ] Calendar view integration

## Credits

- Design inspired by modern dashboards
- Icons by Font Awesome
- Colors from Tailwind CSS palette

## License

Μέρος του Energy Agent Dashboard project.

---

**Developed with ❤️ for the Greek Energy sector**
