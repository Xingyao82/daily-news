#!/usr/bin/env node
/**
 * Browser Control Tool for OpenClaw
 * 浏览器控制工具 - 支持无头浏览器自动化
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const STATE_FILE = '/tmp/browser-control-state.json';
let browser = null;
let context = null;
let page = null;

async function saveState(state) {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function loadState() {
    try {
        return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    } catch {
        return { status: 'stopped', url: null };
    }
}

async function startBrowser() {
    if (browser) {
        console.log('⚠️  浏览器已在运行');
        return;
    }
    
    console.log('🚀 启动浏览器...');
    browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    context = await browser.newContext({
        viewport: { width: 1920, height: 1080 },
        userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    });
    
    page = await context.newPage();
    
    await saveState({ status: 'running', url: null });
    console.log('✅ 浏览器已启动');
}

async function navigate(url) {
    if (!page) {
        console.log('❌ 浏览器未启动，请先运行 start');
        return;
    }
    
    console.log(`🌐 导航到: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await saveState({ status: 'running', url: url });
    console.log('✅ 导航完成');
}

async function takeScreenshot(outputPath = '/tmp/browser-screenshot.png') {
    if (!page) {
        console.log('❌ 浏览器未启动');
        return;
    }
    
    console.log('📸 截图中...');
    await page.screenshot({ 
        path: outputPath, 
        fullPage: true 
    });
    console.log(`✅ 截图已保存: ${outputPath}`);
}

async function getSnapshot() {
    if (!page) {
        console.log('❌ 浏览器未启动');
        return;
    }
    
    console.log('📄 获取页面快照...');
    const title = await page.title();
    const url = page.url();
    const content = await page.content();
    
    console.log(`标题: ${title}`);
    console.log(`URL: ${url}`);
    console.log(`内容长度: ${content.length} 字符`);
    
    // 保存内容到文件
    fs.writeFileSync('/tmp/browser-content.html', content);
    console.log('✅ 内容已保存到 /tmp/browser-content.html');
}

async function getStatus() {
    const state = loadState();
    console.log('📊 浏览器状态:');
    console.log(`  状态: ${state.status}`);
    console.log(`  当前URL: ${state.url || 'N/A'}`);
    console.log(`  进程: ${browser ? '运行中' : '未启动'}`);
}

async function stopBrowser() {
    if (browser) {
        console.log('🛑 关闭浏览器...');
        await browser.close();
        browser = null;
        context = null;
        page = null;
        await saveState({ status: 'stopped', url: null });
        console.log('✅ 浏览器已关闭');
    } else {
        console.log('⚠️  浏览器未运行');
    }
}

async function main() {
    const command = process.argv[2];
    const arg = process.argv[3];
    
    switch (command) {
        case 'start':
            await startBrowser();
            break;
        case 'navigate':
            await navigate(arg);
            break;
        case 'screenshot':
            await takeScreenshot(arg);
            break;
        case 'snapshot':
            await getSnapshot();
            break;
        case 'status':
            await getStatus();
            break;
        case 'stop':
            await stopBrowser();
            break;
        default:
            console.log('🦞 Browser Control Tool');
            console.log('');
            console.log('用法: browser-control.js <command> [args]');
            console.log('');
            console.log('命令:');
            console.log('  start                    启动浏览器');
            console.log('  navigate <url>          导航到指定URL');
            console.log('  screenshot [path]       截图 (默认: /tmp/browser-screenshot.png)');
            console.log('  snapshot                获取页面内容快照');
            console.log('  status                  查看浏览器状态');
            console.log('  stop                    关闭浏览器');
            console.log('');
            console.log('示例:');
            console.log('  browser-control.js start');
            console.log('  browser-control.js navigate https://www.google.com');
            console.log('  browser-control.js screenshot /tmp/google.png');
            console.log('  browser-control.js snapshot');
            console.log('  browser-control.js stop');
    }
}

main().catch(err => {
    console.error('❌ 错误:', err.message);
    process.exit(1);
});
