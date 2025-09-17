import { test, expect } from '@playwright/test';

test.describe('Excel Interviewer Application', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Wait for the application to load
    await page.waitForLoadState('networkidle');
  });

  test('should load the main interview interface', async ({ page }) => {
    // Check that main components are present
    await expect(page.locator('h1')).toContainText('Excel Skills Assessment');
    
    // Check for chat interface
    await expect(page.locator('[data-testid="chat-container"]')).toBeVisible();
    
    // Check for score panel
    await expect(page.locator('[data-testid="score-panel"]')).toBeVisible();
    
    // Check for progress bar
    await expect(page.locator('[data-testid="progress-bar"]')).toBeVisible();
    
    // Check for timer
    await expect(page.locator('[data-testid="timer"]')).toBeVisible();
  });

  test('should start an interview session', async ({ page }) => {
    // Look for start button or input field
    const startButton = page.locator('button:has-text("Start Interview")');
    const messageInput = page.locator('[data-testid="message-input"]');
    
    if (await startButton.isVisible()) {
      // Click start button if present
      await startButton.click();
      
      // Wait for interview to begin
      await expect(page.locator('[data-testid="chat-messages"]')).toContainText(/welcome|hello|interview/i);
    } else if (await messageInput.isVisible()) {
      // Type initial message if input is available
      await messageInput.fill('Hello, I am ready to start the Excel interview');
      await page.locator('button:has-text("Send")').click();
      
      // Wait for response
      await expect(page.locator('[data-testid="chat-messages"]')).toContainText(/welcome|great|let.*begin/i);
    }
  });

  test('should handle user input and responses', async ({ page }) => {
    // Start interview
    const messageInput = page.locator('[data-testid="message-input"]');
    const sendButton = page.locator('[data-testid="send-button"]');
    
    // Send initial message
    await messageInput.fill('I am ready to begin the assessment');
    await sendButton.click();
    
    // Wait for system response
    await page.waitForTimeout(2000);
    
    // Check that messages appear in chat
    const chatMessages = page.locator('[data-testid="chat-messages"]');
    await expect(chatMessages).toContainText(/ready/i);
    
    // Send a technical response
    await messageInput.fill('VLOOKUP is a function that searches for a value in the leftmost column and returns a value from a specified column');
    await sendButton.click();
    
    // Wait for scoring and response
    await page.waitForTimeout(3000);
    
    // Check that score updates
    const scoreDisplay = page.locator('[data-testid="current-score"]');
    await expect(scoreDisplay).toBeVisible();
  });

  test('should display real-time scoring', async ({ page }) => {
    // Check initial score display
    const scorePanel = page.locator('[data-testid="score-panel"]');
    await expect(scorePanel).toBeVisible();
    
    // Check for score components
    await expect(page.locator('[data-testid="current-score"]')).toBeVisible();
    await expect(page.locator('[data-testid="questions-answered"]')).toBeVisible();
    
    // Start interview and provide answers to see score updates
    const messageInput = page.locator('[data-testid="message-input"]');
    const sendButton = page.locator('[data-testid="send-button"]');
    
    await messageInput.fill('Ready to start');
    await sendButton.click();
    await page.waitForTimeout(2000);
    
    await messageInput.fill('=SUM(A1:A10) adds up all values in range A1 to A10');
    await sendButton.click();
    
    // Wait for scoring
    await page.waitForTimeout(4000);
    
    // Score should update from 0
    const scoreValue = await page.locator('[data-testid="current-score"]').textContent();
    expect(parseInt(scoreValue || '0')).toBeGreaterThan(0);
  });

  test('should show interview progress', async ({ page }) => {
    // Check progress bar is visible
    const progressBar = page.locator('[data-testid="progress-bar"]');
    await expect(progressBar).toBeVisible();
    
    // Initial progress should be 0
    const progressValue = await progressBar.getAttribute('value');
    expect(parseInt(progressValue || '0')).toBe(0);
    
    // Start interview
    const messageInput = page.locator('[data-testid="message-input"]');
    const sendButton = page.locator('[data-testid="send-button"]');
    
    // Answer several questions to advance progress
    const responses = [
      'I am ready to begin',
      'A cell reference like A1 refers to a specific cell',
      '=VLOOKUP(lookup_value, table_array, col_index, range_lookup)',
      '=IF(A1>10, "High", "Low") is a conditional formula'
    ];
    
    for (const response of responses) {
      await messageInput.fill(response);
      await sendButton.click();
      await page.waitForTimeout(2000);
    }
    
    // Progress should have increased
    const newProgressValue = await progressBar.getAttribute('value');
    expect(parseInt(newProgressValue || '0')).toBeGreaterThan(0);
  });

  test('should display and update timer', async ({ page }) => {
    // Check timer is visible
    const timer = page.locator('[data-testid="timer"]');
    await expect(timer).toBeVisible();
    
    // Get initial time
    const initialTime = await timer.textContent();
    
    // Wait a few seconds
    await page.waitForTimeout(3000);
    
    // Time should have changed
    const newTime = await timer.textContent();
    expect(newTime).not.toBe(initialTime);
    
    // Time format should be MM:SS
    expect(newTime).toMatch(/^\d{1,2}:\d{2}$/);
  });

  test('should handle interview completion', async ({ page }) => {
    // Mock a completed interview scenario
    // This would require the backend to support test scenarios
    
    const messageInput = page.locator('[data-testid="message-input"]');
    const sendButton = page.locator('[data-testid="send-button"]');
    
    // Simulate completing interview by sending many responses
    const responses = [
      'Ready to start',
      '=SUM(A1:A10)',
      '=VLOOKUP(A1,B:C,2,FALSE)',
      '=IF(A1>10,"High","Low")',
      '=INDEX(B:B,MATCH(A1,A:A,0))',
      'Pivot tables summarize data',
      'Conditional formatting highlights data',
      'Data validation controls input',
      'Charts visualize data trends',
      '=COUNTIF(A:A,">10")'
    ];
    
    for (let i = 0; i < responses.length; i++) {
      await messageInput.fill(responses[i]);
      await sendButton.click();
      await page.waitForTimeout(2000);
      
      // Check if interview completed
      const completionMessage = page.locator('text=/interview.*complete|summary|finished/i');
      if (await completionMessage.isVisible()) {
        // Interview completed
        await expect(completionMessage).toBeVisible();
        
        // Check for final score display
        await expect(page.locator('[data-testid="final-score"]')).toBeVisible();
        
        // Check for summary report
        await expect(page.locator('[data-testid="interview-summary"]')).toBeVisible();
        break;
      }
    }
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check that interface adapts to mobile
    const chatContainer = page.locator('[data-testid="chat-container"]');
    await expect(chatContainer).toBeVisible();
    
    const scorePanel = page.locator('[data-testid="score-panel"]');
    await expect(scorePanel).toBeVisible();
    
    // Check that input is still usable
    const messageInput = page.locator('[data-testid="message-input"]');
    await expect(messageInput).toBeVisible();
    
    // Test touch interaction
    await messageInput.fill('Testing mobile interface');
    const sendButton = page.locator('[data-testid="send-button"]');
    await sendButton.click();
    
    await page.waitForTimeout(2000);
    
    // Verify response appears
    const chatMessages = page.locator('[data-testid="chat-messages"]');
    await expect(chatMessages).toContainText(/testing/i);
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Start interview
    const messageInput = page.locator('[data-testid="message-input"]');
    const sendButton = page.locator('[data-testid="send-button"]');
    
    await messageInput.fill('Ready to start');
    await sendButton.click();
    await page.waitForTimeout(2000);
    
    // Simulate network failure
    await page.route('**/api/**', route => route.abort());
    
    // Try to send message
    await messageInput.fill('This should fail');
    await sendButton.click();
    
    // Should show error message
    await expect(page.locator('text=/error|failed|connection/i')).toBeVisible();
    
    // Restore network
    await page.unroute('**/api/**');
    
    // Should be able to retry
    await messageInput.fill('Retry after error');
    await sendButton.click();
    
    // Should work again
    await page.waitForTimeout(2000);
    const chatMessages = page.locator('[data-testid="chat-messages"]');
    await expect(chatMessages).toContainText(/retry/i);
  });

  test('should validate input properly', async ({ page }) => {
    const messageInput = page.locator('[data-testid="message-input"]');
    const sendButton = page.locator('[data-testid="send-button"]');
    
    // Try to send empty message
    await sendButton.click();
    
    // Should show validation message or button should be disabled
    const isEmpty = await messageInput.inputValue();
    expect(isEmpty).toBe('');
    
    // Send should be disabled or show error
    const isDisabled = await sendButton.isDisabled();
    if (!isDisabled) {
      // Check for error message
      await expect(page.locator('text=/please.*enter|empty.*message/i')).toBeVisible();
    }
    
    // Valid input should work
    await messageInput.fill('Valid input text');
    await expect(sendButton).toBeEnabled();
    
    await sendButton.click();
    await page.waitForTimeout(1000);
    
    // Message should be sent
    expect(await messageInput.inputValue()).toBe('');
  });

  test('should maintain chat history', async ({ page }) => {
    const messageInput = page.locator('[data-testid="message-input"]');
    const sendButton = page.locator('[data-testid="send-button"]');
    const chatMessages = page.locator('[data-testid="chat-messages"]');
    
    // Send multiple messages
    const testMessages = [
      'First message',
      'Second message', 
      'Third message'
    ];
    
    for (const message of testMessages) {
      await messageInput.fill(message);
      await sendButton.click();
      await page.waitForTimeout(1500);
    }
    
    // All messages should be visible in chat history
    for (const message of testMessages) {
      await expect(chatMessages).toContainText(message);
    }
    
    // Chat should be scrollable if many messages
    const chatHeight = await chatMessages.evaluate(el => el.scrollHeight);
    const visibleHeight = await chatMessages.evaluate(el => el.clientHeight);
    
    if (chatHeight > visibleHeight) {
      // Should be able to scroll
      await chatMessages.evaluate(el => el.scrollTop = el.scrollHeight);
      await page.waitForTimeout(500);
    }
  });
});
