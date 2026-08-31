"""
main.py
CRUD de productos con Flet + MySQL (phpMyAdmin).
Requiere: pip install flet mysql-connector-python
Ejecutar: python main.py
"""

import flet as ft
import os
import database as db


def main(page: ft.Page):
    page.title = "CRUD Productos - Flet + MySQL"
    page.window.width = 900
    page.window.height = 700
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # ----- Estado -----
    id_seleccionado = ft.Ref[ft.Text]()
    id_seleccionado_valor = {"id": None}  # producto en edición

    # ----- Campos del formulario -----
    txt_nombre = ft.TextField(label="Nombre", width=300)
    txt_descripcion = ft.TextField(label="Descripción", width=300)
    txt_precio = ft.TextField(label="Precio", width=140, keyboard_type=ft.KeyboardType.NUMBER)
    txt_cantidad = ft.TextField(label="Cantidad", width=140, keyboard_type=ft.KeyboardType.NUMBER)

    mensaje = ft.Text(value="", color=ft.Colors.RED)

    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Precio")),
            ft.DataColumn(ft.Text("Cantidad")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
    )

    def limpiar_formulario(limpiar_mensaje=True):
        id_seleccionado_valor["id"] = None
        txt_nombre.value = ""
        txt_descripcion.value = ""
        txt_precio.value = ""
        txt_cantidad.value = ""
        if limpiar_mensaje:
            mensaje.value = ""
        page.update()

    def cargar_productos():
        tabla.rows.clear()
        productos = db.obtener_productos()
        for p in productos:
            tabla.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(p["id"]))),
                        ft.DataCell(ft.Text(p["nombre"])),
                        ft.DataCell(ft.Text(p["descripcion"] or "")),
                        ft.DataCell(ft.Text(f'${p["precio"]:.2f}')),
                        ft.DataCell(ft.Text(str(p["cantidad"]))),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        tooltip="Editar",
                                        data=p,
                                        on_click=cargar_para_editar,
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        tooltip="Eliminar",
                                        icon_color=ft.Colors.RED,
                                        data=p["id"],
                                        on_click=confirmar_eliminar,
                                    ),
                                ]
                            )
                        ),
                    ]
                )
            )
        page.update()

    def validar_formulario():
        if not txt_nombre.value:
            mensaje.value = "El nombre es obligatorio."
            page.update()
            return False
        try:
            float(txt_precio.value)
            int(txt_cantidad.value)
        except (ValueError, TypeError):
            mensaje.value = "Precio y cantidad deben ser numéricos."
            page.update()
            return False
        mensaje.value = ""
        return True

    def guardar_producto(e):
        if not validar_formulario():
            return

        nombre = txt_nombre.value
        descripcion = txt_descripcion.value
        precio = float(txt_precio.value)
        cantidad = int(txt_cantidad.value)

        if id_seleccionado_valor["id"] is None:
            # Crear
            exito = db.agregar_producto(nombre, descripcion, precio, cantidad)
            mensaje.value = "Producto agregado." if exito else "Error al agregar."
            mensaje.color = ft.Colors.GREEN if exito else ft.Colors.RED
        else:
            # Actualizar
            exito = db.actualizar_producto(
                id_seleccionado_valor["id"], nombre, descripcion, precio, cantidad
            )
            mensaje.value = "Producto actualizado." if exito else "Error al actualizar."
            mensaje.color = ft.Colors.GREEN if exito else ft.Colors.RED

        limpiar_formulario(limpiar_mensaje=False)
        cargar_productos()

    def cargar_para_editar(e):
        p = e.control.data
        id_seleccionado_valor["id"] = p["id"]
        txt_nombre.value = p["nombre"]
        txt_descripcion.value = p["descripcion"] or ""
        txt_precio.value = str(p["precio"])
        txt_cantidad.value = str(p["cantidad"])
        page.update()

    def confirmar_eliminar(e):
        id_producto = e.control.data

        def eliminar(ev):
            db.eliminar_producto(id_producto)
            page.pop_dialog()
            cargar_productos()

        def cancelar(ev):
            page.pop_dialog()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(
                "Este producto se moverá a la papelera (no se borra permanentemente, "
                "podrás restaurarlo después). ¿Continuar?"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Eliminar", on_click=eliminar),
            ],
        )
        page.show_dialog(dialogo)

    def abrir_papelera(e):
        eliminados = db.obtener_productos_eliminados()

        def restaurar(ev):
            db.restaurar_producto(ev.control.data)
            page.pop_dialog()
            cargar_productos()
            abrir_papelera(None)  # reabre la papelera ya actualizada

        def eliminar_definitivo(ev):
            def confirmar(ev2):
                db.eliminar_producto_definitivo(ev.control.data)
                page.pop_dialog()
                abrir_papelera(None)

            def cancelar_def(ev2):
                page.pop_dialog()

            page.show_dialog(
                ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Eliminar definitivamente"),
                    content=ft.Text(
                        "Esta acción SÍ borra el producto para siempre y no se puede deshacer. "
                        "¿Seguro que quieres continuar?"
                    ),
                    actions=[
                        ft.TextButton("Cancelar", on_click=cancelar_def),
                        ft.TextButton("Sí, borrar para siempre", on_click=confirmar),
                    ],
                )
            )

        if not eliminados:
            filas = [ft.Text("No hay productos en la papelera.")]
        else:
            filas = []
            for p in eliminados:
                filas.append(
                    ft.Row(
                        [
                            ft.Text(f'{p["nombre"]} (${p["precio"]:.2f})', width=250),
                            ft.IconButton(
                                icon=ft.Icons.RESTORE,
                                tooltip="Restaurar",
                                icon_color=ft.Colors.GREEN,
                                data=p["id"],
                                on_click=restaurar,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_FOREVER,
                                tooltip="Eliminar definitivamente",
                                icon_color=ft.Colors.RED,
                                data=p["id"],
                                on_click=eliminar_definitivo,
                            ),
                        ]
                    )
                )

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Papelera de productos"),
                content=ft.Column(filas, tight=True, scroll=ft.ScrollMode.AUTO, height=300),
                actions=[ft.TextButton("Cerrar", on_click=lambda ev: page.pop_dialog())],
            )
        )

    btn_guardar = ft.Button("Guardar", icon=ft.Icons.SAVE, on_click=guardar_producto)
    btn_limpiar = ft.OutlinedButton("Limpiar / Cancelar", on_click=lambda e: limpiar_formulario())
    btn_actualizar = ft.OutlinedButton(
        "Actualizar",
        icon=ft.Icons.REFRESH,
        on_click=lambda e: cargar_productos(),
    )
    btn_papelera = ft.OutlinedButton(
        "Papelera",
        icon=ft.Icons.DELETE_OUTLINE,
        on_click=abrir_papelera,
    )

    page.add(
        ft.Text("Gestión de Productos", size=26, weight=ft.FontWeight.BOLD),
        ft.Row(
            [txt_nombre, txt_descripcion, txt_precio, txt_cantidad],
            wrap=True,
        ),
        ft.Row([btn_guardar, btn_limpiar, btn_actualizar, btn_papelera]),
        mensaje,
        ft.Divider(),
        ft.Row([tabla], scroll=ft.ScrollMode.AUTO),
    )

    cargar_productos()


if __name__ == "__main__":
    ft.run(
        main,
        view=ft.AppView.WEB_BROWSER,
        port=int(os.environ.get("PORT", 8550)),  # el hosting asigna el puerto por variable de entorno
    )
