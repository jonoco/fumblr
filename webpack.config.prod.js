var webpack = require('webpack');
var path = require('path');
var autoprefixer = require('autoprefixer');
var PATHS = {
  nodeModules: path.resolve(__dirname, 'node_modules'),
  dist: path.resolve(__dirname, 'fumblr', 'static', 'js'),
  main: path.resolve(__dirname, 'fumblr', 'src', 'js', 'index'),
  src: path.resolve(__dirname, 'fumblr', 'src'),
  fonts: path.resolve(__dirname, 'fumblr', 'static', 'fonts')
};

module.exports = {
  entry: PATHS.main,
  output: {
    path: PATHS.dist,
    filename: 'bundle.js'
  },
  module: {
    loaders: [
      { 
        exclude: [PATHS.nodeModules], 
        test: /\.js?$/, 
        loader: 'babel', 
      }
    ],
    query: { presets: ['es2015'] }
  },
  resolve: {
    extensions: ['', '.js']
  },
  plugins: [
    new webpack.optimize.OccurenceOrderPlugin(),
    new webpack.optimize.DedupePlugin(),
    new webpack.DefinePlugin({
      'process.env': {
        'NODE_ENV': JSON.stringify('production')
      }
    }),
    new webpack.optimize.UglifyJsPlugin({
      sourceMap: false,
      compress: {
        warnings: false
      },
      output: {
        comments: false
      }
    })
  ]
}