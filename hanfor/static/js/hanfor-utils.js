class APITask {
    constructor() {
        this.url = "";
        this.data_json = null;
        this.method = 'GET';
    }

    run() {
        return $.ajax({
            url: this.url,
            type: this.method,
            data: JSON.stringify(this.data_json),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json'
        });
    }
}

class UltimateAPITaskGetVersion extends APITask {
    constructor() {
        super();
        this.method = "GET";
        this.url = "api/ultimate/version";
        this.data_json = {task: 'get_version'}
    }
}

class UltimateAPITaskPingUltimate extends APITask {
    constructor() {
        super();
        this.method = "GET";
        this.url = "api/ultimate/ping";
        this.data_json = {task: 'ping_ultimate'}
    }
}

class UltimateAPITaskAddRun extends APITask {
    constructor(req_ids) {
        super();
        this.method = "POST";
        this.url = "api/ultimate/run";
        this.data_json = {
            task: 'add_new_run',
            req_ids: req_ids
        }
    }
}

class UltimateAPITaskReloadRun extends APITask {
    constructor(id) {
        super();
        this.method = "POST";
        this.url = "api/ultimate/run";
        this.data_json = {
            task: 'reload_run',
            run_id: id // Hanfor internal ID
        }
    }
}

class UltimateAPITaskStartRun extends APITask {
    constructor(id, user_settings, toolchain_xml) {
        super();
        this.method = "POST";
        this.url = "api/ultimate/run";
        this.data_json = {
            task: 'start_run',
            user_settings: user_settings,
            toolchain_xml: toolchain_xml,
            run_id: id // Hanfor internal ID
        }

    }
}

class UltimateAPITaskDeleteRun extends APITask {
    constructor(id) {
        super();
        this.method = "POST";
        this.url = "api/ultimate/run";
        this.data_json = {
            task: 'delete_run',
            run_id: id // Hanfor internal ID
        }

    }
}

class UltimateAPITaskStopRun extends APITask {
    constructor(id) {
        super();
        this.method = "POST";
        this.url = "api/ultimate/run";
        this.data_json = {
            task: 'stop_run',
            run_id: id // Hanfor internal ID
        }

    }
}

class UltimateAPITaskUpdateRun extends APITask {
    constructor(id, meta_data) {
        super();
        this.method = 'POST';
        this.url = "api/ultimate/run";
        this.data_json = {
            task: 'update_run',
            run_id: id, // Hanfor internal ID
            meta_infos: meta_data
        }
    }
}

const api = {
    ultimate: {
        run: {
            url: 'api/ultimate/run',
            task_payload: {
                new_run: {
                    task: 'add_new_run',
                    req_ids: []
                },
                get_run: {
                    task: 'get_run',
                    run_id: ''  // Hanfor internal ID
                },
                set_ultimate_job_id: {
                    task: 'set_ultimate_job_id',
                    run_id: '', // Hanfor internal ID
                    ultimate_job_id: ''  // Ultimate internal ID
                },
                start_run: {
                    task: 'start_run',
                    run_id: ''
                }
            }
        },
        runs: {
            url: 'api/ultimate/runs',
            task_payload: {
                get_all: {
                    task: 'get_runs'
                }
            }
        }
    }
};

/**
 * Escape a HTML string for display as a raw string.
 * @param unsafe
 * @returns {string}
 */
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/**
 * Apply a URL search query to the requirements table.
 * @param get_query
 */
function process_url_query(get_query) {
    // Apply search if we have one.
    if (typeof (get_query.q) !== "undefined") {
        /**
         * Pad a Number string with 0 prefix (max length is 2).
         * Examples: 2 -> 02, '' -> 00, 12 -> 12, 123 -> 23
         * @param num
         * @returns {string}
         */
        function pad(num) {
            let s = "00" + num;
            return s.substr(s.length - 2);
        }

        // Clear filters.
        $('#status-filter-input').val('');
        $('#tag-filter-input').val('');
        $('#type-filter-input').val('');

        // Create the search string.
        let s = get_query.q;
        if (typeof (get_query.col) !== "undefined") {
            s = ':COL_INDEX_' + pad(get_query.col).toString() + ':' + s;
        }
        // Apply the search string
        $('#search_bar').val(s);
    }
}

module.exports.escapeHtml = escapeHtml;
module.exports.process_url_query = process_url_query;
module.exports.api = api;
module.exports.UltimateAPITaskGetVersion = UltimateAPITaskGetVersion;
module.exports.UltimateAPITaskPingUltimate = UltimateAPITaskPingUltimate;
module.exports.UltimateAPITaskReloadRun = UltimateAPITaskReloadRun;
module.exports.UltimateAPITaskStartRun = UltimateAPITaskStartRun;
module.exports.UltimateAPITaskDeleteRun = UltimateAPITaskDeleteRun;
module.exports.UltimateAPITaskStopRun = UltimateAPITaskStopRun;
module.exports.UltimateAPITaskUpdateRun = UltimateAPITaskUpdateRun;
module.exports.UltimateAPITaskAddRun = UltimateAPITaskAddRun;
