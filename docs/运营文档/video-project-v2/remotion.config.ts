/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";
import { enableTailwind } from '@remotion/tailwind-v4';

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.overrideWebpackConfig(enableTailwind);

// 使用本地Chrome浏览器，避免下载Headless Shell
Config.setChromiumOpenGlRenderer('angle');

// 禁用使用Headless Shell，强制使用本地Chrome
Config.setBrowserExecutable(
	'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
);
