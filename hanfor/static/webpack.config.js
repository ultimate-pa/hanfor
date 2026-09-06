const webpack = require('webpack');
const path = require("path");
const fs = require('fs');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

// Determine mode from the --mode flag passed by webpack-cli
const modeArg = process.argv.find((a, i) => process.argv[i - 1] === '--mode' && (a === 'production' || a === 'development'));
const NODE_ENV = modeArg || 'development';

// auto-discovery of ai-addons
const aiAddonEntries = fs.readdirSync(__dirname + '/../ai_addons')
    .filter(dir => !['__pycache__'].includes(dir))
    .filter(dir => fs.statSync(__dirname + '/../ai_addons/' + dir).isDirectory())
    .reduce((entries, dir) => {
        const staticPath = __dirname + '/../ai_addons/' + dir + '/static/';
        if (fs.existsSync(staticPath)) {
            fs.readdirSync(staticPath)
                .filter(file => file.endsWith('.js'))
                .forEach(file => {
                    const name = path.basename(file, '.js');
                    entries[name] = staticPath + file;
                });
        }
        return entries;
    }, {});

const config = {
    mode: NODE_ENV,
    entry: {
        layout_globals: __dirname + '/js/layout-globals.js',
        requirements: __dirname + '/js/requirements.js',
        variables: __dirname + '/js/variables.js',
        variable_import: __dirname + '/js/variable-import.js',
        //stats: __dirname + '/js/stats.js',
        //tags: __dirname + '/js/tags.js',
        simulator_tab: __dirname + '/js/simulator-tab.js',
        simulator_modal: __dirname + '/js/simulator-modal.js',
        example_blueprint: __dirname + '/../example_blueprint/static/example_blueprint.js',
        quickchecks: __dirname + '/../quickchecks/static/quickchecks.js',
        tags: __dirname + '/../tags/static/tags.js',
        statistics: __dirname + '/../statistics/static/statistics.js',
        ultimate: __dirname + '/../ultimate/static/ultimate.js',
        ultimate_tab: __dirname + '/../ultimate/static/ultimate-tab.js',
        telemetry: __dirname + '/../telemetry/static/telemetry.js',
        telemetry_frontend: __dirname + '/../telemetry/static/telemetry_frontend.js',
        ...aiAddonEntries,
    },
    output: {
        filename: '[name]-bundle.js',
        path: __dirname + '/dist',
        publicPath: "./static/dist/"
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
                    NODE_ENV === 'production' ? MiniCssExtractPlugin.loader : 'style-loader',
                    'css-loader'
                ]
            },
            {
                test: /\.(scss)$/,
                use: [
                    NODE_ENV === 'production' ? MiniCssExtractPlugin.loader : { loader: 'style-loader' },
                    { loader: 'css-loader' },
                    {
                        loader: 'postcss-loader',
                        options: {
                            postcssOptions: {
                                plugins: [
                                    //require('precss-v8'),
                                    require('autoprefixer')
                                ]
                            }
                        }
                    },
                    {
                        loader: 'sass-loader',
                        options: {
                            implementation: require("sass")
                        }
                    }
                ]
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
        }),
        ...(NODE_ENV === 'production'
            ? [new MiniCssExtractPlugin({ filename: '[name].css' })]
            : [])
    ]
};

module.exports = config;