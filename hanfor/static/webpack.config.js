const webpack = require('webpack');

const config = {
    entry: {
        requirements: __dirname + '/js/requirements.js',
        variables: __dirname + '/js/variables.js',
        stats: __dirname + '/js/stats.js',
        tags: __dirname + '/js/tags.js',
    },
    output: {
        path: __dirname + '/dist',
        filename: '[name]-bundle.js',
    },
    resolve: {
        extensions: ['.js', '.jsx', '.css']
    },
    plugins: [
        new webpack.ProvidePlugin({
          $: 'jquery',
          jQuery: 'jquery'
        })
    ],
};

module.exports = config;
