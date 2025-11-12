# Stock Screener UI

A professional, minimalistic web interface for the Stock Screener application with real-time breakout detection.

## Overview

The UI provides a clean, intuitive workflow for screening Indian stocks and detecting breakout signals using technical indicators and AI-powered analysis.

## Features

### 1. **Health Status Monitoring**
- Real-time system health indicator in the header
- Shows Redis connection status and stock count
- Auto-refreshes every 30 seconds

### 2. **Three-Step Workflow**

#### Step 1: Initialize Stock List
- Fetches Indian stocks from NSE (NIFTY 50, 500, BANK, IT, PHARMA, AUTO)
- Displays total count of initialized stocks
- View button to see complete list of stocks
- Fallback to popular stocks if NSE API fails

#### Step 2: Screen All Stocks
- Concurrent screening with configurable workers (1-20)
- Real-time progress bar showing completion percentage
- Live statistics:
  - Processed count
  - Breakouts detected
  - Errors encountered
- Synchronous execution with immediate results

#### Step 3: Stocks on Radar
- Displays all stocks with detected breakout signals
- Shows confidence level for each stock
- Lists supporting technical signals
- Displays AI-powered reasoning for each breakout
- Shows last price and timestamp

### 3. **User Experience**

- **Clean Design**: Minimalistic color scheme with professional appearance
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Real-time Updates**: Live progress tracking during screening
- **Toast Notifications**: Non-intrusive feedback for all actions
- **Loading States**: Clear visual indicators for ongoing operations
- **Error Handling**: Graceful error messages with helpful context

## Design System

### Color Palette

- **Primary**: Deep blue (#2563eb) - Action buttons, progress bars
- **Success**: Green (#10b981) - Breakout indicators, completed states
- **Warning**: Orange (#f59e0b) - Moderate confidence, errors
- **Background**: Light gray (#f8fafc) - Main background
- **Surface**: White (#ffffff) - Cards and containers
- **Text**: Dark slate (#0f172a) - Primary text

### Typography

- **Font**: Inter (Google Fonts)
- **Weights**: 300 (light), 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- **Hierarchy**: Clear visual hierarchy with appropriate sizing

### Components

- **Cards**: Elevated surfaces with subtle shadows
- **Buttons**: Clear primary/secondary distinction
- **Stats**: Large, readable numbers with descriptive labels
- **Progress Bars**: Smooth animations with percentage indicators
- **Modals**: Centered overlay with backdrop
- **Toast Notifications**: Slide-in from right with auto-dismiss

## Technical Stack

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS variables, flexbox, and grid
- **Vanilla JavaScript**: No framework dependencies for lightweight performance
- **Google Fonts**: Inter font family
- **SVG Icons**: Inline scalable icons

## API Integration

The UI communicates with the FastAPI backend through RESTful endpoints:

- `GET /api/v1/health` - System health check
- `POST /api/v1/stocks/initialize` - Initialize stock list
- `GET /api/v1/stocks/list` - Get all stocks
- `POST /api/v1/screen/all/sync` - Screen all stocks
- `GET /api/v1/radar` - Get stocks on radar

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # Complete styling with CSS variables
├── app.js          # Application logic and API integration
└── README.md       # This file
```

## Usage

1. **Start the application**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Access the UI**:
   - Navigate to `http://localhost:8000` in your web browser

3. **Workflow**:
   - Click "Initialize Stocks" to fetch stock list from NSE
   - Set concurrent workers (recommended: 5)
   - Click "Start Screening" to analyze all stocks
   - View detected breakouts in the "Stocks on Radar" section
   - Click "Refresh Radar" to update the list anytime

## Key Features for Users

### Stock List Modal
- Grid view of all initialized stocks
- Easy browsing of available symbols
- Quick access via "View List" button

### Real-time Progress
- Visual progress bar during screening
- Percentage completion indicator
- Live count updates for processed, breakouts, and errors

### Radar Stock Cards
- Symbol and confidence badge
- Last price with timestamp
- Top 3 technical signals with expandable view
- AI-generated reasoning for breakout detection

### Responsive Design
- Mobile-first approach
- Adapts to all screen sizes
- Touch-friendly interface
- Optimized for both desktop and mobile workflows

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Lightweight: No heavy JavaScript frameworks
- Fast loading: Minimal dependencies
- Efficient API calls: Debounced requests
- Smooth animations: Hardware-accelerated CSS transitions

## Accessibility

- Semantic HTML5 elements
- Clear visual hierarchy
- Keyboard navigation support
- High contrast ratios for readability
- Screen reader friendly

## Future Enhancements

- Stock search and filtering
- Historical radar view
- Export results to CSV/JSON
- Real-time WebSocket updates
- Dark mode toggle
- Customizable technical indicator thresholds
- Chart visualization for individual stocks
- Portfolio tracking integration
