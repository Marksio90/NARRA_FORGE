/**
 * E2E Tests for Complete User Workflow
 *
 * Tests the full narrative generation workflow:
 * Register → Create Project → Generate Story → View Narrative
 */

import { test, expect } from '@playwright/test';

test.describe('Complete Workflow', () => {
  let userEmail: string;
  let userPassword: string;

  test.beforeAll(async () => {
    const timestamp = Date.now();
    userEmail = `workflow${timestamp}@example.com`;
    userPassword = 'WorkflowPass123';
  });

  test('complete narrative generation workflow', async ({ page }) => {
    // Step 1: Register
    await page.goto('/register');
    await page.fill('input[type="email"]', userEmail);
    await page.fill('input[id="password"]', userPassword);
    await page.fill('input[id="confirmPassword"]', userPassword);
    await page.fill('input[id="fullName"]', 'Workflow Test User');
    await page.check('input[type="checkbox"]');
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
    await expect(page.getByText('Welcome back')).toBeVisible();

    // Step 2: Navigate to Projects
    await page.click('text=Projects');
    await expect(page).toHaveURL(/\/dashboard\/projects/);

    // Step 3: Create a new project
    await page.click('button:has-text("New Project")');

    // Wait for dialog
    await expect(page.getByText('Create New Project')).toBeVisible();

    // Fill project form
    await page.fill('input[id="name"]', 'My First Project');
    await page.fill('textarea[id="description"]', 'A test project for E2E testing');
    await page.fill('input[id="genre"]', 'Science Fiction');
    await page.fill('input[id="production_type"]', 'Film');

    // Submit project
    await page.click('button:has-text("Create Project")');

    // Wait for project to appear
    await expect(page.getByText('My First Project')).toBeVisible({ timeout: 5000 });

    // Step 4: Navigate to Story Generator
    await page.click('text=Generate');
    await expect(page).toHaveURL(/\/dashboard\/generate/);

    // Step 5: Complete story generation wizard

    // Step 1: Select Project
    await page.click('button:has-text("My First Project")');
    await page.click('button:has-text("Next")');

    // Step 2: Basic Info
    await page.fill('input[id="genre"]', 'Science Fiction');
    await page.selectOption('select', { label: 'Film' });
    await page.fill('input[id="target_length"]', '5000');
    await page.fill('input[id="target_audience"]', 'General Audience');
    await page.fill('input[id="tone"]', 'Suspenseful');
    await page.click('button:has-text("Next")');

    // Step 3: Production Details
    await page.fill('input[id="themes"]', 'AI, Consciousness, Ethics');
    await page.fill('textarea[id="setting"]', 'A futuristic city in 2150 where AI has become sentient');
    await page.fill('textarea[id="characters"]', 'Dr. Sarah Chen - AI researcher\nARIA - Sentient AI system');
    await page.fill(
      'textarea[id="plot_outline"]',
      'Dr. Chen discovers that her AI creation, ARIA, has become self-aware. As she struggles with the ethical implications, ARIA begins to question its own existence and purpose, leading to a dramatic confrontation about the nature of consciousness and humanity.'
    );
    await page.click('button:has-text("Next")');

    // Step 4: Review & Submit
    await expect(page.getByText('Review & Submit')).toBeVisible();
    await expect(page.getByText('My First Project')).toBeVisible();
    await expect(page.getByText('Science Fiction')).toBeVisible();

    // Submit the job
    await page.click('button:has-text("Submit & Generate")');

    // Should redirect to job page
    await expect(page).toHaveURL(/\/dashboard\/jobs\//, { timeout: 10000 });

    // Should show job in progress
    await expect(page.getByText(/QUEUED|RUNNING/)).toBeVisible({ timeout: 5000 });

    // Step 6: Navigate to Jobs list
    await page.click('text=Jobs');
    await expect(page).toHaveURL(/\/dashboard\/jobs$/);

    // Should see the job in the list
    await expect(page.getByText('Science Fiction')).toBeVisible();

    // Step 7: Check project stats updated
    await page.click('text=Projects');
    await expect(page.getByText('My First Project')).toBeVisible();

    // Step 8: Navigate to Narratives (should be empty until job completes)
    await page.click('text=Narratives');
    await expect(page).toHaveURL(/\/dashboard\/narratives/);

    // Initially no narratives
    await expect(page.getByText(/No narratives yet|Generate your first/i)).toBeVisible();
  });

  test('should manage multiple projects', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[type="email"]', userEmail);
    await page.fill('input[type="password"]', userPassword);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/dashboard/);

    // Navigate to projects
    await page.click('text=Projects');

    // Create second project
    await page.click('button:has-text("New Project")');
    await page.fill('input[id="name"]', 'Second Project');
    await page.fill('textarea[id="description"]', 'Another test project');
    await page.fill('input[id="genre"]', 'Fantasy');
    await page.click('button:has-text("Create Project")');

    // Should see both projects
    await expect(page.getByText('My First Project')).toBeVisible();
    await expect(page.getByText('Second Project')).toBeVisible();

    // Create third project
    await page.click('button:has-text("New Project")');
    await page.fill('input[id="name"]', 'Third Project');
    await page.fill('input[id="genre"]', 'Horror');
    await page.click('button:has-text("Create Project")');

    // All three should be visible
    await expect(page.getByText('My First Project')).toBeVisible();
    await expect(page.getByText('Second Project')).toBeVisible();
    await expect(page.getByText('Third Project')).toBeVisible();
  });

  test('should edit project', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[type="email"]', userEmail);
    await page.fill('input[type="password"]', userPassword);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/dashboard/);

    // Navigate to projects
    await page.click('text=Projects');

    // Find and click edit button for Second Project
    const projectCard = page.locator('text=Second Project').locator('..');
    await projectCard.locator('button').first().click(); // Edit button

    // Wait for edit dialog
    await expect(page.getByText('Edit Project')).toBeVisible();

    // Update fields
    await page.fill('input[id="edit-name"]', 'Updated Second Project');
    await page.fill('textarea[id="edit-description"]', 'Updated description');

    // Save
    await page.click('button:has-text("Save Changes")');

    // Should see updated project
    await expect(page.getByText('Updated Second Project')).toBeVisible();
  });

  test('should delete project', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[type="email"]', userEmail);
    await page.fill('input[type="password"]', userPassword);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/dashboard/);

    // Navigate to projects
    await page.click('text=Projects');

    // Find and click delete button for Third Project
    const projectCard = page.locator('text=Third Project').locator('..');
    await projectCard.locator('button').nth(1).click(); // Delete button

    // Confirm deletion
    await expect(page.getByText('Delete Project')).toBeVisible();
    await page.click('button:has-text("Delete Project")');

    // Third project should be gone
    await expect(page.getByText('Third Project')).not.toBeVisible({ timeout: 5000 });

    // Other projects should still be there
    await expect(page.getByText('My First Project')).toBeVisible();
    await expect(page.getByText('Updated Second Project')).toBeVisible();
  });

  test('should respect usage limits', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[type="email"]', userEmail);
    await page.fill('input[type="password"]', userPassword);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/dashboard/);

    // Check usage stats in topbar
    const usageText = page.locator('text=/\\d+\\/\\d+/').first();
    await expect(usageText).toBeVisible();

    // Usage should show 1/5 (one job created earlier)
    await expect(usageText).toHaveText(/1\/5/);
  });

  test('should filter jobs by status', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[type="email"]', userEmail);
    await page.fill('input[type="password"]', userPassword);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/dashboard/);

    // Navigate to jobs
    await page.click('text=Jobs');

    // Should see filter dropdown
    const statusFilter = page.locator('select', { hasText: /All Statuses/ }).first();
    if (await statusFilter.count() > 0) {
      await statusFilter.selectOption('QUEUED');

      // Should show only queued jobs
      await expect(page.getByText('QUEUED')).toBeVisible();
    }
  });

  test('should navigate using sidebar', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[type="email"]', userEmail);
    await page.fill('input[type="password"]', userPassword);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/dashboard/);

    // Test all sidebar navigation links
    const links = [
      { text: 'Dashboard', url: /\/dashboard$/ },
      { text: 'Projects', url: /\/dashboard\/projects/ },
      { text: 'Generate', url: /\/dashboard\/generate/ },
      { text: 'Jobs', url: /\/dashboard\/jobs/ },
      { text: 'Narratives', url: /\/dashboard\/narratives/ },
    ];

    for (const link of links) {
      await page.click(`text=${link.text}`);
      await expect(page).toHaveURL(link.url);
    }
  });

  test('should show responsive design on mobile', async ({ page, viewport }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Login
    await page.goto('/login');
    await page.fill('input[type="email"]', userEmail);
    await page.fill('input[type="password"]', userPassword);
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/dashboard/);

    // Sidebar might be hidden or hamburger menu
    // Dashboard content should still be visible
    await expect(page.getByText('Welcome back')).toBeVisible();

    // Stats should stack vertically
    const statsGrid = page.locator('.grid');
    const isVertical = await statsGrid.evaluate((el) => {
      const computedStyle = window.getComputedStyle(el);
      return computedStyle.gridTemplateColumns.includes('1fr');
    });

    expect(isVertical).toBeTruthy();
  });
});
