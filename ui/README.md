# NARRA_FORGE UI

Production-ready Next.js 16 interface for the NARRA_FORGE autonomous literary production platform.

## Features

- **Next.js 16** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Real-time Job Monitoring** with automatic polling
- **Pipeline Visualization** showing all 9 stages
- **Cost Tracking Dashboard** with detailed breakdown
- **Artifact Management** with JSON viewing
- **Responsive Design** optimized for desktop and mobile

## Prerequisites

- Node.js 18+ or Bun
- Backend API running at `http://localhost:8000`

## Getting Started

### 1. Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
# or
bun install
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` and set the API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
ui/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── jobs/              # Job management pages
│   │   │   ├── [id]/          # Job detail page
│   │   │   ├── new/           # Job creation page
│   │   │   └── page.tsx       # Jobs list page
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Homepage
│   │   └── globals.css        # Global styles
│   ├── lib/
│   │   └── api-client.ts      # Backend API client
│   └── types/
│       └── api.ts             # TypeScript types (matches backend)
├── public/                     # Static assets
├── tailwind.config.ts          # Tailwind configuration
├── tsconfig.json              # TypeScript configuration
└── next.config.ts             # Next.js configuration
```

## Pages

### Homepage (`/`)
- Platform overview
- Feature highlights
- Pipeline stages visualization
- Quick access to job creation

### Jobs List (`/jobs`)
- View all jobs
- Filter by status
- Quick access to job details
- Real-time status updates

### Job Detail (`/jobs/[id]`)
- Complete job information
- Live pipeline visualization
- Artifacts viewer
- Cost tracking table
- Job control (start, cancel)

### New Job (`/jobs/new`)
- Job creation form
- Type selection (short story, novel chapter, etc.)
- Genre selection
- Word count configuration
- Budget limits

## API Integration

The UI communicates with the backend via the API client in `src/lib/api-client.ts`.

### Available Methods

```typescript
// Jobs
apiClient.createJob(request)
apiClient.getJob(jobId)
apiClient.listJobs(params)
apiClient.cancelJob(jobId)

// Pipeline
apiClient.executePipeline(jobId)
apiClient.getPipelineStatus(jobId)

// Artifacts
apiClient.getArtifacts(jobId)
apiClient.getArtifact(artifactId)

// Costs
apiClient.getCosts(jobId)
apiClient.checkBudget(jobId)

// Observability
apiClient.getStatistics()
```

## Development

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

### Build for Production

```bash
npm run build
npm run start
```

## Styling

The UI uses Tailwind CSS with a custom color palette:

- **Primary**: Blue shades for main actions
- **Success**: Green for completed states
- **Warning**: Yellow for warnings
- **Error**: Red for errors
- **Gray**: Neutral tones for UI elements

## Real-time Updates

Job detail pages automatically poll the backend every 5 seconds to show:
- Pipeline progress
- Cost updates
- New artifacts
- Status changes

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Performance

- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Time to Interactive**: < 3.5s

Optimized with:
- Server-side rendering (SSR)
- Automatic code splitting
- Image optimization
- CSS minification

## License

Part of the NARRA_FORGE project.
