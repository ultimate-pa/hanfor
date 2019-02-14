const webpack = require('webpack');

const config = {
    entry: {
        layout_globals: __dirname + '/js/layout-globals.js',
        requirements: __dirname + '/js/requirements.js',
        variables: __dirname + '/js/variables.js',
        variable_import: __dirname + '/js/variable-import.js',
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
    optimization: {
        splitChunks: {
            cacheGroups: {
                commons: {
                    name: "commons",
                    chunks: "initial",
                    minChunks: 2
                }
            }
        }
    },
    plugins: [
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery'
        })
    ],
};

module.exports = config;
