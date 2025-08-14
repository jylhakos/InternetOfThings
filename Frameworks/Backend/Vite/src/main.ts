import './styles/main.css';
import { setupApp } from './app';

console.log('Vite app starting...');

// Setup the main application
document.addEventListener('DOMContentLoaded', () => {
  setupApp();
});

// Hot Module Replacement (HMR)
if (import.meta.hot) {
  import.meta.hot.accept('./app', (newModule) => {
    if (newModule) {
      console.log('HMR: App module updated');
      newModule.setupApp();
    }
  });

  import.meta.hot.dispose(() => {
    console.log('HMR: Disposing old module');
  });
}
