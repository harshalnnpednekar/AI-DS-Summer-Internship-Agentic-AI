# OmniSync Frontend Application

Welcome to the OmniSync Frontend repository. This directory houses the React-based user interface that serves as the primary gateway for Head of Departments, Faculty, and Students to interact with the OmniSync platform. Designed with user experience (UX) and performance in mind, this application delivers a responsive, dynamic, and intuitive digital environment.

## 🌟 Technical Stack

- **Core Library**: [React.js](https://reactjs.org/) (v18+) utilizing modern Functional Components and Hooks.
- **Build Tool**: [Vite](https://vitejs.dev/) - chosen for its significantly faster cold starts and Hot Module Replacement (HMR) compared to traditional bundlers like Webpack.
- **Routing**: [React Router DOM](https://reactrouter.com/) for seamless, client-side Navigation and protected route enforcement.
- **Styling**: Pure CSS combined with custom CSS variables (design tokens) for high customization, enabling rapid iteration of glassmorphism effects, shadows, and flexbox/grid layouts.
- **Icons**: [Lucide React](https://lucide.dev/) for crisp, scalable, and customizable SVG iconography.
- **PDF Generation**: [jsPDF](https://github.com/parallax/jsPDF) paired with `jspdf-autotable` for generating enterprise-grade, academic audit reports on the client side.

## 🗂️ Directory Structure

```text
frontend/
├── public/                 # Static assets that bypass the bundler (e.g., favicons, logos)
├── src/                    # Source code
│   ├── assets/             # Images, fonts, and local stylesheets
│   ├── components/         # Reusable UI components
│   │   ├── Layout.jsx      # Core navigation and sidebar layout (including real-time clock & notifs)
│   │   └── Layout.css      # Heavily customized CSS for equidistant spacing and perfect alignment
│   ├── pages/              # Top-level route components (Views)
│   │   ├── Login.jsx       # Authentication portal
│   │   ├── Dashboard.jsx   # Role-specific main dashboard
│   │   ├── AcademicCalendar.jsx # Calendar upload and event management view
│   │   ├── Attendance.jsx  # Raw attendance data viewer
│   │   └── DefaulterManagement.jsx # Advanced workflow UI and PDF export engine
│   ├── App.jsx             # Root React component and Router configuration
│   └── main.jsx            # Application entry point and DOM rendering
├── index.html              # Base HTML template
├── vite.config.js          # Vite configuration and proxy settings
└── package.json            # Node.js dependencies and NPM scripts
```

## 🚀 Key Features & UI/UX Design

### 1. Role-Based Dashboards
The application dynamically alters its UI based on the authenticated user's role (encoded in the JWT and local storage).
- **HOD/Faculty View**: Grants access to administrative features, including the ability to upload Academic Calendar PDFs and process Attendance files. They have exclusive access to generate Defaulter Lists and Broadcast notifications.
- **Student View**: A streamlined, read-only interface focused on upcoming critical deadlines and personal attendance statistics.

### 2. Defaulter Management & Advanced Workflow UI
We have moved away from basic dashboards to highly descriptive, workflow-driven UI blocks.
- **Vertical Step-by-Step UI**: The Defaulter Management page now includes a dedicated vertical workflow explaining exactly how attendance is calculated, replacing vague explanations with detailed, inline-bolded text and circular badges.
- **Data Granularity**: Displays separate columns for Theory, Practical, and Total attendance, natively ignoring missing practicals for students without them (N/A).
- **Dynamic Attendance Tracking UI**: Features a robust, native collapsible HTML5 dropdown (accordion) layout that sorts attendance records intelligently by Academic Year (FE, SE, TE, BE), Class, and Faculty. It also dynamically adapts the view structure based on whether the logged-in user is an HOD or a Faculty member to remove redundant groupings.
- **Bulk Email Broadcast**: Integrates a seamless UI for selecting multiple defaulter students and dispatching warning emails to them in a single action directly from the dashboard.
- **Form Validation Constraints**: Validates absentee inputs dynamically to ensure integrity during attendance entry, while allowing optional lecture topics for smoother workflow.

### 3. Enterprise-Grade PDF Engine (`exportToPDF`)
Using jsPDF and AutoTable, the frontend generates ultra-premium Academic Audit reports.
- **Cover Page Architecture**: Reports include a formalized cover page featuring institutional titles ("Office of the Academic Registrar"), and a dynamic summary matrix.
- **Conditional Typography**: The table renderer intercepts specific cells (like "Critical" statuses) and automatically changes their text color to dark red, while standard alerts appear in amber.
- **Signature Blocks**: Appends formal HOD and Registrar signature lines directly inside the PDF context.

### 4. Agent Configuration & Settings
- **Persistent State**: Configuration settings (e.g., defaulter thresholds, broadcast toggles) are managed via a dedicated Configuration dashboard and persisted across sessions.
- **Custom Notifications**: Refined user feedback replaces standard browser alerts with custom, beautifully styled toast notifications that align with the platform's premium design system.
- **Live Event Feed**: The `Layout` component polls the backend for upcoming events and displays a live, pulsing notification badge that drops down into an interactive feed.

### 5. Responsive & Modern Aesthetics
- **Pixel-Perfect Alignments**: The sidebar navigation layout enforces strict heights (`64px`), flexbox centering (`justify-content: center`), and synchronized padding so that avatars, icons, and text are universally flush along their vertical axes.
- **Glassmorphism & Shadows**: Utilizes subtle shadows, rounded corners, and blurred backdrops to create a premium, modern aesthetic.
- **Color Palette**: Adheres to a carefully curated color palette designed to reduce eye strain while maintaining high contrast for accessibility.

## 🛠️ Installation & Setup

### Prerequisites
- Node.js (v18.0.0 or higher)
- NPM (v8.0.0 or higher)

### 1. Install Dependencies
Navigate to the `frontend` directory and install the required NPM packages:
```bash
npm install
```

### 2. Development Server
Start the Vite development server:
```bash
npm run dev
```
The application will launch on `http://localhost:5173`. 

### 3. API Proxy Configuration
To circumvent CORS (Cross-Origin Resource Sharing) issues during local development, Vite is configured to proxy API requests. Any request prefixed with `/api` is automatically routed to the FastAPI backend running on `http://localhost:8000`.

This configuration is maintained in `vite.config.js`:
```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```
*Note: Ensure your backend server is actively running when testing API integrations locally.*

### 4. Building for Production
To generate a highly optimized, minified production build:
```bash
npm run build
```
The output will be placed in the `dist/` directory, ready to be served by Nginx, Apache, or any static hosting provider (e.g., Vercel, Netlify).
