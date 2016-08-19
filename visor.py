import gear
from flask import Flask, render_template, redirect, url_for, flash, get_flashed_messages, jsonify

import settings

app = Flask(__name__, static_url_path='%s/static' % settings.URL_PREFIX)
app.config.from_object('settings')


def refresh_connections():
    app.gearmans = []
    for server in settings.SERVERS:
        try:
            client = gear.Client()
            client.addServer(host=server['host'], port=server['port'])
            client.waitForServer(settings.CONNECT_TIMEOUT)
            conn = client.getConnection()
        except gear.TimeoutError:
            conn = None

        app.gearmans.append({'alias': server['alias'], 'conn': conn})


def get_server_data(server_alias):
    servers = app.gearmans

    gear_server = None
    for server in servers:
        if server['alias'] == server_alias:
            gear_server = server
            break

    if not gear_server:
        raise Exception('Unknown server alias: %s' % server_alias)

    gear_conn = gear_server['conn']

    try:
        request = gear.VersionAdminRequest()
        gear_conn.sendAdminRequest(request, timeout=settings.REQUEST_TIMEOUT)
        server_version = request.response
    except gear.TimeoutError:
        raise Exception('Timeout. Cannot retrieve version.')

    try:
        request = gear.StatusAdminRequest()
        gear_conn.sendAdminRequest(request, timeout=settings.REQUEST_TIMEOUT)
        server_status = request.response
    except gear.TimeoutError:
        raise Exception('Timeout. Cannot retrieve data.')

    data = server_status.decode()
    server_funcs = data.splitlines()

    monitor_data = []
    for func in server_funcs:
        func_data = func.split('\t')
        if len(func_data) > 1:
            monitor_data.append({
                'function': func_data[0],
                'queue_jobs': func_data[1],
                'running_jobs': func_data[2],
                'workers': func_data[3],
            })

    version = server_version.decode().split()[1]

    data = {
        'monitor_data': monitor_data,
        'alias': server_alias,
        'version': version
    }

    return data


@app.route('%s/' % settings.URL_PREFIX, methods=['GET'])
def index():
    return redirect(url_for('servers'))


@app.route('%s/servers/reload' % settings.URL_PREFIX, methods=['GET'])
def servers_reload():
    refresh_connections()
    return redirect(url_for('servers'))


@app.route('%s/servers' % settings.URL_PREFIX, methods=['GET'])
def servers():
    servers = app.gearmans
    data = {
        'servers': servers,
        'errors': get_flashed_messages(category_filter=['servers.error'])
    }

    return render_template('servers.html', **data)


@app.route('%s/servers/<server_alias>' % settings.URL_PREFIX, methods=['GET'])
def monitor(server_alias):
    try:
        data = get_server_data(server_alias)
    except Exception as e:
        flash(str(e), category='servers.error')
        return redirect(url_for('servers'))

    return render_template('monitor.html', **data)


@app.route('%s/ajax/servers/<server_alias>' % settings.URL_PREFIX, methods=['GET'])
def ajax_monitor(server_alias):
    try:
        data = get_server_data(server_alias)
    except Exception as e:
        data = {
            'error': str(e)
        }

    return jsonify(**data)


if __name__ == "__main__":
    refresh_connections()
    app.run("0.0.0.0", port=settings.RUN_PORT, debug=settings.DEBUG)
