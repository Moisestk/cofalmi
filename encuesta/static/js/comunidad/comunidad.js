$(document).ready(function() {

    // --- 1. Configuración de DataTable ---
    var tabla = $('#tabla-comunidades').DataTable({
        "language": {
            "processing": "Procesando...",
            "lengthMenu": "Mostrar _MENU_ registros",
            "zeroRecords": "No se encontraron resultados",
            "emptyTable": "Ningún dato disponible en esta tabla",
            "info": "Mostrando del _START_ al _END_ de _TOTAL_ registros",
            "infoEmpty": "Mostrando 0 de 0 registros",
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

// Mostrar el nombre de la comunidad en el modal de papelera y guardar el id
$(document).on('click', '.btn-borrar-comunidad', function() {
    var id = $(this).data('id');
    var nombre = $(this).data('titulo');
    $('#modal-borrar-titulo').text(nombre);
    $('#formPapeleraComunidad').data('id', id);
});

// Enviar a papelera por AJAX
$('#formPapeleraComunidad').on('submit', function(e) {
    e.preventDefault();
    var id = $(this).data('id');
    var csrf = $(this).find('[name=csrfmiddlewaretoken]').val();
    $.ajax({
        url: '/comunidad/' + id + '/enviar_a_papelera/',
        type: 'POST',
        data: {csrfmiddlewaretoken: csrf},
        success: function(response) {
            // 1. Oculta el modal
            $('#borrarComunidadModal').modal('hide'); 
            // 2. Muestra el mensaje de éxito (con aviso de recarga)
            mostrarToast('Comunidad enviada a la papelera.', false); 
            // 3. Espera 10 segundos (10000ms)
            setTimeout(function() {
                // Primero elimina la fila visualmente
                $('a.btn-borrar-comunidad[data-id="' + id + '"]').closest('tr').remove();
                // Y luego recarga la página
                location.reload(); 
            }, 1000); 
            
        },
        error: function(xhr) {
            mostrarToast('Error al enviar a papelera.', true);
        }
    });
});

// Configuración de campos de fecha al cargar el documento
document.addEventListener('DOMContentLoaded', function() {
    // --------- Lógica para campos de fecha en crear y editar comunidad ---------
    // IDs de los campos de fecha en crear y editar comunidad
    var camposFecha = [
        document.getElementById('fecha_finalizacion'),
        document.getElementById('edit_fecha_finalizacion')
    ];
    var today = new Date();
    var currentYear = today.getFullYear();
    // Calcular mañana
    var tomorrow = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1);
    var minDate = tomorrow.toISOString().split('T')[0];
    var maxDate = (currentYear + 4) + '-12-31';

    // Para crear y editar: solo permitir fechas a partir de mañana
    camposFecha.forEach(function(fechaCampo) {
        if (fechaCampo) {
            fechaCampo.setAttribute('min', minDate);
            fechaCampo.setAttribute('max', maxDate);
            // Si el campo está vacío, ponerle mañana como valor inicial
            if (!fechaCampo.value) {
                fechaCampo.value = minDate;
            }
        }
    });
    // --------------------------------------------------------------------------
});

    // --- 2. Lógica para Crear Comunidad (Modal y AJAX) ---
    $('#formCrearComunidad').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var data = form.serialize();
        var errorContainer = $('#ajax-error-msg');
        errorContainer.addClass('d-none').html('');

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            dataType: 'json',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.success) {
                    var comunidad = response.comunidad;

                    // Crear el HTML para los botones de acción
                    var botonesAccion = `
                        <div class='d-flex justify-content-center flex-wrap gap-1'>
                            <button type="button"
                                class="btn btn-primary btn-sm btn-editar-comunidad"
                                title="Editar"
                                data-bs-toggle="modal"
                                data-bs-target="#modalEditarComunidad"
                                data-id="${comunidad.id}"
                                data-nombre="${comunidad.nombre}"
                                data-estado="${comunidad.estado}"
                                data-municipio="${comunidad.municipio}"
                                data-parroquia="${comunidad.parroquia}"
                                data-comuna="${comunidad.comuna}"
                                data-cantidad_habitantes="${comunidad.cantidad_habitantes}">
                                <i class="fa fa-edit"></i>
                            </button>
                            <a href='#' class='btn btn-danger btn-sm' title='Enviar a papelera'
                               data-bs-toggle='modal' data-bs-target='#borrarComunidadModal'
                               data-id='${comunidad.id}' data-titulo='${comunidad.nombre}'>
                               <i class='fa fa-trash'></i>
                            </a>
                            <a href="/comunidad/${comunidad.id}/detalle/" class="btn btn-info btn-sm" title="Ver">
                                <i class="fa fa-ellipsis"></i>
                            </a>
                        </div>`;
                    
                    // Añadir la nueva fila a la tabla DataTable
                    var nuevaFila = tabla.row.add([
                        tabla.rows().count() + 1,
                        comunidad.nombre,
                        comunidad.estado,
                        comunidad.municipio,
                        comunidad.parroquia,
                        comunidad.comuna,
                        comunidad.cantidad_habitantes,
                        botonesAccion
                    ]).draw(false).node();
                    
                    $(nuevaFila).attr('id', `comunidad-row-${comunidad.id}`);
                    $(nuevaFila).find('td:eq(1)').addClass('nombre');
                    $(nuevaFila).find('td:eq(2)').addClass('estado');
                    $(nuevaFila).find('td:eq(3)').addClass('municipio');

                    $('#modalCrearComunidad').modal('hide');
                    showToast('Comunidad añadida exitosamente.', 'success');
                }
            },
            error: function(xhr) {
                let errorMessage = '<strong>Revise los siguientes errores:</strong><ul>';
                if (xhr.responseJSON && xhr.responseJSON.errors) {
                    for (let field in xhr.responseJSON.errors) {
                        let errorText = xhr.responseJSON.errors[field][0].message || xhr.responseJSON.errors[field][0];
                        errorMessage += `<li>${errorText}</li>`;
                    }
                } else {
                    errorMessage += `<li>Error de servidor (${xhr.status}). Intente de nuevo.</li>`;
                }
                errorMessage += '</ul>';
                errorContainer.html(errorMessage).removeClass('d-none');
                showToast('Error al añadir comunidad. Revise el formulario.', 'danger');
            }
        });
    });

// Función para mostrar el toast
function mostrarToast(mensaje, error=false) {
    var toastHtml = `
    <div class="toast align-items-center text-bg-${error ? 'danger' : 'success'} border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="3500">
      <div class="d-flex">
        <div class="toast-body">${mensaje}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
      </div>
    </div>`;
    var $toastContainer = $('.position-fixed.top-0.end-0.p-3');
    if ($toastContainer.length === 0) {
        $toastContainer = $('<div aria-live="polite" aria-atomic="true" class="position-fixed top-0 end-0 p-3" style="z-index: 1080; right: 0; top: 0;"></div>');
        $('body').append($toastContainer);
    }
    var $toast = $(toastHtml);
    $toastContainer.append($toast);
    var toast = new bootstrap.Toast($toast[0]);
    toast.show();
    $toast.on('hidden.bs.toast', function() { $(this).remove(); });
}

// Al hacer click en editar, rellena el modal
$(document).on('click', '.btn-editar-comunidad', function() {
    const button = this;
    
    $('#editar-id').val(button.getAttribute('data-id'));
    $('#editar-nombre').val(button.getAttribute('data-nombre'));
    $('#editar-estado').val(button.getAttribute('data-estado'));
    $('#editar-municipio').val(button.getAttribute('data-municipio'));
    $('#editar-parroquia').val(button.getAttribute('data-parroquia'));
    $('#editar-comuna').val(button.getAttribute('data-comuna'));
    $('#editar-cantidad_habitantes').val(button.getAttribute('data-cantidad_habitantes'));
});

// Enviar el formulario de edición por AJAX
    $('#formEditarComunidad').on('submit', function(e) {
        e.preventDefault();
        var id = $('#editar-id').val();
        var form = $(this);
        var data = form.serialize();
        
        $.ajax({
            url: '/comunidad/editar/' + id + '/',
            type: 'POST',
            data: data,
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var comunidad = response.comunidad;
                    
                    // Actualizar la fila en la tabla sin recargar
                    var $btn = $('.btn-editar-comunidad[data-id="' + comunidad.id + '"]');
                    var $row = $btn.closest('tr');
                    
                    if ($row.length) {
                        $row.find('td:eq(1)').html('<strong>' + comunidad.nombre + '</strong>');
                        $row.find('td:eq(2)').text(comunidad.estado);
                        $row.find('td:eq(3)').text(comunidad.municipio);
                        $row.find('td:eq(4)').text(comunidad.parroquia);
                        $row.find('td:eq(5)').text(comunidad.comuna);
                        $row.find('td:eq(6)').text(comunidad.cantidad_habitantes);
                        
                        // Actualizar los data attributes del botón editar
                        $btn.attr({
                            'data-nombre': comunidad.nombre,
                            'data-estado': comunidad.estado,
                            'data-municipio': comunidad.municipio,
                            'data-parroquia': comunidad.parroquia,
                            'data-comuna': comunidad.comuna,
                            'data-cantidad_habitantes': comunidad.cantidad_habitantes
                        });
                    }
                    
                    $('#modalEditarComunidad').modal('hide');
                    mostrarToast('Comunidad editada con éxito.', false);
                }
            },
            error: function(xhr) {
                mostrarToast('Error al editar la comunidad.', true);
            }
        });
    });

}); // Cierre del primer $(document).ready