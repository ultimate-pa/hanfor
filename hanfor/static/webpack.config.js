const webpack = require('webpack');
const path = require("path");

const config = {
    entry: {
        layout_globals: __dirname + '/js/layout-globals.js',
        requirements: __dirname + '/js/requirements.js',
        variables: __dirname + '/js/variables.js',
        variable_import: __dirname + '/js/variable-import.js',
        stats: __dirname + '/js/stats.js',
        tags: __dirname + '/js/tags.js',
        simulator_tab: __dirname + '/js/simulator-tab.js',
        simulator_modal: __dirname + '/js/simulator-modal.js',
        example_bp: '../example_bp/static/example_bp.js'
    },
    output: {
        path: __dirname + '/dist',
        publicPath: "./static/dist/",
        filename: '[name]-bundle.js',
    },
    resolve: {
        extensions: ['.js', '.jsx', '.css'],
        modules: [path.resolve(__dirname, 'node_modules'), 'node_modules']
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                use: [
                    'style-loader',
                    'css-loader'
                ]
            },
            {
                test: /\.(scss)$/,
                use: [{
                    loader: 'style-loader', // inject CSS to page
                }, {
                    loader: 'css-loader', // translates CSS into CommonJS modules
                }, {
                    loader: 'postcss-loader', // Run post css actions
                    options: {
                        postcssOptions: { // post css plugins, can be exported to postcss.config.js
                            plugins: [
                                require('precss-v8'),
                                require('autoprefixer')
                            ]
                        }
                    }
                }, {
                    loader: 'sass-loader' // compiles Sass to CSS
                }]
            },
            {
                test: /\.(jpe?g|png|gif)$/i,
                loader: "file-loader"
            },
        ]
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
    ]
};

module.exports = config;
