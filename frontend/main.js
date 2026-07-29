const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow () {
  const win = new BrowserWindow({
    width: 900,
    height: 700,
    title: "AI Assistant",
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // Yeh load karega humari frontend UI file ko
  win.loadFile('index.html');
  // Window load hone ke turant baad Console automatically khul jayega
win.webContents.openDevTools();
  // Menu bar hide karne ke liye (clean look ke liye)
  win.setMenuBarVisibility(false);
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});