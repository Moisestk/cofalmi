$(document).ready(function() {

    // --- 1. Configuración de DataTable ---
    var tabla = $('#tabla-encuestados').DataTable({
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

    // Ocultar el mensaje de "no hay datos" si la tabla ya tiene filas al cargar
    if ($('#tabla-encuestados tbody tr').length > 0 && $('#tabla-encuestados tbody tr td').length > 1) {
        $('.alert-info').hide();
    }


    // --- 2. Lógica para Crear Encuestado (Modal y AJAX) ---
    $('#formCrearEncuestado').on('submit', function(e) {
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
                    var encuestado = response.encuestado;

                    // Crear el HTML para los botones de acción
                    var botonesAccion = `
                        <div class='d-flex justify-content-center flex-wrap gap-1'>
                            <button type="button"
                                class="btn btn-primary btn-sm btn-editar-encuestado"
                                title="Editar"
                                data-bs-toggle="modal"
                                data-bs-target="#modalEditarEncuestado"
                                data-id="${encuestado.id}"
                                data-nombre="${encuestado.nombre}"
                                data-apellido="${encuestado.apellido}"
                                data-tipo_cedula="${encuestado.cedula_completa.split('-')[0]}"
                                data-cedula_numero="${encuestado.cedula_completa.split('-')[1]}"
                                data-genero="${encuestado.genero}"
                                data-telefono="${encuestado.telefono || ''}"
                                data-direccion="${encuestado.direccion || ''}"
                                data-cargo="${encuestado.cargo || ''}"
                                data-ubicacion="${encuestado.ubicacion_administrativa || ''}">
                                <i class="fa fa-edit"></i>
                            </button>
                            <a href='#' class='btn btn-danger btn-sm' title='Enviar a papelera'
                               data-bs-toggle='modal' data-bs-target='#borrarEncuestadoModal'
                               data-id='${encuestado.id}' data-nombre='${encuestado.nombre}'
                               data-apellido='${encuestado.apellido}'>
                               <i class='fa fa-trash'></i>
                            </a>
                            <a href='#' class='btn btn-info btn-sm' title='Detalles'
                               data-bs-toggle='modal' data-bs-target='#detalleModal'
                               data-nombre='${encuestado.nombre}' data-apellido='${encuestado.apellido}'
                               data-cedula='${encuestado.cedula_completa}' data-genero='${encuestado.genero}'
                               data-telefono='${encuestado.telefono || "N/A"}' data-direccion='${encuestado.direccion || "N/A"}'
                               data-cargo='${encuestado.cargo || "N/A"}' data-ubicacion='${encuestado.ubicacion_administrativa || "N/A"}'
                               data-fecha='${encuestado.fecha_registro}'>
                               <i class='fa fa-ellipsis'></i>
                            </a>
                        </div>`;
                    
                    // Añadir la nueva fila a la tabla DataTable
                    var nuevaFila = tabla.row.add([
                        tabla.rows().count() + 1,
                        encuestado.nombre,
                        encuestado.apellido,
                        encuestado.cedula_completa,
                        botonesAccion
                    ]).draw(false).node();
                    
                    $(nuevaFila).attr('id', `encuestado-row-${encuestado.id}`);
                    $(nuevaFila).find('td:eq(1)').addClass('nombre');
                    $(nuevaFila).find('td:eq(2)').addClass('apellido');
                    $(nuevaFila).find('td:eq(3)').addClass('cedula');

                    // Ocultar mensaje de tabla vacía si estaba visible
                    if ($('.alert-info').is(':visible')) {
                        $('.alert-info').hide();
                        $('#tabla-encuestados_wrapper').show();
                    }

                    $('#modalCrearEncuestado').modal('hide');
                    showToast('Encuestado añadido exitosamente.', 'success');
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
                showToast('Error al añadir encuestado. Revise el formulario.', 'danger');
            }
        });
    });


    // --- 3. Lógica para Verificación de Cédula en Tiempo Real ---
    $('#modal_cedula_numero').on('blur', function() {
        var cedulaInput = $(this);
        var numeroCedula = cedulaInput.val();
        var errorDiv = $('#cedula-error-msg');
        var submitButton = $('#formCrearEncuestado button[type="submit"]');

        if (numeroCedula.length >= 6) {
            $.ajax({
                url: '/verificar-cedula/',
                data: { 'cedula_numero': numeroCedula },
                dataType: 'json',
                success: function(response) {
                    if (response.existe) {
                        errorDiv.text('Esta cédula ya está registrada.');
                        cedulaInput.addClass('is-invalid');
                        submitButton.prop('disabled', true);
                    } else {
                        errorDiv.text('');
                        cedulaInput.removeClass('is-invalid');
                        submitButton.prop('disabled', false);
                    }
                }
            });
        } else {
            errorDiv.text('');
            cedulaInput.removeClass('is-invalid');
            submitButton.prop('disabled', false);
        }
    });


    // --- 4. Lógica para Enviar a Papelera (Eliminar) ---
    var encuestadoIdAEliminar = null;
    $('#borrarEncuestadoModal').on('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        encuestadoIdAEliminar = button.getAttribute('data-id');
        var nombre = button.getAttribute('data-nombre');
        var apellido = button.getAttribute('data-apellido');
        // Truncar nombres si son muy largos
        var nombreTruncado = nombre.length > 15 ? nombre.substring(0, 15) + '...' : nombre;
        var apellidoTruncado = apellido.length > 15 ? apellido.substring(0, 15) + '...' : apellido;
        
        $('#modal-borrar-nombre').text(nombreTruncado).attr('title', nombre);
        $('#modal-borrar-apellido').text(apellidoTruncado).attr('title', apellido);
        var form = $('#formPapeleraEncuestado');
        var actionUrl = `/encuestados/papelera/${encuestadoIdAEliminar}/`;
        form.attr('action', actionUrl);
    });

    $('#formPapeleraEncuestado').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        $.ajax({
            url: form.attr('action'),
            type: 'POST',
            data: form.serialize(),
            success: function(response) {
                if(response.success) {
                    $('#borrarEncuestadoModal').modal('hide');
                    var fila = $(`#encuestado-row-${encuestadoIdAEliminar}`);
                    tabla.row(fila).remove().draw();
                    
                    if (tabla.rows().count() === 0) {
                        $('#tabla-encuestados_wrapper').hide();
                        $('.alert-info').show();
                    }
                    showToast('Encuestado enviado a la papelera.', 'success');
                }
            },
            error: function() {
                showToast('Error al enviar a la papelera.', 'danger');
            }
        });
    });


    // --- 5. Lógica para Llenar Modal de Detalles ---
    $('#detalleModal').on('show.bs.modal', function (event) {
        var button = event.relatedTarget;
        $('#modal-nombre').text(button.getAttribute('data-nombre'));
        $('#modal-apellido').text(button.getAttribute('data-apellido'));
        $('#modal-cedula').text(button.getAttribute('data-cedula'));
        $('#modal-genero').text(button.getAttribute('data-genero'));
        $('#modal-telefono').text(button.getAttribute('data-telefono'));
        $('#modal-direccion').text(button.getAttribute('data-direccion'));
        $('#modal-cargo').text(button.getAttribute('data-cargo'));
        $('#modal-ubicacion').text(button.getAttribute('data-ubicacion'));
        $('#modal-fecha').text(button.getAttribute('data-fecha'));
    });


    // --- 6. Limpieza de Modales al Cerrar ---
    $('#modalCrearEncuestado').on('hidden.bs.modal', function() {
        var form = $('#formCrearEncuestado');
        form[0].reset();
        form.find('.is-invalid').removeClass('is-invalid');
        $('#cedula-error-msg').text('');
        $('#ajax-error-msg').addClass('d-none').html('');
        form.find('button[type="submit"]').prop('disabled', false);
    });


    // --- 7. Función de Notificaciones (Toast) ---
    function showToast(message, type = 'success') {
        let toastContainer = $('#toast-container');
        if (toastContainer.length === 0) {
            $('body').prepend('<div id="toast-container" class="position-fixed top-0 end-0 p-3" style="z-index: 1080;"></div>');
            toastContainer = $('#toast-container');
        }
        const toastId = 'toast-' + Date.now();
        const bgClass = type === 'success' ? 'text-bg-success' : 'text-bg-danger';
        const toastHtml = `
            <div id='${toastId}' class='toast align-items-center ${bgClass} border-0' role='alert' aria-live='assertive' aria-atomic='true' data-bs-delay='3500'>
              <div class='d-flex'>
                <div class='toast-body'>${message}</div>
                <button type='button' class='btn-close btn-close-white me-2 m-auto' data-bs-dismiss='toast' aria-label='Cerrar'></button>
              </div>
            </div>`;
        toastContainer.append(toastHtml);
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
    }
            // --- 8. LÓGICA PARA EDITAR ENCUESTADO ---
    $(document).on('show.bs.modal', '#modalEditarEncuestado', function(event) {
        const button = event.relatedTarget;
        const dataset = button.dataset;
        const encuestadoId = dataset.id;
        const formEditar = $('#formEditarEncuestado');

        const actionTemplate = formEditar.data('action-template');
        formEditar.attr('action', actionTemplate.replace(/0\/?$/, `${encuestadoId}/`));

        // Poblar el formulario de edición
        $('#edit_nombre').val(dataset.nombre);
        $('#edit_apellido').val(dataset.apellido);
        $('#edit_tipo_cedula').val(dataset.tipo_cedula);
        $('#edit_cedula_numero').val(dataset.cedula_numero);
        $('#edit_genero').val(dataset.genero);
        $('#edit_direccion').val(dataset.direccion);
        $('#edit_cargo').val(dataset.cargo);
        $('#edit_ubicacion_administrativa').val(dataset.ubicacion);

        const telefonoCompleto = dataset.telefono;
        const prefijos = ["0412", "0414", "0416", "0424", "0426"];
        let prefijoEncontrado = "";
        let numeroTelefono = "";

        if (telefonoCompleto) {
            for (const p of prefijos) {
                if (telefonoCompleto.startsWith(p)) {
                    prefijoEncontrado = p;
                    numeroTelefono = telefonoCompleto.substring(p.length);
                    break;
                }
            }
        }
        $('#edit_telefono_prefijo').val(prefijoEncontrado);
        $('#edit_telefono_numero').val(numeroTelefono);
    });

    $('#formEditarEncuestado').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var data = form.serialize();
        var errorContainer = $('#ajax-edit-error-msg');
        errorContainer.addClass('d-none').html('');

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            dataType: 'json',
            headers: {
                'x-requested-with': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.success) {
                    var encuestado = response.encuestado;
                    var row = $(`#encuestado-row-${encuestado.id}`);
                    
                    if (row.length) {
                        row.find('td:eq(1)').text(encuestado.nombre);
                        row.find('td:eq(2)').text(encuestado.apellido);
                        row.find('td:eq(3)').text(encuestado.cedula_completa);
                        
                        row.find('.btn-editar-encuestado').attr({
                            'data-nombre': encuestado.nombre,
                            'data-apellido': encuestado.apellido,
                            'data-tipo_cedula': encuestado.cedula_completa.split('-')[0],
                            'data-cedula_numero': encuestado.cedula_completa.split('-')[1]
                        });
                        
                        tabla.row(row).invalidate().draw(false);
                    }
                    
                    $('#modalEditarEncuestado').modal('hide');
                    showToast('Encuestado actualizado exitosamente.', 'success');
                }
            },
            error: function(xhr) {
                console.log('Error AJAX:', xhr);
                console.log('Status:', xhr.status);
                console.log('Response Text:', xhr.responseText);
                console.log('Response JSON:', xhr.responseJSON);
                
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
                showToast('Error al actualizar encuestado. Revise el formulario.', 'danger');
            }
        });
    });

    // Limpia el formulario y los errores del modal de EDITAR cuando se cierra
    $('#modalEditarEncuestado').on('hidden.bs.modal', function() {
        $('#ajax-edit-error-msg').addClass('d-none').html('');
        $('#formEditarEncuestado')[0].reset();
    });
});