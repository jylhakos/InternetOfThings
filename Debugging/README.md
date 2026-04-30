# Debugging

Debugging is the process of analyzing, and removing errors from software. Visual Studio Code provides rich built-in debugging support for JavaScript, TypeScript, and Node.js, and extends to Python, Java, and many other languages through extensions from the Visual Studio Marketplace. The debugger integrates directly into the editor workflow, enabling developers to set breakpoints, inspect variables, step through code, and evaluate expressions without leaving VS Code. See [Debug code with Visual Studio Code](https://code.visualstudio.com/docs/debugtest/debugging) for a full overview.

---

## Folder Structure

```
◈ Debugging/
  ▸ GDB/
  │   ▪ README.md
  ▸ Java/
  │   ▪ README.md
  ▸ JavaScript/
  │   ▪ README.md
  ▸ Python/
  │   ▪ README.md
  ▸ Sentry/
  │   ▪ README.md
  ▸ TypeScript/
  │   ▪ README.md
  ▪ README.md
```

---

## Debugger User Interface in VS Code

VS Code organizes debugging into five main areas:

- **Run and Debug view** - displays all information related to running and debugging, and manages debug configuration settings.
- **Debug toolbar** - contains buttons for the most common debugging actions (Continue, Step Over, Step Into, Step Out, Restart, Stop).
- **Debug console** - enables viewing and interacting with output from code running in the debugger.
- **Debug sidebar** - during a session, lets you interact with the call stack, breakpoints, variables, and watch expressions.
- **Run menu** - provides the most common run and debug commands.

---

## Debugging Actions

These actions are common across all supported languages in VS Code:

| Action | Shortcut | Description |
|---|---|---|
| Set Breakpoint | Click gutter / F9 | Pause execution at a specific line. A red circle appears in the editor margin. |
| Start Debugging | F5 | Launch the active debug configuration or auto-detect the current file. |
| Continue / Pause | F5 | Resume normal execution up to the next breakpoint, or pause at the current line. |
| Step Over | F10 | Execute the next statement without entering called functions. |
| Step Into | F11 | Enter the next function call to follow its execution line by line. |
| Step Out | Shift+F11 | Complete the current function and return to the calling context. |
| Restart | Ctrl+Shift+F5 | Terminate and restart the current debug session. |
| Stop | Shift+F5 | Terminate the current debug session. |

### Breakpoint Types

VS Code supports several breakpoint variants beyond simple line breakpoints:

- **Conditional breakpoints** - pause only when an expression evaluates to true, or after a specified hit count.
- **Triggered breakpoints** - automatically activate once another breakpoint is hit, useful for diagnosing precondition failures.
- **Inline breakpoints** - set at a specific column within a line, useful when debugging minified code with multiple statements per line (Shift+F9).
- **Function breakpoints** - break when a named function is called, even when source is unavailable.
- **Data breakpoints** - break when the value of a variable changes, is read, or is accessed (shown as a red hexagon in the BREAKPOINTS section).
- **Logpoints** - log a message to the Debug Console without pausing execution. Expressions inside `{}` are evaluated inline.

### Data Inspection

While paused, hover over any variable in the editor to see its value. The **VARIABLES** and **WATCH** sections in the Run and Debug view show all in-scope variables and custom expressions relative to the selected stack frame. The **Debug Console REPL** (Ctrl+Shift+Y) allows evaluating arbitrary expressions against the live program state. To filter variables, use Ctrl+Alt+F while focused on the VARIABLES section.

---

## TypeScript Debugging

Visual Studio Code supports TypeScript debugging through its built-in [Node.js debugger](https://code.visualstudio.com/docs/nodejs/nodejs-debugging) and [Edge and Chrome debugger](https://code.visualstudio.com/docs/nodejs/browser-debugging). See [Debugging TypeScript](https://code.visualstudio.com/docs/typescript/typescript-debugging) for the full reference.

### Source Maps

TypeScript compiles to JavaScript, so VS Code relies on source maps to map breakpoints in `.ts` files back to the running `.js` output. Enable source maps in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES5",
    "module": "CommonJS",
    "outDir": "out",
    "sourceMap": true
  }
}
```

For advanced scenarios, create a `.vscode/launch.json` file (Run and Debug view > "create a launch.json file") to specify the program entry, pre-launch build task, and output file locations:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Launch Program",
      "program": "${workspaceFolder}/helloworld.ts",
      "preLaunchTask": "tsc: build - tsconfig.json",
      "outFiles": ["${workspaceFolder}/out/**/*.js"]
    }
  ]
}
```

If source maps exist but breakpoints appear as gray hollow circles, run the **Debug: Diagnose Breakpoint Problems** command (Ctrl+Shift+P) to identify the mapping issue.

### Client-Side Debugging

TypeScript is well-suited for client-side code as well as Node.js applications. You can debug client-side TypeScript using the built-in Edge or Chrome debugger by creating a launch configuration of type `msedge` or `chrome` and pointing `url` to your HTML file or local dev server. Open the `.ts` source file, set a breakpoint, and press F5 to launch the browser and hit the breakpoint directly in the TypeScript source.

### Running TypeScript with a Runner

For running TypeScript directly without a manual compile step, Node.js supports two popular runtime wrappers. See [Running TypeScript with a runner](https://nodejs.org/learn/typescript/run) for details.

**ts-node** - executes TypeScript files directly and performs type checking by default:

```bash
npm install -D ts-node typescript
npx ts-node example.ts

# Debug mode using Node's --inspect flag
node --inspect -r ts-node/register your-script.ts
```

**tsx** - a faster TypeScript execution environment that skips type checking (run `tsc` separately to validate types):

```bash
npm install -D tsx
npx tsx example.ts

# Or register via node
node --import=tsx example.ts
```

---

## JavaScript Debugging

VS Code includes a built-in JavaScript debugger that supports Node.js, Chrome, Edge, and other environments without any additional extensions. See [JavaScript Debugging Recipes](https://code.visualstudio.com/docs/nodejs/debugging-recipes) for a curated collection of setup guides covering Angular, Next.js, Vue.js, Meteor, Mocha, Jest, Electron, and more.

### Key Features

- **Auto Attach** - when enabled via the Command Palette (Toggle Auto Attach), VS Code automatically attaches the debugger to Node.js processes started from the integrated terminal. Three modes are available: `smart` (attaches to scripts outside `node_modules` and known runners), `always`, and `onlyWithFlag` (requires `--inspect` or `--inspect-brk`).
- **JavaScript Debug Terminal** - create a dedicated terminal (Debug: Create JavaScript Debug Terminal) that automatically debugs any Node.js process launched inside it.
- **Conditional and Logpoint breakpoints** - right-click the editor gutter to create a conditional breakpoint or logpoint. Logpoints use `{expression}` syntax to interpolate values inline in the Debug Console.
- **skipFiles** - configure `"skipFiles"` in `launch.json` to skip stepping through `node_modules`, library code, or Node.js internals (`<node_internals>/**`).

---

## Node.js Debugging

VS Code has built-in debugging support for the Node.js runtime. It can debug JavaScript, TypeScript, and any language that transpiles to JavaScript. See [Node.js debugging in VS Code](https://code.visualstudio.com/docs/nodejs/nodejs-debugging) for the complete reference.

### Attaching to a Running Process

Start Node.js in inspect mode, then attach VS Code:

```bash
node --inspect program.js

# Break immediately on start and wait for debugger to attach
node --inspect-brk program.js
```

Use the **Attach to Node Process** command (Ctrl+Shift+P) to select the running process from a picker, or configure an explicit attach entry in `launch.json`:

```json
{
  "name": "Attach to Process",
  "type": "node",
  "request": "attach",
  "port": 9229
}
```

### Nodemon Integration

[Nodemon](https://nodemon.io/) monitors source files for changes and automatically restarts the Node.js process. VS Code's Node debugger supports auto-reattachment after a restart. See the [Node.js debugging in VS Code with Nodemon](https://github.com/microsoft/vscode-recipes/tree/main/nodemon) recipe for a working setup.

Start nodemon from the command line:

```bash
nodemon --inspect server.js
```

Then attach VS Code with `"restart": true` to automatically reconnect after each nodemon-triggered restart:

```json
{
  "name": "Attach to node",
  "type": "node",
  "request": "attach",
  "restart": true,
  "port": 9229
}
```

Alternatively, launch nodemon directly from VS Code as the `runtimeExecutable`:

```json
{
  "name": "Launch server.js via nodemon",
  "type": "node",
  "request": "launch",
  "runtimeExecutable": "nodemon",
  "program": "${workspaceFolder}/server.js",
  "console": "integratedTerminal",
  "internalConsoleOptions": "neverOpen"
}
```

### Source Maps for Node.js

Enable source maps in TypeScript with `--sourceMap` or `"sourceMap": true` in `tsconfig.json`. For Webpack, set `devtool: "source-map"` in `webpack.config.js`. Use `outFiles` in `launch.json` to guide VS Code to the generated JavaScript when running transpiled code:

```json
"outFiles": ["${workspaceFolder}/bin/**/*.js"]
```

The `smartStep` attribute skips over generated helper code (such as async/await downcompilation from TypeScript) that has no corresponding source map entry.

---

## Python Debugging

Visual Studio provides a debugging environment for Python. See [Debug your Python code in Visual Studio](https://learn.microsoft.com/en-us/visualstudio/python/debugging-python-in-visual-studio?view=visualstudio) and the [Tutorial: Run code in the Visual Studio Debugger](https://learn.microsoft.com/en-us/visualstudio/python/tutorial-working-with-python-in-visual-studio-step-04-debugging?view=visualstudio) for full guidance.

### Setup

No project file is required to debug a standalone Python script. Open the file in Visual Studio and select **Debug > Start Debugging** (F5). Visual Studio launches the script using the active Python environment. For project-based workflows, right-click the file in Solution Explorer and select **Set as Startup Item**, then configure debug properties via right-click > Properties > Debug tab.

### Setting Breakpoints

Click in the left margin (gutter) next to the line number, or press F9. A red dot confirms the breakpoint is set. For conditional breakpoints, right-click the red dot and select **Conditions** to enter a Python expression (for example, `i > 100`) or hit count. Breakpoint actions (tracepoints) allow logging messages to the Output window without stopping execution.

### Stepping Through Code

| Command | Shortcut | Description |
|---|---|---|
| Continue | F5 | Run to the next breakpoint. |
| Step Into | F11 | Enter the next function call. |
| Step Over | F10 | Execute the next statement, skipping into called functions. |
| Step Out | Shift+F11 | Run to the end of the current function and return to caller. |
| Run to Cursor | Ctrl+F10 | Run code to the current caret position. |
| Set Next Statement | Ctrl+Shift+F10 | Skip directly to the line at the cursor. |

### Inspecting Values

- **Hover (DataTips)** - hover over any variable in the editor during a debug session to see its current value. Click the value to edit it inline.
- **Locals window** (Debug > Windows > Locals) - displays all variables in the current scope.
- **Autos window** (Debug > Windows > Autos) - shows variables and expressions near the current statement.
- **Watch window** (Debug > Windows > Watch) - enter arbitrary Python expressions; they are re-evaluated at each step.
- **Python Debug Interactive window** (Shift+Alt+I) - a full REPL connected to the running process, supporting meta-commands such as `$step`, `$stepout`, `$frame`, and `$threads`.

### Exceptions

When an unhandled exception occurs, the debugger pauses at the point of the error and shows the current call stack. Configure which exceptions break execution via **Debug > Windows > Exception Settings**. Add custom exceptions by entering their fully qualified name.

---

## Java Debugging

Java debugging in VS Code is supported through the **Debugger for Java** extension, which provides integration with the Java Debug Server. See [Running and debugging Java](https://code.visualstudio.com/docs/java/java-debugging) for setup instructions. The JDK also ships the command-line [Java Debugger (jdb)](https://docs.oracle.com/javase/7/docs/technotes/tools/windows/jdb.html) for debugging without an IDE.

Essential tools include:

- **IDEs** - VS Code with the Java Extension Pack, Eclipse, and IntelliJ IDEA all provide graphical debuggers with breakpoint management, variable inspection, and hot code replace.
- **jdb (Java Debugger)** - included in the JDK, it supports attaching to running JVMs, setting breakpoints by class and method, evaluating expressions, and inspecting threads.
- **Logging frameworks** - Log4j, SLF4J, and `java.util.logging` supplement debuggers by providing structured runtime output and trace-level diagnostics.

---

## Vibe Coding and AI Agents in Debugging with VS Code

In Visual Studio Code, Vibe Coding and AI Agents shift debugging from manual line-by-line inspection to a high-level, conversational workflow.

### Vibe Coding in Debugging

Vibe coding is a development practice coined by AI researcher Andrej Karpathy that describes a workflow where the primary role shifts from writing code line-by-line to guiding an AI assistant through a conversational process. Instead of manually writing specific commands or syntax, the developer focuses on high-level intent and desired outcomes. See [Understanding how the vibe coding process works](https://cloud.google.com/discover/what-is-vibe-coding) for a detailed breakdown.

Applied to debugging, vibe coding changes the workflow in the following ways:

- **Intent-Based Debugging** - instead of manually setting breakpoints and tracing execution, you describe the buggy behavior to an AI. For example, telling a tool to "fix why the login button does not respond on mobile" allows it to diagnose the issue across multiple files without you navigating the call stack yourself.
- **Conversational Refinement** - the debugging loop becomes: describe the symptom, observe the AI's diagnosis, provide feedback ("that works but it still fails when the input is empty"), and repeat. Error handling is guided by conversational feedback rather than manual code comprehension.
- **Responsible AI-Assisted Development** - in professional workflows, AI tools act as a pair programmer. The developer guides the AI and then reviews, tests, and takes ownership of the proposed fix rather than blindly accepting it.

The code-level workflow follows five steps: describe the goal in plain language, let the AI generate a fix, execute and observe the result, provide refined feedback, and repeat until the bug is resolved.

### Vibe Debugging

"Vibe debugging" is the essential counterpart to vibe coding. While vibe coding focuses on building software through natural language descriptions, vibe debugging applies the same conversational, intent-driven approach to the process of finding and fixing defects. The developer's role shifts from manual line-by-line tracing to high-level guidance of an AI agent. A practical example from the Microsoft Developer Blog illustrates this directly: rather than manually tracing CSV parsing logic, the developer simply described the symptom — "double check the CSV parsing, doesn't seem correct here as the numbers aren't accurate" — and GitHub Copilot diagnosed and rewrote the parser without manual inspection of the code. See [Complete Beginner's Guide to Vibe Coding an App in 5 Minutes](https://developer.microsoft.com/blog/complete-beginners-guide-to-vibe-coding-an-app-in-5-minutes) for the full walkthrough.

The process collapses the traditional investigative loop into a fluid interaction with AI:

- **Conversational Hypothesis** - instead of manually setting breakpoints, you describe the observed issue in plain language (for example, "The dashboard is not loading data from the CSV"). The AI translates that description into a structured hypothesis about the root cause.
- **Natural Language Interaction** - instead of reading stack traces or manually tracing logs, you ask vague, symptom-level questions (for example, "Why is performance dipping?") and let the AI agent interrogate the relevant code, telemetry, or logs on your behalf.
- **Iterative Refinement** - if the first fix does not resolve the issue, you provide follow-up "vibe" feedback (for example, "It is still slow") and the AI refines its output until the behavior matches your expectations. Each iteration narrows the hypothesis space without requiring the developer to read additional code.
- **Agentic Investigation** - the AI agent proactively translates intent into tool calls. It queries live telemetry, analyzes production logs, and correlates data across silos such as GitHub repositories and Azure infrastructure, surfacing root causes that manual serial debugging might miss.

#### Tools for Vibe Debugging

- **Visual Studio and VS Code with GitHub Copilot** - GitHub Copilot Chat and Agent Mode automate tactical investigation, suggest targeted fixes, and can be invoked directly on failing tests, build errors, or pull request checks. Agent Mode is the primary surface for vibe debugging workflows in VS Code, where the developer describes a symptom and the agent handles reading files, running commands, and applying fixes.

#### The Vibe Debugging Workflow: Capture, Analyze, Resolve

The process generally follows a three-stage cycle:

**1. Capture (Reproduction and Context)**

Instead of setting manual breakpoints, the developer provides the AI with contextual traces. These can include error logs, terminal output, screenshots of the issue, or a plain-language description of the unexpected behavior. The richer the context, the more precisely the agent can scope its investigation. This stage replaces the traditional effort of isolating a reproduction case.

**2. Analyze (Parallel Exploration)**

AI agents, such as Claude Code or GitHub Copilot in Agent Mode, investigate multiple hypotheses simultaneously. They cross-reference code changes, live telemetry, and deployment history to pinpoint root causes that traditional serial debugging would require the developer to trace manually, file by file. For example, an agent can correlate a regression introduced in a recent commit with a mismatch in CSV field parsing and surface both findings in a single response.

**3. Resolve (Iterative Fixes)**

The developer guides the AI through a conversational loop: describe the expected behavior, let the agent suggest and apply a fix, then validate the result. If the fix does not fully resolve the issue, the developer provides further feedback and the cycle repeats. The agent can also be asked to insert temporary debug print statements to confirm intermediate assumptions before committing to a final change.

### AI Agents in Debugging

AI Agents in VS Code are autonomous assistants that perform multi-step debugging tasks across an entire codebase. Unlike basic chat assistants that answer single questions, agents independently read files, run terminal commands, execute tests, and self-correct until a bug is resolved. See [Using agents in Visual Studio Code](https://code.visualstudio.com/docs/copilot/agents/overview) for the full reference.

VS Code provides three built-in agent modes:

- **Agent** - autonomously plans and implements changes across files, runs terminal commands, and invokes tools to complete a debugging task end to end.
- **Plan** - creates a structured, step-by-step implementation plan before writing any code, then hands the plan off to an implementation agent.
- **Ask** - answers questions about coding concepts, the codebase, or VS Code itself without making file changes.

Key capabilities relevant to debugging:

- **Autonomous Root Cause Analysis** - agents analyze entire repositories to identify a bug's origin across multiple files, rather than suggesting a fix for a single failing line.
- **Self-Correction** - if a proposed fix fails a test, the agent automatically re-runs the tests, analyzes the new failure output, and iterates on the fix without requiring user intervention.
- **Integrated Browser Tools** - agents can open a browser directly inside VS Code to validate UI changes and inspect front-end behavior in real time, providing visual proof of fixes rather than text-only logs.
- **Permission Levels** - developers control how much autonomy agents have. The options range from approving every individual tool call, to bypassing all approvals, to full **Autopilot** mode where the agent auto-responds to questions and works uninterrupted until the task is complete.
- **Agent Handoffs** - start with a local agent for interactive exploration, hand off to the Copilot CLI for background execution, then delegate to a cloud agent to submit a pull request for team review.

#### Third-Party Agents

VS Code also supports third-party agents from external providers, enabling access to their unique capabilities while still benefiting from unified session management and the full VS Code debugging experience. See [Third-party agents in Visual Studio Code](https://code.visualstudio.com/docs/copilot/agents/third-party-agents) for setup instructions.

- **Claude Agent (Anthropic)** - powered by Anthropic's Claude Agent SDK, the Claude agent operates autonomously on your workspace to plan, execute, and iterate on coding tasks. It supports specialized slash commands (`/review`, `/security-review`, `/pr-comments`, `/memory`) and configurable permission modes (Edit Automatically, Request Approval, Plan).
- **Claude Code (CLI)** - Anthropic's Claude Code functions as a terminal-based agent that iterates continuously in an auto-accept loop, writing code and running tests until the bug is resolved.
- **OpenAI Codex** - uses OpenAI's Codex to perform coding tasks autonomously, running either interactively in VS Code or unattended in the background.

#### Inspecting Agent Behavior

When an agent produces unexpected results, VS Code provides internal tooling to understand what happened. Agent debug logs and the Chat Debug View allow developers to inspect how an agent reasoned about a problem, which tools it invoked, and at what point a decision was made. This transparency is important when using agents in security-sensitive or production codebases.

---

## References

- [Debug code with Visual Studio Code](https://code.visualstudio.com/docs/debugtest/debugging)
- [Debugging TypeScript](https://code.visualstudio.com/docs/typescript/typescript-debugging)
- [JavaScript Debugging Recipes](https://code.visualstudio.com/docs/nodejs/debugging-recipes)
- [Node.js debugging in VS Code](https://code.visualstudio.com/docs/nodejs/nodejs-debugging)
- [Node.js debugging in VS Code with Nodemon](https://github.com/microsoft/vscode-recipes/tree/main/nodemon)
- [Running TypeScript with a runner](https://nodejs.org/learn/typescript/run)
- [Debug your Python code in Visual Studio](https://learn.microsoft.com/en-us/visualstudio/python/debugging-python-in-visual-studio?view=visualstudio)
- [Tutorial: Run code in the Visual Studio Debugger](https://learn.microsoft.com/en-us/visualstudio/python/tutorial-working-with-python-in-visual-studio-step-04-debugging?view=visualstudio)
- [Running and debugging Java](https://code.visualstudio.com/docs/java/java-debugging)
- [jdb - The Java Debugger](https://docs.oracle.com/javase/7/docs/technotes/tools/windows/jdb.html)
- [Understanding how the vibe coding process works](https://cloud.google.com/discover/what-is-vibe-coding)
- [Complete Beginner's Guide to Vibe Coding an App in 5 Minutes](https://developer.microsoft.com/blog/complete-beginners-guide-to-vibe-coding-an-app-in-5-minutes)
- [Using agents in Visual Studio Code](https://code.visualstudio.com/docs/copilot/agents/overview)
- [Third-party agents in Visual Studio Code](https://code.visualstudio.com/docs/copilot/agents/third-party-agents)
