// Función para formatear fechas
function formatearFecha(fechaISO) {
    if (!fechaISO) return '<span class="text-muted">Sin fecha</span>';
    const meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const partes = fechaISO.split("-");
    if (partes.length !== 3) return fechaISO;
    const anio = partes[0];
    const mes = meses[parseInt(partes[1], 10) - 1];
    const dia = partes[2];
    return `${mes} ${dia}, ${anio}`;
}

// Función para mostrar Toast
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'text-bg-success' : 'text-bg-danger';
    const iconClass = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="3500">
            <div class="d-flex">
                <div class="toast-body"><i class="fa ${iconClass} me-2"></i>${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
            </div>
        </div>`;
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    const toastEl = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

$(document).ready(function() {
    var tabla = $('#tabla-encuestas').DataTable({
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
    
    var encuestaIdAEliminar = null;

    // Ocultar el mensaje si hay filas
    if($('#tabla-encuestas tbody tr').length > 0) {
        $('.alert-info').hide();
    }

    // Modal de enviar a papelera
    document.getElementById('borrarEncuestaModal').addEventListener('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        var id = button.getAttribute('data-id');
        var titulo = button.getAttribute('data-titulo');
        document.getElementById('modal-borrar-titulo').textContent = titulo;
        var form = document.getElementById('formPapeleraEncuesta');
        form.action = window.urlEnviarPapelera.replace('0', id);
        encuestaIdAEliminar = id;
    });

    // Enviar a papelera por AJAX y eliminar la fila de la tabla
    $('#formPapeleraEncuesta').on('submit', function(e) {
        e.preventDefault();
        var form = this;
        $.ajax({
            url: form.action,
            type: 'POST',
            data: $(form).serialize(),
            success: function() {
                $('#borrarEncuestaModal').modal('hide');
                if(encuestaIdAEliminar) {
                    var fila = $('#tabla-encuestas').find('a[data-id="' + encuestaIdAEliminar + '"]').closest('tr');
                    tabla.row(fila).remove().draw();

                    // Renumerar la columna #
                    tabla.rows({search:'applied'}).every(function(rowIdx, tableLoop, rowLoop) {
                        var node = this.node();
                        $(node).find('td').eq(0).text(rowIdx + 1);
                    });

                    // Si ya no quedan filas, ocultar la tabla y mostrar el mensaje
                    if(tabla.rows().count() === 0) {
                        $('#tabla-encuestas').parents('div.dataTables_wrapper').first().hide();
                        $('.alert-info').show();
                    }
                }
                showToast('Encuesta eliminada exitosamente.', 'success');
            },
            error: function() {
                showToast('Error al eliminar la encuesta.', 'danger');
            }
        });
    });

    // Modal En Curso/Finalizada encuesta
    $('#modalEstadoEncuesta').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var encuestaId = button.data('id');
        var action = button.data('action');
        var titulo = button.data('titulo');
        var form = $('#formEstadoEncuesta');
        var modalTitle = $('#modalEstadoEncuestaLabel');
        var modalBody = $('#modalEstadoEncuestaBody');
        var modalBtn = $('#modalEstadoEncuestaBtn');

        if (action === 'desactivar') {
            modalTitle.text('Finalizar encuesta');
            modalBody.html('¿Seguro que deseas marcar la encuesta <strong>' + titulo + '</strong> como <span class="text-danger">Finalizada</span>?');
            modalBtn.text('Finalizar');
            modalBtn.removeClass('btn-success btn-primary btn-secondary btn-danger').addClass('btn-danger');
            form.attr('action', window.urlDesactivarEncuesta.replace('0', encuestaId));
        }
    });

    // Modal Reabrir encuesta con autenticación
    $('#modalReabrirEncuesta').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var encuestaId = button.data('id');
        var form = $('#formReabrirEncuesta');
        var actionUrl = window.urlReabrirEncuesta.replace('0', encuestaId);
        form.attr('action', actionUrl);
    });

    // Modal crear encuesta AJAX
    $('#formCrearEncuesta').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var formDataArray = form.serializeArray();
    
        // Normaliza la fecha si viene en formato dd/mm/yyyy
        formDataArray.forEach(function(item) {
            if(item.name === 'fecha_finalizacion' && item.value) {
                if(item.value.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
                    var parts = item.value.split('/');
                    item.value = parts[2] + '-' + parts[1] + '-' + parts[0];
                }
            }
        });
        var data = $.param(formDataArray);
    
        $('#ajax-error-msg').addClass('d-none').text('');
        $.ajax({
            url: window.urlCrearEncuesta,
            type: 'POST',
            data: data,
            success: function(response) {
                $('#modalCrearEncuesta').modal('hide');
                form.trigger('reset');
                
                // Agrega la nueva encuesta a la tabla usando DataTables
                let encuesta = response.encuesta;
                let desc = encuesta.descripcion ? encuesta.descripcion : '<span class="text-muted">Sin descripción</span>';
                if(desc.length > 30) desc = desc.substring(0, 30) + '...';
                let fecha = formatearFecha(encuesta.fecha_finalizacion);
                
                // Construir botones de acción
                let botonesAccion = '<div class="d-flex justify-content-center flex-wrap gap-1">';
                
                // Botón Editar
                botonesAccion += '<button type="button" class="btn btn-primary btn-sm btn-editar-encuesta" ' +
                    'data-bs-toggle="modal" data-bs-target="#modalEditarEncuesta" ' +
                    'data-id="' + encuesta.id + '" ' +
                    'data-titulo="' + encuesta.titulo + '" ' +
                    'data-descripcion="' + (encuesta.descripcion || '') + '" ' +
                    'data-fecha_finalizacion="' + (encuesta.fecha_finalizacion || '') + '" ' +
                    'title="Editar">' +
                    '<i class="fa fa-edit"></i>' +
                    '</button>';
                
                // Botón Eliminar (solo para superusuarios)
                if (window.isSuperuser) {
                    botonesAccion += '<a href="#" class="btn btn-danger btn-sm" title="Borrar" ' +
                        'data-bs-toggle="modal" data-bs-target="#borrarEncuestaModal" ' +
                        'data-id="' + encuesta.id + '" ' +
                        'data-titulo="' + encuesta.titulo + '">' +
                        '<i class="fa fa-trash"></i>' +
                        '</a>';
                }
                
                // Botón Ver Detalles
                botonesAccion += '<a href="/encuestas/' + encuesta.id + '/" ' +
                    'class="btn btn-info btn-sm" title="Ver">' +
                    '<i class="fa fa-ellipsis"></i>' +
                    '</a>';
                
                botonesAccion += '</div>';
                
                // Badge de estado
                let badgeEstado = '<button type="button" class="badge bg-success border-0" style="cursor:pointer;" ' +
                    'data-bs-toggle="modal" data-bs-target="#modalEstadoEncuesta" ' +
                    'data-id="' + encuesta.id + '" ' +
                    'data-action="desactivar" ' +
                    'data-titulo="' + encuesta.titulo + '">' +
                    'En Curso' +
                    '</button>';
                
                // Crear la fila con DataTables
                let newRowData = [
                    '', // El número se actualizará automáticamente
                    '<strong>' + encuesta.titulo + '</strong>',
                    '<div style="max-width:180px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;">' + desc + '</div>',
                    fecha,
                    badgeEstado,
                    botonesAccion
                ];
                
                // Agregar la fila usando DataTables API
                tabla.row.add(newRowData).draw(false);
                
                // Renumerar todas las filas
                tabla.rows().every(function(rowIdx) {
                    this.data()[0] = rowIdx + 1;
                });
                tabla.draw(false);
                
                // Ocultar mensaje de "no hay encuestas" si estaba visible
                $('.alert-info').hide();
                $('#tabla-encuestas').parents('div.dataTables_wrapper').first().show();
                
                showToast('Encuesta creada exitosamente.', 'success');
            },
            error: function(xhr) {
                let msg = 'Error al crear la encuesta.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    msg = xhr.responseJSON.error;
                }
                $('#ajax-error-msg').removeClass('d-none').text(msg);
                showToast(msg, 'danger');
            }
        });
    });

    // Editar Encuesta: abrir modal y rellenar datos
    $(document).on('click', '.btn-editar-encuesta', function() {
        var btn = $(this);
        $('#edit_id').val(btn.data('id'));
        $('#edit_titulo').val(btn.data('titulo'));
        $('#edit_descripcion').val(btn.data('descripcion'));
        $('#edit_fecha_finalizacion').val(btn.data('fecha_finalizacion'));
        $('#ajax-edit-error-msg').addClass('d-none').text('');
    });

    // Enviar edición por AJAX
    $('#formEditarEncuesta').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var data = form.serialize();
        var id = $('#edit_id').val();
        $('#ajax-edit-error-msg').addClass('d-none').text('');
        
        $.ajax({
            url: window.urlEditarEncuesta.replace('0', id),
            type: 'POST',
            data: data,
            success: function(response) {
                $('#modalEditarEncuesta').modal('hide');
                
                // Obtener los nuevos valores del response del servidor
                var encuesta = response.encuesta;
                var nuevoTitulo = encuesta.titulo;
                var nuevaDesc = encuesta.descripcion || '';
                var nuevaFecha = encuesta.fecha_finalizacion;
                
                // Buscar la fila específica usando el botón de editar
                var fila = $('#tabla-encuestas').find('.btn-editar-encuesta[data-id="' + id + '"]').closest('tr');
                
                // Actualizar el contenido visible de la tabla
                fila.find('td:eq(1)').html('<strong>' + nuevoTitulo + '</strong>');
                
                var descCorta = nuevaDesc;
                if(descCorta && descCorta.length > 30) descCorta = descCorta.substring(0, 30) + '...';
                fila.find('td:eq(2)').html(descCorta ? descCorta : '<span class="text-muted">Sin descripción</span>');
                fila.find('td:eq(3)').html(nuevaFecha ? formatearFecha(nuevaFecha) : '<span class="text-muted">Sin fecha</span>');
                
                // Actualizar TODOS los atributos data-* del botón de editar
                var btnEditar = fila.find('.btn-editar-encuesta');
                btnEditar.attr('data-titulo', nuevoTitulo);
                btnEditar.attr('data-descripcion', nuevaDesc);
                btnEditar.attr('data-fecha_finalizacion', nuevaFecha);
                
                // Actualizar el badge de estado (botón "En Curso")
                var badgeEstado = fila.find('button[data-bs-target="#modalEstadoEncuesta"]');
                if (badgeEstado.length > 0) {
                    badgeEstado.attr('data-titulo', nuevoTitulo);
                    badgeEstado.attr('data-id', id);
                }
                
                // Actualizar el botón de borrar
                var btnBorrar = fila.find('a[data-bs-target="#borrarEncuestaModal"]');
                if (btnBorrar.length > 0) {
                    btnBorrar.attr('data-titulo', nuevoTitulo);
                    btnBorrar.attr('data-id', id);
                }
                
                // Actualizar el enlace de ver detalles
                var btnDetalle = fila.find('a[href*="/encuestas/"]');
                if (btnDetalle.length > 0) {
                    btnDetalle.attr('href', '/encuestas/' + id + '/');
                }
                
                // Forzar redibujado de DataTables para asegurar que los cambios se reflejen
                tabla.row(fila).invalidate().draw(false);
                
                showToast('Encuesta actualizada exitosamente.', 'success');
            },
            error: function(xhr) {
                let msg = 'Error al editar la encuesta.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    msg = xhr.responseJSON.error;
                }
                $('#ajax-edit-error-msg').removeClass('d-none').text(msg);
                showToast(msg, 'danger');
            }
        });
    });

    // Toast Bootstrap: activar automáticamente los mensajes de Django
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.forEach(function(toastEl) {
        var toast = new bootstrap.Toast(toastEl);
        toast.show();
    });
});

// Configuración de fechas para los campos de fecha
document.addEventListener('DOMContentLoaded', function() {
    var camposFecha = [
        document.getElementById('fecha_finalizacion'),
        document.getElementById('edit_fecha_finalizacion')
    ];
    var today = new Date();
    var currentYear = today.getFullYear();
    var tomorrow = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1);
    var minDate = tomorrow.toISOString().split('T')[0];
    var maxDate = (currentYear + 4) + '-12-31';

    camposFecha.forEach(function(fechaCampo) {
        if (fechaCampo) {
            fechaCampo.setAttribute('min', minDate);
            fechaCampo.setAttribute('max', maxDate);
            if (!fechaCampo.value) {
                fechaCampo.value = minDate;
            }
        }
    });

    var campoReabrir = document.getElementById('nueva_fecha_finalizacion');
    if (campoReabrir) {
        campoReabrir.setAttribute('min', minDate);
        campoReabrir.setAttribute('max', maxDate);
        if (!campoReabrir.value) {
            campoReabrir.value = minDate;
        }
    }
});