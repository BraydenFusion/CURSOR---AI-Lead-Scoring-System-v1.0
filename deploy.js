// Run this script from your local terminal, not inside Cursor.
// Requires a valid .env file and local network access.

import { execSync } from "child_process";
import { appendFileSync } from "fs";
import dotenv from "dotenv";
import fetch from "node-fetch";

const LOG_FILE = "deploy.log";

const formatTimestamp = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const seconds = String(now.getSeconds()).padStart(2, "0");
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

const writeLog = (message, success = true) => {
  const status = success ? "✅" : "❌";
  const line = `[${formatTimestamp()}] ${status} ${message}`;
  console.log(line);
  appendFileSync(LOG_FILE, `${line}\n`, { encoding: "utf-8" });
};

const runCommand = (command, description) => {
  try {
    writeLog(`Starting ${description}...`);
    execSync(command, { stdio: "inherit" });
    writeLog(`${description} completed`);
  } catch (error) {
    writeLog(`${description} failed - ${error.message}`, false);
    throw error;
  }
};

const main = async () => {
  try {
    dotenv.config();
    writeLog("Environment variables loaded");

    runCommand("git add .", "Git add");
    runCommand('git commit -m "auto commit"', "Git commit");
    runCommand("git push origin main", "Git push");

    const hookUrl = process.env.DEPLOY_HOOK_URL;
    if (!hookUrl) {
      throw new Error("DEPLOY_HOOK_URL is not set in the environment");
    }

    const payload = {
      branch: "main",
      status: "pushed",
      timestamp: new Date().toISOString(),
    };

    writeLog("Sending deploy webhook...");
    const response = await fetch(hookUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const body = await response.text();
      throw new Error(`Webhook responded with ${response.status}: ${body}`);
    }

    writeLog(`Node webhook POST success (${response.status})`);
    writeLog("Code pushed successfully!");
  } catch (error) {
    writeLog(`Deployment failed - ${error.message}`, false);
    throw error;
  }
};

main().catch(() => process.exit(1));

