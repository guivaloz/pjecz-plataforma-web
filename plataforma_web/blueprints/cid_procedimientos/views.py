"""
CID Procedimientos, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento

cid_procedimientos = Blueprint("cid_procedimientos", __name__, template_folder="templates")


@cid_procedimientos.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """ Permiso por defecto """


@cid_procedimientos.route("/cid_procedimientos")
def list_active():
    """ Listado de CID Procedimientos activos """
    cid_procedimientos_activos = CIDProcedimiento.query.filter(CIDProcedimiento.estatus == "A").order_by(CIDProcedimiento.creado.desc()).limit(100).all()
    return render_template("cid_procedimientos/list.jinja2", cid_procedimientos=cid_procedimientos_activos, estatus="A")
