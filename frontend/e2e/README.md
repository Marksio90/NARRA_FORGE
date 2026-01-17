# E2E Tests

End-to-end tests for NARRA_FORGE V2 frontend using Playwright.

## Overview

These tests verify the complete user workflows from browser perspective:
- User authentication (register, login, logout)
- Project management (create, edit, delete)
- Story generation (4-step wizard)
- Job monitoring
- Narrative viewing

## Prerequisites

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Install Playwright browsers:
```bash
npx playwright install
```

3. Ensure backend API is running:
```bash
cd /home/user/NARRA_FORGE
uvicorn api.main:app --reload
```

4. Ensure frontend dev server is running (or tests will start it automatically):
```bash
cd frontend
npm run dev
```

## Running Tests

### Run all tests
```bash
npm test
```

### Run tests in UI mode (interactive)
```bash
npm run test:ui
```

### Run tests in headed mode (see browser)
```bash
npm run test:headed
```

### Run tests with debugging
```bash
npm run test:debug
```

### Run specific test file
```bash
npx playwright test auth.spec.ts
```

### Run specific test
```bash
npx playwright test auth.spec.ts:10
```

### View test report
```bash
npm run test:report
```

## Test Files

- `auth.spec.ts` - Authentication flows (12 tests)
  - Registration with validation
  - Login/logout
  - Session persistence
  - Protected routes
  - Dark mode toggle

- `full-workflow.spec.ts` - Complete user workflows (10 tests)
  - End-to-end narrative generation
  - Multi-project management
  - Project CRUD operations
  - Usage limit tracking
  - Mobile responsive design

## Test Coverage

Current E2E test coverage:
- **Authentication**: 100% (all flows covered)
- **Projects**: 95% (create, edit, delete, list)
- **Story Generation**: 80% (wizard flow, missing actual generation completion)
- **Jobs**: 70% (listing, filtering, missing real-time updates)
- **Narratives**: 60% (listing, filtering, missing viewing details)

## Writing New Tests

Example test structure:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should do something', async ({ page }) => {
    await page.click('button');
    await expect(page.getByText('Success')).toBeVisible();
  });
});
```

## Configuration

Test configuration is in `playwright.config.ts`:
- Base URL: http://localhost:3000
- Browsers: Chrome, Firefox, Safari
- Mobile devices: Pixel 5, iPhone 12
- Retries: 2 on CI, 0 locally
- Screenshots: On failure
- Videos: On first retry

## CI Integration

Tests run automatically on:
- Pull requests to main
- Commits to main
- Nightly builds

GitHub Actions workflow: `.github/workflows/e2e-tests.yml`

## Debugging

### Common Issues

**Tests failing with "page.goto: net::ERR_CONNECTION_REFUSED"**
- Ensure backend and frontend are running
- Check BASE_URL environment variable

**Tests timing out**
- Increase timeout in test or config
- Check if backend is responding slowly

**Element not found**
- Use Playwright Inspector: `npm run test:debug`
- Check selectors with `page.pause()`

### Best Practices

1. **Use semantic selectors**:
   ```typescript
   // Good
   await page.click('text=Submit');
   await page.getByRole('button', { name: 'Submit' });

   // Avoid
   await page.click('#btn-123');
   ```

2. **Wait for navigation**:
   ```typescript
   await page.click('text=Login');
   await page.waitForURL(/dashboard/);
   ```

3. **Use test.beforeEach for setup**:
   ```typescript
   test.beforeEach(async ({ page }) => {
     await page.goto('/');
     // Common setup
   });
   ```

4. **Clean up test data**:
   - Use unique identifiers (timestamps)
   - Clean database between test runs

## Performance Testing

Playwright includes performance metrics:

```typescript
test('should load dashboard quickly', async ({ page }) => {
  const start = Date.now();
  await page.goto('/dashboard');
  const loadTime = Date.now() - start;
  expect(loadTime).toBeLessThan(2000); // 2 seconds
});
```

## Accessibility Testing

Example accessibility test:

```typescript
import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test('should be accessible', async ({ page }) => {
  await page.goto('/');
  await injectAxe(page);
  await checkA11y(page);
});
```

## Next Steps

- [ ] Add tests for real-time job updates
- [ ] Add tests for narrative text viewing
- [ ] Add tests for file downloads
- [ ] Add tests for error states
- [ ] Add visual regression tests
- [ ] Add accessibility tests
- [ ] Add performance tests
