const webpack = require('webpack');
const GitRevisionPlugin = require('git-revision-webpack-plugin');
const gitRevisionPlugin = new GitRevisionPlugin({
    versionCommand: 'describe --always --tags'
});

const config = {
    entry: {
        layout_globals: __dirname + '/js/layout-globals.js',
        autocomplete: __dirname + '/js/autocomplete.js',
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
        }),
        new webpack.DefinePlugin({
            'HANFOR_VERSION': JSON.stringify(gitRevisionPlugin.version()),
            'HANFOR_COMMITHASH': JSON.stringify(gitRevisionPlugin.commithash()),
            'HANFOR_BRANCH': JSON.stringify(gitRevisionPlugin.branch()),
        })
    ],
};

module.exports = config;
