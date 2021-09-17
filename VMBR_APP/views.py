# -*-  coding: utf-8 -*-

from flask import jsonify
from flask import render_template, flash, redirect, session, url_for, request, g
from VMBR_APP import app, db
#from forms import loginForm, serviceForm
#from flask_login import login_user, logout_user, current_user, login_required
from VMBR_APP.models import VMInf
from sqlalchemy import desc
from VMBR_APP.vm_app import get_all_vms, operation_snapshots

@app.route('/get_all_vms/<int:page>')
def get_all_vms_info():
    ret = get_all_vms()
    if ret:
        return jsonify({'ret': ret})

@app.route('/list_cur_snapshot')
def list_cur_snapshot():
    ret = operation_snapshots(vm_name, snapshot_name, operation='list_current')
    if ret:
        return jsonify({'ret': ret})

@app.route('/list_all_snapshot/<int:page>')
def list_all_snapshot():
    ret = operation_snapshots(vm_name, snapshot_name=None, operation='list_all')
    if ret:
        return jsonify({'ret': ret})

@app.route('/create_snapshot', methods=['GET','POST'])
def create_snapshot():
    ret = operation_snapshots(vm_name, snapshot_name, operation='create')
    if ret:
        return jsonify({'ret': ret})
@app.route('/remove_snapshot', methods=['GET','POST'])
def remove_snapshot():
    ret = operation_snapshots(vm_name, snapshot_name, operation='remove')
    if ret:
        return jsonify({'ret': ret})

@app.route('/remove_all_snapshots', methods=['GET','POST'])
def remove_all_snapshots():
    ret = operation_snapshots(vm_name, snapshot_name, operation='remove_all')
    if ret:
        return jsonify({'ret': ret})

@app.route('/revert_snapshot', methods=['GET','POST'])
def revert_snapshot():
    ret = operation_snapshots(vm_name, snapshot_name, operation='revert')
    if ret:
        return jsonify({'ret': ret})