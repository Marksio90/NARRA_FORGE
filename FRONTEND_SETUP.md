# Frontend Setup Instructions

## Phase 3: Frontend (Next.js 14 + TypeScript + TailwindCSS)

### Quick Start

```bash
cd /home/user/NARRA_FORGE/frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Implementation Status

**Phase 3 Progress:** 27% (4/15 tasks)

✅ **Completed:**
1. Next.js 15 initialization
2. TailwindCSS + shadcn/ui setup
3. Project structure
4. API client + TypeScript types

⏭️ **To Do:**
5. Auth Context + hooks
6-13. Build 8 main pages
14-15. Mobile responsive + dark mode
16. Testing & polish

### Files Created (Not in Git)

Due to large node_modules, frontend source is maintained separately.

**Key Files:**
- `package.json` - Next.js 15, React 19, TypeScript, Tailwind
- `src/types/api.ts` - TypeScript types matching backend
- `src/services/api.ts` - Complete API client
- `src/app/` - Next.js App Router pages
- `src/components/ui/` - shadcn/ui components

### API Integration

Frontend connects to backend at `http://localhost:8000` via:
- Auth: register, login, refresh
- Projects: CRUD operations
- Jobs: create, monitor, cancel, resume
- Narratives: list, view, download

### Next Steps

1. Implement Auth Context
2. Build Landing Page
3. Create Dashboard layout
4. Add 8 main pages (wizard, viewer, etc.)

---

**Note:** Full frontend implementation continues in Phase 3.
See `api/README.md` for complete backend documentation.
