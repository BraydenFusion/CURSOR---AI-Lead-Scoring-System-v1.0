// deploy.js

import { execSync } from "child_process";

function run(command) {
  console.log(`Running: ${command}`);
  execSync(command, { stdio: "inherit" });
}

try {
  run("git add .");
  run('git commit -m "auto commit"');
  run("git push origin main");
  console.log("✅ Code pushed successfully!");
} catch (error) {
  console.error("❌ Deployment failed:", error.message);
}

