
$(document).ready(function() {
    // Toast Bootstrap: activar automáticamente los mensajes de Django
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.forEach(function(toastEl) {
        var toast = new bootstrap.Toast(toastEl);
        toast.show();
    });
});

// Función para mostrar toast
function mostrarToast(mensaje, tipo = "success") {
    const toastId = "toast-" + Date.now();
    const color = {
        success: "bg-success text-white",
        danger: "bg-danger text-white",
        info: "bg-info text-white",
        warning: "bg-warning text-dark"
    }[tipo] || "bg-primary text-white";
    const toastHtml = `
      <div id="${toastId}" class="toast align-items-center ${color} border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="3500">
        <div class="d-flex">
          <div class="toast-body">${mensaje}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
        </div>
      </div>
    `;
    if ($("#toast-container").length) {
        $("#toast-container").append(toastHtml);
        const toastEl = document.getElementById(toastId);
        if (toastEl) {
            const toast = new bootstrap.Toast(toastEl);
            toast.show();
            toastEl.addEventListener('hidden.bs.toast', function () {
                toastEl.remove();
            });
        }
    } else {
        alert(mensaje); // Fallback si no existe el contenedor
    }
}

$(document).ready(function() {

    // 1. Inicializamos la tabla UNA SOLA VEZ y guardamos la instancia en la variable 'table'.
    // Usamos tu código de inicialización original.
    var table = $('#tabla-casas').DataTable({
        "responsive": true,
        "language": {
            "processing": "Procesando...",
            "lengthMenu": "Mostrar _MENU_ registros",
            "zeroRecords": "No se encontraron resultados",
            "emptyTable": "Ningún dato disponible en esta tabla",
            "info": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_",
            "infoEmpty": "Mostrando registros del 0 al 0 de un total de 0",
            "infoFiltered": "(filtrado de un total de _MAX_ registros)",
            "search": "Buscar:",
            "paginate": {
                "first": "Primero",
                "last": "Último",
                "next": "Siguiente",
                "previous": "Anterior"
            }
        },
        "info": false
    });

    // Código para ocultar alertas si la tabla ya tiene datos.
    if ($('#tabla-casas tbody tr').length > 0) {
        $('.alert-info').hide();
    }

    // 2. Manejo del envío del formulario para AGREGAR casa.
    // Este evento ahora usa la misma variable 'table' que definimos arriba.
    $('#formAgregarCasa').on('submit', function(e) {
        e.preventDefault(); // Evitar que la página se recargue

        var form = $(this);
        var url = form.attr('action');
        var data = form.serialize();

        $.post(url, data)
            .done(function(response) {
                // Si la respuesta de la vista es exitosa
                if (response.status === 'success') {
                    
                    // Mostrar notificación de éxito
                    mostrarToast(response.message, 'success');
                    
                    // Cerrar el modal
                    $('#modalAgregarCasa').modal('hide');
                    
                    // Limpiar el formulario
                    form[0].reset();
                    
                    // Agregar la nueva fila a DataTables
                    var nuevaFila = table.row.add([
                        table.rows().count() + 1,
                        '<strong>' + response.casa.numero_casa + '</strong>',
                        response.casa.cantidad_familia,
                        response.casa.consejo_comunal,
                        `<div class="d-flex justify-content-center flex-wrap gap-1">
                            <a href="#" class="btn btn-danger btn-sm" title="Borrar" data-bs-toggle="modal" data-bs-target="#modalBorrarCasa${response.casa.id}">
                                <i class="fa fa-trash"></i>
                            </a>
                            <a href="#" class="btn btn-primary btn-sm" title="Editar" data-bs-toggle="modal" data-bs-target="#modalEditarCasa${response.casa.id}">
                                <i class="fa fa-edit"></i>
                            </a>
                            <a href="/familias/casa/${response.casa.id}/" class="btn btn-info btn-sm" title="Familias de esta casa">
                                <i class="fa fa-ellipsis"></i>
                            </a>
                        </div>`
                    ]).draw(false).node();

                    // Añadir el atributo data-casa-id a la nueva fila <tr>
                    $(nuevaFila).attr('data-casa-id', response.casa.id);
                }
            })
            .fail(function(xhr) {
                // Manejar errores de validación o del servidor
                mostrarToast('Error al agregar la casa. Revise los datos.', 'danger');
            });
    });

   // Evento para el envío del formulario de edición (tu código, pero modificado)
$(document).on('submit', '[id^="formEditarCasa"]', function(e) {
    e.preventDefault(); // Previene el envío normal del formulario

    var form = $(this);
    var url = form.attr('action');
    var data = form.serialize(); // Contiene todos los datos del form, incluido el csrf token
    var casaId = form.attr('id').replace('formEditarCasa', '');
    var modal = $('#modalEditarCasa' + casaId);

    // Se mantiene igual el envío por POST
    $.post(url, data)
        .done(function(response) { // 'response' es el JSON que envía tu vista de Django
            
            // Verificamos que la respuesta del servidor fue exitosa
            if (response.status === 'success') {
                mostrarToast(response.message, "success");
                modal.modal('hide');

                // --- ¡AQUÍ ESTÁ EL CAMBIO IMPORTANTE! ---
                // En lugar de actualizar los <td> a mano, usamos la API de DataTables
                
                // 1. Seleccionamos la fila que vamos a editar usando la API
                var fila = table.row('tr[data-casa-id="' + casaId + '"]');
                
                if (fila.length) {
                    // 2. Actualizamos cada celda usando la data de la respuesta JSON
                    // La sintaxis es: table.cell(fila, indiceDeColumna).data(nuevoValor)
                    table.cell(fila, 1).data('<strong>' + response.casa.numero_casa + '</strong>');
                    table.cell(fila, 2).data(response.casa.cantidad_familia);
                    table.cell(fila, 3).data(response.casa.consejo_comunal);

                    // 3. Redibujamos la tabla para que los cambios se apliquen visualmente
                    // El 'false' es para que no se reinicie la paginación
                    table.draw(false);
                }

            } else {
                // Si la vista devuelve un error de validación, por ejemplo
                mostrarToast(response.message || "Ocurrió un error.", "danger");
            }
        })
        .fail(function(xhr) {
            mostrarToast("Error de conexión al intentar editar la casa.", "danger");
        });
});

    // Eliminar casa por AJAX y eliminar la fila
$(document).on('submit', '[id^="formEliminarCasa"]', function(e) {
    e.preventDefault();
    var form = this;
    var casaId = form.id.replace('formEliminarCasa', '');
    $.post(form.action, $(form).serialize())
        .done(function() {
            mostrarToast("Casa eliminada correctamente.", "success");
            var fila = $('#tabla-casas tbody tr[data-casa-id="' + casaId + '"]');
            var tablaCasas = $('#tabla-casas').DataTable();
            tablaCasas.row(fila).remove().draw(false);
            $('#modalBorrarCasa' + casaId).modal('hide');
        })
        .fail(function() {
            mostrarToast("Error al eliminar la casa.", "danger");
        });
});

});