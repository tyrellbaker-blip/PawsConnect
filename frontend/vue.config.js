const path = require('path');

module.exports = {
  // Ensures dependencies are transpiled correctly
  transpileDependencies: true,

  // DevServer configuration to handle API requests in development
devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Changed port to 8000
        changeOrigin: true,
        pathRewrite: { '^/api': '' },
      }
    }
  },
};