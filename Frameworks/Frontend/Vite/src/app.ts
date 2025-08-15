export function setupApp(): void {
  const contentElement = document.getElementById('content');
  
  if (contentElement) {
    contentElement.innerHTML = `
      <div class="app-content">
        <h2>Development Features</h2>
        <ul>
          <li> TypeScript support with source maps</li>
          <li> Hot Module Replacement (HMR)</li>
          <li> VS Code debugging integration</li>
          <li> ESLint and Prettier configuration</li>
          <li> DevOps build pipeline ready</li>
        </ul>
        <button id="demo-button" class="demo-button">
          Click me to test debugging!
        </button>
        <div id="output" class="output"></div>
      </div>
    `;

    // Add event listeners
    const button = document.getElementById('demo-button');
    const output = document.getElementById('output');
    
    if (button && output) {
      button.addEventListener('click', () => {
        // Set a breakpoint here to test debugging
        const timestamp = new Date().toLocaleTimeString();
        const message = `Debugging works! Clicked at ${timestamp}`;
        
        console.log(message);
        output.textContent = message;
        
        // Example of error handling for debugging
        try {
          // This is a test for debugging - you can set breakpoints here
          debugExample();
        } catch (error) {
          console.error('Debug example error:', error);
          output.textContent += ` | Error: ${(error as Error).message}`;
        }
      });
    }
  }
}

function debugExample(): void {
  // Example function for debugging
  const data = {
    environment: import.meta.env.MODE,
    isDev: import.meta.env.DEV,
    isProd: import.meta.env.PROD,
    baseUrl: import.meta.env.BASE_URL
  };
  
  console.log('Environment data:', data);
  
  // Simulate some processing
  for (let i = 0; i < 3; i++) {
    console.log(`Processing step ${i + 1}`);
  }
}
