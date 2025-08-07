import { exec } from 'child_process';
import { promisify } from 'util';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

/**
 * Setup script for LangGraph Taxi Booking Agent
 */
class ProjectSetup {
  constructor() {
    this.steps = [];
    this.completed = 0;
    this.failed = 0;
  }

  async log(message, type = 'info') {
    const icons = {
      info: 'ℹ️',
      success: '✅',
      error: '❌',
      warning: '⚠️',
      step: '🔄'
    };
    console.log(`${icons[type]} ${message}`);
  }

  async runStep(description, stepFn) {
    await this.log(`${description}...`, 'step');
    try {
      await stepFn();
      await this.log(`${description} completed`, 'success');
      this.completed++;
    } catch (error) {
      await this.log(`${description} failed: ${error.message}`, 'error');
      this.failed++;
      throw error;
    }
  }

  async checkDependencies() {
    await this.runStep("Checking Node.js version", async () => {
      const { stdout } = await execAsync('node --version');
      const version = stdout.trim();
      const majorVersion = parseInt(version.substring(1).split('.')[0]);
      
      if (majorVersion < 18) {
        throw new Error(`Node.js ${majorVersion} detected. Node.js 18+ required.`);
      }
      await this.log(`Node.js ${version} ✓`);
    });

    await this.runStep("Checking npm availability", async () => {
      const { stdout } = await execAsync('npm --version');
      await this.log(`npm ${stdout.trim()} ✓`);
    });
  }

  async installDependencies() {
    await this.runStep("Installing npm dependencies", async () => {
      process.chdir(projectRoot);
      const { stdout, stderr } = await execAsync('npm install', { 
        cwd: projectRoot,
        timeout: 120000 // 2 minutes timeout
      });
      
      if (stderr && !stderr.includes('WARN')) {
        throw new Error(`npm install failed: ${stderr}`);
      }
    });
  }

  async installLangGraphCLI() {
    await this.runStep("Installing LangGraph CLI", async () => {
      try {
        await execAsync('npx @langchain/langgraph-cli --version', { timeout: 30000 });
        await this.log("LangGraph CLI already available ✓");
      } catch (error) {
        // CLI not available, install it
        await execAsync('npm install -g @langchain/langgraph-cli', { timeout: 60000 });
        await this.log("LangGraph CLI installed globally ✓");
      }
    });
  }

  async setupEnvironmentFile() {
    await this.runStep("Setting up environment file", async () => {
      const envPath = join(projectRoot, '.env');
      const envExamplePath = join(projectRoot, '.env.example');

      // Create .env.example if it doesn't exist
      if (!existsSync(envExamplePath)) {
        const envExampleContent = `# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize OpenAI model
OPENAI_MODEL=gpt-3.5-turbo

# Optional: MapTiler API for real geocoding (currently using mock data)
MAPTILER_API_KEY=your_maptiler_api_key_here

# Optional: Real Taxi API keys
TAXI_API_KEY=your_taxi_api_key_here
TAXI_API_BASE_URL=https://api.taxicode.com

# LangGraph Server Configuration (for development)
LANGGRAPH_API_URL=http://localhost:2024
`;
        writeFileSync(envExamplePath, envExampleContent);
        await this.log("Created .env.example file ✓");
      }

      // Create .env if it doesn't exist
      if (!existsSync(envPath)) {
        const envExampleContent = readFileSync(envExamplePath, 'utf8');
        writeFileSync(envPath, envExampleContent);
        await this.log("Created .env file from template ✓");
        await this.log("⚠️  Please edit .env file and add your OpenAI API key", 'warning');
      } else {
        await this.log(".env file already exists ✓");
      }
    });
  }

  async validateProject() {
    await this.runStep("Validating project structure", async () => {
      const requiredFiles = [
        'package.json',
        'index.js',
        'agents/taxi-booking-agent.js',
        'tools/taxi-booking-tool.js',
        'test/test-taxi-tool.js'
      ];

      for (const file of requiredFiles) {
        const filePath = join(projectRoot, file);
        if (!existsSync(filePath)) {
          throw new Error(`Required file missing: ${file}`);
        }
      }

      await this.log("All required files present ✓");
    });
  }

  async runBasicTests() {
    await this.runStep("Running basic tool tests", async () => {
      // Test that tools can be imported
      try {
        const { taxiTools } = await import('../tools/taxi-booking-tool.js');
        if (!taxiTools || taxiTools.length === 0) {
          throw new Error("Failed to load taxi tools");
        }
        await this.log(`Loaded ${taxiTools.length} taxi tools ✓`);
      } catch (error) {
        throw new Error(`Failed to import tools: ${error.message}`);
      }
    });
  }

  async setup() {
    console.log("🚗 LangGraph Taxi Booking Agent - Setup");
    console.log("=========================================\n");

    try {
      await this.checkDependencies();
      await this.installDependencies();
      await this.installLangGraphCLI();
      await this.setupEnvironmentFile();
      await this.validateProject();
      await this.runBasicTests();

      console.log("\n" + "=".repeat(50));
      console.log("🎉 SETUP COMPLETED SUCCESSFULLY!");
      console.log("=".repeat(50));
      console.log("✅ Steps completed:", this.completed);
      console.log("❌ Steps failed:", this.failed);
      
      console.log("\n📋 Next Steps:");
      console.log("1. Edit .env file and add your OPENAI_API_KEY");
      console.log("2. Run: npm start (to run the demo)");
      console.log("3. Run: npm test (to run the test suite)");
      console.log("4. Run: npm run dev (to start LangGraph dev server)");
      
      console.log("\n🔗 Useful Commands:");
      console.log("• npm start          - Run the main demo");
      console.log("• npm test           - Run comprehensive tests");
      console.log("• npm run dev        - Start LangGraph development server");
      console.log("• node index.js      - Run the agent directly");
      
    } catch (error) {
      console.log("\n" + "=".repeat(50));
      console.log("❌ SETUP FAILED");
      console.log("=".repeat(50));
      console.log("Error:", error.message);
      console.log("✅ Steps completed:", this.completed);
      console.log("❌ Steps failed:", this.failed + 1);
      
      console.log("\n💡 Troubleshooting:");
      console.log("• Make sure you have Node.js 18+ installed");
      console.log("• Check your internet connection");
      console.log("• Try running: npm cache clean --force");
      console.log("• For permission issues, try: sudo npm install -g @langchain/langgraph-cli");
      
      process.exit(1);
    }
  }
}

// Run setup if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const setup = new ProjectSetup();
  await setup.setup();
}
