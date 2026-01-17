/**
 * E2E Tests for Authentication Flow
 *
 * Tests user registration, login, and logout
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Start from the home page
    await page.goto('/');
  });

  test('should display landing page', async ({ page }) => {
    await expect(page).toHaveTitle(/NARRA_FORGE/);
    await expect(page.getByText('AI-Powered Narrative')).toBeVisible();
    await expect(page.getByText('Generation Platform')).toBeVisible();
  });

  test('should navigate to registration page', async ({ page }) => {
    await page.click('text=Get Started');
    await expect(page).toHaveURL(/\/register/);
    await expect(page.getByText('Create your account')).toBeVisible();
  });

  test('should register new user successfully', async ({ page }) => {
    const timestamp = Date.now();
    const email = `test${timestamp}@example.com`;
    const password = 'TestPass123';

    // Navigate to register page
    await page.goto('/register');

    // Fill registration form
    await page.fill('input[type="email"]', email);
    await page.fill('input[id="password"]', password);
    await page.fill('input[id="confirmPassword"]', password);
    await page.check('input[type="checkbox"]'); // Accept terms

    // Submit form
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
    await expect(page.getByText('Welcome back')).toBeVisible();
  });

  test('should show error for weak password', async ({ page }) => {
    await page.goto('/register');

    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[id="password"]', 'weak');
    await page.fill('input[id="confirmPassword"]', 'weak');
    await page.check('input[type="checkbox"]');

    await page.click('button[type="submit"]');

    // Should show error message
    await expect(page.getByText(/at least 8 characters/i)).toBeVisible();
  });

  test('should show error for mismatched passwords', async ({ page }) => {
    await page.goto('/register');

    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[id="password"]', 'TestPass123');
    await page.fill('input[id="confirmPassword"]', 'DifferentPass123');
    await page.check('input[type="checkbox"]');

    await page.click('button[type="submit"]');

    // Should show error
    await expect(page.getByText(/do not match/i)).toBeVisible();
  });

  test('should login existing user', async ({ page }) => {
    // First register a user
    const timestamp = Date.now();
    const email = `login${timestamp}@example.com`;
    const password = 'LoginPass123';

    await page.goto('/register');
    await page.fill('input[type="email"]', email);
    await page.fill('input[id="password"]', password);
    await page.fill('input[id="confirmPassword"]', password);
    await page.check('input[type="checkbox"]');
    await page.click('button[type="submit"]');

    // Wait for redirect
    await page.waitForURL(/\/dashboard/);

    // Logout
    await page.click('button:has-text("Menu")').catch(() => {
      // Click user avatar/menu
      page.click('[role="button"]:has-text("U")');
    });
    await page.click('text=Log out');

    // Should return to home
    await expect(page).toHaveURL('/', { timeout: 5000 });

    // Now login
    await page.goto('/login');
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', password);
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByText('Welcome back')).toBeVisible();
  });

  test('should show error for wrong password', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[type="email"]', 'nonexistent@example.com');
    await page.fill('input[type="password"]', 'WrongPass123');
    await page.click('button[type="submit"]');

    // Should show error
    await expect(page.getByText(/incorrect|not found/i)).toBeVisible();
  });

  test('should protect dashboard from unauthenticated access', async ({ page, context }) => {
    // Clear all cookies
    await context.clearCookies();

    // Clear localStorage
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());

    // Try to access dashboard
    await page.goto('/dashboard');

    // Should redirect to login
    await expect(page).toHaveURL(/\/login/, { timeout: 5000 });
  });

  test('should maintain session across page refreshes', async ({ page }) => {
    // Register and login
    const timestamp = Date.now();
    const email = `session${timestamp}@example.com`;
    const password = 'SessionPass123';

    await page.goto('/register');
    await page.fill('input[type="email"]', email);
    await page.fill('input[id="password"]', password);
    await page.fill('input[id="confirmPassword"]', password);
    await page.check('input[type="checkbox"]');
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/dashboard/);

    // Refresh page
    await page.reload();

    // Should still be on dashboard
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByText('Welcome back')).toBeVisible();
  });

  test('should logout successfully', async ({ page }) => {
    // Register user
    const timestamp = Date.now();
    const email = `logout${timestamp}@example.com`;
    const password = 'LogoutPass123';

    await page.goto('/register');
    await page.fill('input[type="email"]', email);
    await page.fill('input[id="password"]', password);
    await page.fill('input[id="confirmPassword"]', password);
    await page.check('input[type="checkbox"]');
    await page.click('button[type="submit"]');

    await page.waitForURL(/\/dashboard/);

    // Logout - try to find and click the user menu/logout button
    try {
      await page.click('button[aria-haspopup="menu"]', { timeout: 5000 });
    } catch {
      await page.click('button:has-text("U")', { timeout: 5000 });
    }

    await page.click('text=Log out');

    // Should redirect to home
    await expect(page).toHaveURL('/', { timeout: 5000 });

    // Try to access dashboard
    await page.goto('/dashboard');

    // Should redirect to login
    await expect(page).toHaveURL(/\/login/);
  });

  test('should toggle dark mode', async ({ page }) => {
    await page.goto('/');

    // Find theme toggle button
    const themeButton = page.locator('button').filter({ hasText: /theme|dark|light/i }).first();

    if (await themeButton.count() > 0) {
      await themeButton.click();

      // Check if dark class is added to html or body
      const isDark = await page.evaluate(() => {
        return document.documentElement.classList.contains('dark') ||
               document.body.classList.contains('dark');
      });

      expect(isDark).toBeTruthy();
    }
  });
});
