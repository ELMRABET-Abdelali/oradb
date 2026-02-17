# Static Assets Directory

This directory contains static assets (CSS, JavaScript, images) for the OracleDBA Web GUI.

## Structure

```
static/
├── css/
│   └── custom.css      # Custom styles (optional)
├── js/
│   └── custom.js       # Custom JavaScript (optional)
└── img/
    └── logo.png        # Custom logo (optional)
```

## Current Implementation

Currently, all CSS and JavaScript are loaded from CDNs:

- **Bootstrap 5**: https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
- **Font Awesome 6**: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css
- **jQuery 3.7**: https://code.jquery.com/jquery-3.7.0.min.js

This keeps the deployment simple and ensures fast loading from CDN edge servers.

## Adding Custom Assets

### Custom CSS

Create `static/css/custom.css`:

```css
/* Custom styles */
.my-custom-class {
    color: #ff0000;
}
```

Then add to `base.html`:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
```

### Custom JavaScript

Create `static/js/custom.js`:

```javascript
// Custom JavaScript
console.log('Custom JS loaded');
```

Then add to `base.html`:

```html
<script src="{{ url_for('static', filename='js/custom.js') }}"></script>
```

### Custom Logo

Place your logo at `static/img/logo.png` and update the header in `base.html`:

```html
<div class="logo">
    <img src="{{ url_for('static', filename='img/logo.png') }}" alt="Logo" height="30">
    OracleDBA
</div>
```

## Production Considerations

For production deployments, consider:

1. **Download CDN assets locally** for offline environments
2. **Minify CSS/JS** for faster loading
3. **Use cache busting**: `custom.css?v=1.0.0`
4. **Enable gzip compression** on web server
5. **Set proper cache headers** for static files

## Nginx Static File Serving

If using Nginx reverse proxy:

```nginx
location /static {
    alias /path/to/oracledba/web/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

This serves static files directly from Nginx without hitting Flask, improving performance.
