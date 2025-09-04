import { GoogleGenerativeAI } from '@google/generative-ai';
import { chromium } from 'playwright';

export class AgentRuntime {
    constructor(apiKey) {
        const genAI = new GoogleGenerativeAI(apiKey);
        this.model = genAI.getGenerativeModel({ model: "gemini-1.5-pro-latest" });
    }

    async runTask(task) {
        const prompt = `
You are an autonomous AI agent. Your job is to complete tasks without further input unless absolutely stuck.
Be concise, proactive, and resourceful.

Task: ${task}

Respond with:
- "ACTION: browseWeb - [url] - [query]" to browse the web
- "FINAL ANSWER: [response]" when done
- "NEEDS INPUT: [question]" only if critical
        `;

        try {
            const result = await this.model.generateContent(prompt);
            const response = await result.response;
            const text = response.text();

            // Check if agent wants to browse the web
            const actionMatch = text.match(/ACTION: browseWeb - (.+?) - (.+)/);
            if (actionMatch) {
                const url = actionMatch[1].trim();
                const query = actionMatch[2].trim();
                const webResult = await this.browseWeb(url, query);
                return { output: webResult, success: true };
            }

            return { output: text, success: true };
        } catch (error) {
            return { output: `Error: ${error.message}`, success: false };
        }
    }

    async browseWeb(url, query) {
        const browser = await chromium.launch();
        const page = await browser.newPage();
        await page.goto(url);
        await page.waitForTimeout(2000);

        const content = await page.evaluate(() => {
            return document.body.innerText.slice(0, 10000);
        });

        await browser.close();

        const prompt = `Based on this text, answer: ${query}\n\nText: ${content}`;
        const result = await this.model.generateContent(prompt);
        const response = await result.response;
        return response.text();
    }
}
