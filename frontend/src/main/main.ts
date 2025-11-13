import { app, BrowserWindow, ipcMain, Menu, shell, dialog } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import Store from 'electron-store'
import log from 'electron-log'
import { autoUpdater } from 'electron-updater'

// 配置日志
log.transports.file.level = 'info'
log.info('应用启动')

// 初始化配置存储
const store = new Store()

class Application {
  private mainWindow: BrowserWindow | null = null

  constructor() {
    this.initializeApp()
  }

  private initializeApp(): void {
    // 设置应用用户模型ID (Windows)
    app.setAppUserModelId('com.xiaoyaosearch.app')

    // 开发环境下默认打开或关闭DevTools
    app.whenReady().then(() => {
      // 设置应用用户模型ID
      electronApp.setAppUserModelId('com.xiaoyaosearch.app')

      // 开发环境下默认打开DevTools
      app.on('browser-window-created', (_, window) => {
        optimizer.watchWindowShortcuts(window)
      })

      // 创建主窗口
      this.createWindow()

      app.on('activate', () => {
        // macOS上，当点击dock图标并且没有其他窗口打开时重新创建窗口
        if (BrowserWindow.getAllWindows().length === 0) this.createWindow()
      })
    })

    // 当所有窗口关闭时退出应用 (Windows & Linux)
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') app.quit()
    })

    // 安全设置
    app.on('web-contents-created', (_, contents) => {
      contents.on('new-window', (event, navigationUrl) => {
        event.preventDefault()
        shell.openExternal(navigationUrl)
      })
    })
  }

  private createWindow(): void {
    // 创建浏览器窗口
    this.mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 800,
      minHeight: 600,
      show: false,
      autoHideMenuBar: true,
      icon: join(__dirname, '../../assets/icon.png'),
      webPreferences: {
        preload: join(__dirname, '../preload/index.js'),
        sandbox: false,
        contextIsolation: true,
        nodeIntegration: false
      }
    })

    this.mainWindow.on('ready-to-show', () => {
      this.mainWindow?.show()
    })

    this.mainWindow.webContents.setWindowOpenHandler((details) => {
      shell.openExternal(details.url)
      return { action: 'deny' }
    })

    // 根据环境加载应用
    if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
      this.mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
      this.mainWindow.webContents.openDevTools()
    } else {
      this.mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
    }

    // 设置IPC处理器
    this.setupIpcHandlers()

    // 设置菜单
    this.setupMenu()

    // 检查更新
    this.checkForUpdates()
  }

  private setupIpcHandlers(): void {
    // 应用控制
    ipcMain.handle('app:getVersion', () => {
      return app.getVersion()
    })

    ipcMain.handle('app:quit', () => {
      app.quit()
    })

    ipcMain.handle('app:minimize', () => {
      this.mainWindow?.minimize()
    })

    ipcMain.handle('app:maximize', () => {
      if (this.mainWindow?.isMaximized()) {
        this.mainWindow.unmaximize()
      } else {
        this.mainWindow?.maximize()
      }
    })

    // 窗口控制
    ipcMain.handle('window:close', () => {
      this.mainWindow?.close()
    })

    // 配置存储
    ipcMain.handle('store:get', (_, key) => {
      return store.get(key)
    })

    ipcMain.handle('store:set', (_, key, value) => {
      store.set(key, value)
    })

    ipcMain.handle('store:delete', (_, key) => {
      store.delete(key)
    })

    // 文件对话框
    ipcMain.handle('dialog:showOpenDialog', async (_, options) => {
      if (!this.mainWindow) return { canceled: true }
      return await dialog.showOpenDialog(this.mainWindow, options)
    })

    ipcMain.handle('dialog:showSaveDialog', async (_, options) => {
      if (!this.mainWindow) return { canceled: true }
      return await dialog.showSaveDialog(this.mainWindow, options)
    })
  }

  private setupMenu(): void {
    const template: Electron.MenuItemConstructorOptions[] = [
      {
        label: '文件',
        submenu: [
          {
            label: '打开文件夹',
            accelerator: 'CmdOrCtrl+O',
            click: () => {
              this.mainWindow?.webContents.send('menu:open-folder')
            }
          },
          { type: 'separator' },
          {
            label: '退出',
            accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
            click: () => {
              app.quit()
            }
          }
        ]
      },
      {
        label: '编辑',
        submenu: [
          { label: '撤销', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
          { label: '重做', accelerator: 'Shift+CmdOrCtrl+Z', role: 'redo' },
          { type: 'separator' },
          { label: '剪切', accelerator: 'CmdOrCtrl+X', role: 'cut' },
          { label: '复制', accelerator: 'CmdOrCtrl+C', role: 'copy' },
          { label: '粘贴', accelerator: 'CmdOrCtrl+V', role: 'paste' }
        ]
      },
      {
        label: '视图',
        submenu: [
          { label: '重载', accelerator: 'CmdOrCtrl+R', role: 'reload' },
          { label: '强制重载', accelerator: 'CmdOrCtrl+Shift+R', role: 'forceReload' },
          { label: '开发者工具', accelerator: 'F12', role: 'toggleDevTools' },
          { type: 'separator' },
          { label: '实际大小', accelerator: 'CmdOrCtrl+0', role: 'resetZoom' },
          { label: '放大', accelerator: 'CmdOrCtrl+Plus', role: 'zoomIn' },
          { label: '缩小', accelerator: 'CmdOrCtrl+-', role: 'zoomOut' },
          { type: 'separator' },
          { label: '全屏', accelerator: 'F11', role: 'togglefullscreen' }
        ]
      },
      {
        label: '窗口',
        submenu: [
          { label: '最小化', accelerator: 'CmdOrCtrl+M', role: 'minimize' },
          { label: '关闭', accelerator: 'CmdOrCtrl+W', role: 'close' }
        ]
      },
      {
        label: '帮助',
        submenu: [
          {
            label: '关于小遥搜索',
            click: () => {
              dialog.showMessageBox(this.mainWindow!, {
                type: 'info',
                title: '关于小遥搜索',
                message: '小遥搜索',
                detail: `版本: ${app.getVersion()}\n一个跨平台的本地文件智能搜索工具`
              })
            }
          }
        ]
      }
    ]

    const menu = Menu.buildFromTemplate(template)
    Menu.setApplicationMenu(menu)
  }

  private checkForUpdates(): void {
    if (is.dev) return

    autoUpdater.checkForUpdatesAndNotify()

    autoUpdater.on('update-available', () => {
      log.info('发现新版本')
    })

    autoUpdater.on('update-downloaded', () => {
      log.info('更新下载完成')
      dialog.showMessageBox(this.mainWindow!, {
        type: 'info',
        title: '应用更新',
        message: '新版本已下载完成',
        detail: '应用将重启以完成更新',
        buttons: ['立即重启', '稍后重启']
      }).then((result) => {
        if (result.response === 0) {
          autoUpdater.quitAndInstall()
        }
      })
    })
  }
}

// 创建应用实例
new Application()