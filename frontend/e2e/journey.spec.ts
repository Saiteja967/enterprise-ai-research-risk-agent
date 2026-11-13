import {test,expect} from '@playwright/test'
test('seed to report',async({page})=>{await page.goto('/');await page.getByRole('button',{name:'Run and save research'}).click();await expect(page.getByText(/Overdue receivables changed/)).toBeVisible()})

